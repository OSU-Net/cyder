$(document).ready(function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var hidden_inner_form = document.getElementById('hidden-inner-form');
    if(hidden_inner_form) {
        var defaults = hidden_inner_form.innerHTML;
    };
    var objType = metadata.attr('data-objType');
    var objName = metadata.attr('data-objName');
    var prettyObjType = metadata.attr('data-prettyObjType');
    var searchUrl = metadata.attr('data-searchUrl');
    var getUrl = metadata.attr('data-getUrl');
    var domainsUrl = metadata.attr('data-domainsUrl');
    var objPk = metadata.attr('data-objPk');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    if (domainsUrl) {
        make_smart_name_get_domains($('#id_fqdn, #id_target, #id_server'), true, domainsUrl);
    }

    $('#id_attribute').live('focus', function() {
        $('#id_attribute').autocomplete({
            minLength: 1,
            source: function(request, response) {
                $.ajax({
                    url: '/eav/search',
                    dataType: 'json',
                    data: {
                        term: request.term,
                        attribute_type: $('#id_attribute_type').val()
                    },
                    success: response
                })
            },
            delay: 400,
            select: function(event, ui) {
                attributeName = ui.item.label
            }
        });
    });

	$('#id_attribute_type').live('change', function() {
		$('#id_attribute').val('');
	});

    $('.create-obj').click(function(e) {
        // Show create form on clicking create button.
        e.preventDefault();
        slideUp($('#obj-form'));
        form.action = this.href;
        if(this.hasAttribute('data-objType')) {
            var $createBtn = $(this);
            var formPrettyObjType = $createBtn.attr('data-prettyobjtype');
            var formObjType = $createBtn.attr('data-objType');
            var formGetUrl = $createBtn.attr('data-getUrl');
            var formObjName = $createBtn.attr('data-objName');
            var data_to_post = $createBtn.attr('data-kwargs');
            $.get(formGetUrl,
                {
                    'object_type': formObjType,
                    'related_type': objType,
                    'related_pk': objPk,
                    'data': data_to_post
                },
                function(data) {
                    setTimeout(function() {
                        if(formObjName) {
                            $('#form-title').html('Creating ' + formPrettyObjType + ' for ' + formObjName);
                        } else {
                            $('#form-title').html('Creating ' + formPrettyObjType);
                        }
                        data.form.action = $createBtn.attr('href');
                        $('.inner-form').empty().append(data.form);
                        initForms();
                    }, 150);
                    $('#obj-form form')[0].action = $createBtn.attr('href');
                    $('.form-btns a.submit').text('Create ' + formPrettyObjType);
                    // Adjust this if statement to submit forms with ajax
                    if (formObjType.indexOf('av') >= 0) {
                        $('.form-btns a.submit').attr('class', 'btn c');
                    };
                    $('#obj-form').slideToggle();
                }, 'json');
        } else {
            setTimeout(function() {
                $('#form-title').html('Creating ' + prettyObjType);

                if(defaults) {
                    $('#hidden-inner-form').empty().html(defaults);
                } else {
                    clear_form_all(form);
                };
            }, 150);
            $('.form-btns a.submit').text('Create ' + prettyObjType);

            // Adjust this if statement to submit forms with ajax
            if (objType.indexOf('av') >= 0) {
                $('.form-btns a.submit').attr('class', 'btn c');
            };
            $('#obj-form').slideToggle();
        }
    });

    $('.update').click(function(e) {
        // Show update form on clicking update icon.
        slideUp($('#obj-form'));

        e.preventDefault();
        form.action = this.href;
        var extra_title = ''
        if(this.href.indexOf(document.location) == -1) {
            extra_title = ' for ' + objName;
        };
        var object_type = $(this).attr('data-object_type') || objType;
        var pretty_obj_type = $(this).attr('data-prettyObjType');
        $.get($(this).attr('data-getUrl') || getUrl, {'object_type': object_type,
                       'pk': $(this).attr('data-pk')}, function(data) {
            setTimeout(function() {
                if (objType.indexOf('interface') != -1 && data.form.indexOf('title=') != -1) {
                    extra_title = ' for ' + data.form.split('title=')[1].split('/')[0].replace(/"/g, "");
                };
                $('#form-title').html('Updating ' + pretty_obj_type + extra_title);
                $('#hidden-inner-form').empty().append(data.form);
                initForms();
            }, 150);
            $('.form-btns a.submit').text('Update ' + pretty_obj_type);

            // Adjust this if statement to submit forms with ajax
            if (object_type.indexOf('av') >= 0) {
                $('.form-btns a.submit').attr('class', 'btn c');
            };
            $('#obj-form').slideDown();
        }, 'json');
    });


    $('#obj-form').live('submit', function(event) {
        var url = $('#obj-form form')[0].action;
        if (url.indexOf('av') >=0) {
            event.preventDefault();
            var data = ajax_form_submit(url, $('#obj-form'));
            if (!data.errors) {
                location.reload();
            };
        };
    });
});


function ajax_form_submit(url, form) {
    $.ajaxSetup({async:false});
    var fields = form.find(':input').serializeArray();
    var postData = {}
    jQuery.each(fields, function (i, field) {
        postData[field.name] = field.value;
    });
    var ret_data = null;
    $.post(url, postData, function(data) {
        ret_data = data;
        if (data.errors) {
            if ($('#hidden-inner-form').find('#error').length) {
                $('#hidden-inner-form').find('#error').remove();
            };
            jQuery.each(fields, function (i, field) {
                if (data.errors[field.name]) {
                    $('#id_' + field.name).after(
                        '<p id="error"><font color="red">'
                        + data.errors[field.name] + '</font></p>');
                };
            });
            if (data.errors['__all__']) {
                $('#hidden-inner-form').find('p:first').before(
                    '<p id="error"><font color="red">'
                    + data.errors['__all__'] + '</font></p>');
            };
        };
    }, 'json');
    return ret_data;
};
