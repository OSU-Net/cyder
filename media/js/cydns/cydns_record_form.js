$(document).ready(function() {
    var cydns = $('#cydns-record');
    var form = $('#cydns-record-form form')[0];
    var recordType = cydns.attr('data-recordType');
    var prettyRecordType = cydns.attr('data-prettyRecordType');
    var searchUrl = cydns.attr('data-searchUrl');
    var getUrl = cydns.attr('data-getUrl');
    var domainsUrl = cydns.attr('data-domainsUrl');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    make_smart_name_get_domains($('#id_fqdn, #id_target, #id_server'), true, domainsUrl);

    // Auto complete for search dialogs.
    $('#record-searchbox').autocomplete({
        // Bind autocomplete to the search field for the specifc record type.
        minLength: 1,
        source: searchUrl + '?record_type=' + recordType,
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            $('#search-dialog').attr('pk', ui.item.pk);
        }
    });
    $('#soa-searchbox').autocomplete({
        minLength: 1,
        source: searchUrl + '?record_type=SOA',
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            $('#search-soa-dialog').attr('pk', ui.item.pk);
        }
    });

    // Show create form on clicking create button.
    $('#record-create').click(function() {
        $('#record-form-title').html('Creating a ' + prettyRecordType);
        $('.delete').hide();

        clear_form_all(form);
        form.action = '?action=create';
        $('#cydns-record-form').slideDown();
    });

    $('.update').click(function() {
        $.get(getUrl, {'record_type': recordType, 'pk': $(this).attr('data-pk')}, function(data) {
            $('#record-form-title').html('Updating a ' + prettyRecordType);
            $('.inner-form').empty().append(data.form);
            $('.delete').show();
            initForms();
            form.action = '?action=update&pk=' + data.pk;
            $('#cydns-record-form').slideDown();
        }, 'json');
    });
});
