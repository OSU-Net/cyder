$(document).ready(function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var objType = metadata.attr('data-objType');
    var prettyObjType = metadata.attr('data-prettyObjType');
    var searchUrl = metadata.attr('data-searchUrl');
    var getUrl = metadata.attr('data-getUrl');
    var domainsUrl = metadata.attr('data-domainsUrl');
    var objPk = metadata.attr('data-objPk');
    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    if (domainsUrl) {
        make_smart_name_get_domains($('#id_fqdn, #id_target, #id_server'), true, domainsUrl);
    }

    $('.create-obj').click(function() {
        // Show create form on clicking create button.
        if(this.hasAttribute('data-objType')) {
            var $createBtn = $(this);
            var formPrettyObjType = $createBtn.attr('data-prettyobjtype');
            var formObjType = $createBtn.attr('data-objType');
            var formGetUrl = $createBtn.attr('data-getUrl');
            var formObjName = $createBtn.attr('data-objName');
            slideUp($('#obj-form'));
            $.get(formGetUrl,
                {
                    'object_type': formObjType,
                    'related_type': objType,
                    'related_pk': objPk
                },
                function(data) {
                    setTimeout(function() {
                        $('#form-title').html('Creating ' + FormPrettyObjType + ' for ' + formObjName);
                        $('.inner-form').empty().append(data.form);
                        initForms();
                    }, 150);
                    $('.form-btns a.submit').text('Create ' + formPrettyObjType);
                    $('#obj-form').slideDown();
                }, 'json');
        } else {
            setTimeout(function() {
                $('#form-title').html('Creating ' + prettyObjType);
                clear_form_all(form);
            }, 150);
            $('.form-btns a.submit').text('Create ' + prettyObjType);
            $('#obj-form').slideToggle();
        }
    });

    $('.update').click(function(e) {
        // Show update form on clicking update icon.
        slideUp($('#obj-form'));

        e.preventDefault();
        form.action = this.href;
        $.get(getUrl, {'object_type': objType, 'pk': $(this).attr('data-pk')}, function(data) {
            setTimeout(function() {
                $('#form-title').html('Updating ' + prettyObjType);
                $('.inner-form').empty().append(data.form);
                initForms();
            }, 150);
            $('.form-btns a.submit').text('Update ' + prettyObjType);
            $('#obj-form').slideDown();
        }, 'json');
    });
});
