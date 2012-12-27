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

    // Show create form on clicking create button.
    $('#create-obj').click(function() {
        $('#form-title').html('Creating a ' + prettyObjType);

        clear_form_all(form);
        $('#obj-form').slideDown();
    });

    $('.update').click(function(e) {
        e.preventDefault();
        form.action = this.href;
        $.get(getUrl, {'object_type': objType, 'pk': $(this).attr('data-pk')}, function(data) {
            $('#form-title').html('Updating a ' + prettyObjType);
            $('.inner-form').empty().append(data.form);
            initForms();
            $('#obj-form').slideDown();
        }, 'json');
    });
});
