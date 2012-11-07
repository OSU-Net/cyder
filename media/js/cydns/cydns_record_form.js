$(document).ready(function(){
    var cydns = $('#cydns-record');
    var recordType = cydns.attr('data-recordType');
    var searchUrl = cydns.attr('data-searchUrl');
    var updateUrl = cydns.attr('data-updateUrl');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    var inputs = $('input');
    inputs.length;
    for (var x = 0; x < inputs.length; x++) {
        if(inputs[x].id === 'id_fqdn' || inputs[x].id === 'id_target' || inputs[x].id === 'id_server') {
            make_smart_name_get_domains(inputs[x], true);
            $(inputs[x]).css('width', '400px');
        }
    }

    // Record-search dialogs to find records to update.
    $('#record-search').click(function() {
        $('#search-dialog').dialog({
            title: 'Search for a ' + recordType + ' record to update.',
            autoShow: false,
            minWidth: 520,
            buttons: {
                'Edit Record': function() {
                    // To edit. get pk (from when selected from the
                    // dropdown, and request object's form to replace current one.
                    $.get(updateUrl, {'record_type': recordType,
                                      'record_pk': $('#search-dialog').attr('stage_pk')},
                          function(data) {
                              $('#record-form-title').html('Update');
                              $('.inner-form').empty().append(data);
                              $('#cydns-record-form').show();
                              $('#record-searchbox').attr('value', '');
                          });
                    $(this).dialog('close');
                },
                'Cancel': function() {
                    $('#search-dialog').attr('stage_pk', ''),
                    $(this).dialog('close');
                }
            }
        }).show();
    });
    $('#record-search-soa').click(function() {
        $('#search-soa-dialog').dialog({
            title: 'Search for a BIND file',
            autoShow: true,
            minWidth: 520,
            buttons: {
                'View ZONE file': function() {
                    // To edit. get pk (from when selected from the
                    // dropdown, and request object's form to replace current one.
                    window.open('/cydns/bind/build_debug/'+ $('#search-soa-dialog').attr('stage_soa_pk') + '/');
                    $(this).dialog('close');
                },
                'Cancel': function() {
                    $('#search-dialog').attr('stage_soa_pk', ''),
                    $(this).dialog('close');
                }
            }
        }).show();
    });

    // Auto complete for search dialogs.
    $('#record-searchbox').autocomplete({
        // Bind autocomplete to the search field for the specifc record type.
        minLength: 2,
        source: searchUrl + '?record_type=' + recordType,
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            $('#search-dialog').attr('stage_pk', ui.item.pk);
        }
    });
    $('#soa-searchbox').autocomplete({
        minLength: 2,
        source: searchUrl + '?record_type=SOA',
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            $('#search-soa-dialog').attr('stage_soa_pk', ui.item.pk);
        }
    });

    // Show create form on clicking create button.
    $('#record-create').click(function() {
        $('#record-form-title').html('Create');
        clear_form_all($('#cydns-record-form form')[0]);
        $('#cydns-record-form').show();
    });
});
