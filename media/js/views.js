$(document).ready(function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var objType = metadata.attr('data-objType');
    var prettyObjType = metadata.attr('data-prettyObjType');
    var searchUrl = metadata.attr('data-searchUrl');
    var getUrl = metadata.attr('data-getUrl');
    var domainsUrl = metadata.attr('data-domainsUrl');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    make_smart_name_get_domains($('#id_fqdn, #id_target, #id_server'), true, domainsUrl);

    $('#create-obj').click(function() {
        // Show create form on clicking create button.
        slideUp($('#obj-form'));
        setTimeout(function() {
            $('#form-title').html('Creating ' + prettyObjType);
            clear_form_all(form);
        }, 150);
        $('.form-btns a.submit').text('Create ' + prettyObjType);
        slideDown($('#obj-form'));
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
            slideDown($('#obj-form'));
        }, 'json');
    });
});
