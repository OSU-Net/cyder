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
    var csrfToken = metadata.attr('data-csrfToken');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    if (domainsUrl) {
        make_smart_name_get_domains(
            $('#id_fqdn, #id_target, #id_server'), true, domainsUrl);
    }
    $('#settings-btn').click( function(e) {
        $('.settings-menu').slideToggle();
        $('#settings-btn').toggleClass('selected');
    });
    $('#menu-btn').click( function(e) {
        $('#menu-btn').toggleClass('selected');
        $('#sidebar_div').toggleClass('displayed');
    });
    $('.nav-item.parent').click( function(e) {
        e.preventDefault();
        var parentsChild = ('#' + this.id + '-children');
        if ($(parentsChild).css('display') != 'none') {
            $(parentsChild).slideUp('slow');
        } else {
            var children = [
                '#dns-sidebar-children',
                '#dhcp-sidebar-children',
                '#core-sidebar-children'];
            $.each(children, function(i, child) {
                if (parentsChild != child) {
                    if ($(child).css('display') != 'none') {
                        $(child).slideToggle('slow');
                    };
                };
            });
            $(parentsChild).slideToggle('slow');
        };
    });

    $('#delete, .delete').click( function(e) {
        e.preventDefault();
        if ($(this).attr('id') == 'delete'
                || $(this).attr('class') == 'delete') {
            var msg = "Are you sure you want to delete this?";
            if (objType == 'system') {
                msg = "Deleting this system will also delete its"
                    + " interfaces. Are you sure you want to continue?";
            }
            if (!confirm(msg)) {
                return false;
            }
        }
        var url = $(this).attr('href');
        var postData = JSON.parse($(this).attr('data-kwargs'));
        var postForm = $('<form style="display: none" action="' + url
            + '" method="post"></form>');
        $.each(postData, function(key, value) {
            postForm.append($('<input>').attr(
                {type: 'text', name: key, value: value}));
        });
        postForm.append($('<input>').attr(
            {type: 'hidden', name: 'csrfmiddlewaretoken', value: csrfToken}));
        $('.content').append(postForm);
        $(postForm).submit();
    });

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

    $('#action-bar').find('a').each(function() {
        $('#action-bar').find('a').addClass('hover');
        $(this).click(function(e) {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
            } else {
                $('#action-bar').find('a').removeClass('selected');
                $(this).removeClass('hover').addClass('selected');
            };
        });
    });

    $('.create-obj').click(function(e) {
        // Show create form on clicking create button.
        e.preventDefault();
        slideUp($('#obj-form'));
        if ($(this).hasClass('selected')) {
            form.action = this.href;
            if(this.hasAttribute('data-objType')) {
                var $createBtn = $(this);
                var formPrettyObjType = $createBtn.attr('data-prettyobjtype');
                var formObjType = $createBtn.attr('data-objType');
                $('#obj-form form').attr('objType', formObjType);
                var formGetUrl = $createBtn.attr('data-getUrl');
                var data_to_post = $createBtn.attr('data-kwargs');
                var formTitle = 'Creating ' + formPrettyObjType;

                $.get(formGetUrl,
                    {
                        'obj_type': formObjType,
                        'related_type': objType,
                        'related_pk': objPk,
                        'data': data_to_post
                    },
                    function(data) {
                        setTimeout(function() {
                            $('#form-title').html(formTitle);
                            data.form.action = $createBtn.attr('href');
                            $('.inner-form').empty().append(data.form);
                            initForms();
                        }, 150);
                        $('#obj-form form')[0].action = $createBtn.attr('href');
                        $('.form-btns a.submit').text(
                            'Create ' + formPrettyObjType);
                        $('.form-btns a.submit').attr('class', 'btn c');
                        $('#obj-form').slideToggle();
                    }, 'json');
            } else {
                $('#obj-form form').attr('objType', objType);
                setTimeout(function() {
                    $('#form-title').html('Creating ' + prettyObjType);

                    if(defaults) {
                        $('#hidden-inner-form').empty().html(defaults);
                    } else {
                        clear_form_all(form);
                    };
                }, 150);
                $('.form-btns a.submit').text('Create ' + prettyObjType);

                $('.form-btns a.submit').attr('class', 'btn c');
                $('#obj-form').slideToggle();
            }
            $('.form').append($('<input>',
                              {type: 'hidden', name: 'csrfmiddlewaretoken',
                               value: csrfToken}));
        };
    });

    $('.update').click(function(e) {
        // Show update form on clicking update icon.
        slideUp($('#obj-form'));
        e.preventDefault();
        if ($(this).hasClass('selected') ||
                $(this).parents().attr('class') == 'actions_column') {
            form.action = this.href;
            var formObjName = $(this).attr('data-objName') || objName;
            var formObjType = $(this).attr('data-objType');
            $('#obj-form form').attr('objType', formObjType);
            var formPrettyObjType = $(this).attr('data-prettyObjType');
            var formTitle = 'Updating ' + formPrettyObjType + ' ' + formObjName;

            $.get($(this).attr('data-getUrl') || getUrl,
                    {'obj_type': formObjType, 'pk': $(this).attr('data-pk')},
                    function(data) {
                setTimeout(function() {
                    $('#form-title').html(formTitle);
                    $('#hidden-inner-form').empty().append(data.form);
                    initForms();
                }, 150);
                $('.form-btns a.submit').text('Update ' + formPrettyObjType);

                $('.form-btns a.submit').attr('class', 'btn c');
                $('#obj-form').slideDown();
            }, 'json');

            $('.form').append($('<input>', {type: 'hidden',
                name: 'csrfmiddlewaretoken', value: csrfToken}));
        };
    });

    $('#obj-form form').live('submit', function(event) {
        var url = $('#obj-form form')[0].action;
        event.preventDefault();
        var data = ajax_form_submit(url, $('#obj-form'), csrfToken);
        if (!data.errors) {
            location.reload();
        };
    });
});


function ajax_form_submit(url, form, csrfToken) {
    $.ajaxSetup({async:false});
    jQuery.ajaxSettings.traditional = true;
    var fields = form.find(':input').serializeArray();
    var postData = {}
    jQuery.each(fields, function (i, field) {
        if (i > 0 && fields[i-1].name == field.name) {
            postData[field.name].push(field.value);
        } else {
            postData[field.name] = [field.value];
        };
    });
    postData['csrfmiddlewaretoken'] = csrfToken;
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
