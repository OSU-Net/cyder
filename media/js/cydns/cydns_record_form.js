$(document).ready(function(){
    var recordType = $('#record-type').attr('data-recordType');

    // Bind smart names.
    // Look for inputs that have id = 'id_fqdn' | 'id_target' | server . Make these smart names.
    var inputs = $('input');
    inputs.length;
    for (var x = 0; x < inputs.length; x++){
        if(inputs[x].id === 'id_fqdn' || inputs[x].id === 'id_target' || inputs[x].id === 'id_server'){
            make_smart_name_get_domains(inputs[x], true)
            $(inputs[x]).css('width', '400px');
        }
    }

    // Bind record search box.
    // We also need bind an auto complete to the search field for this specifc record type.
    $( "#record_search" ).autocomplete({
        minLength: 2,
        source:'/cydns/record/search/?record_type=' + recordType,
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            $('#search-dialog').attr('stage_pk', ui.item.pk);
        }
    });

    // Bind SOA search box.
    // We also need bind an auto complete to the search field for this specifc record type.
    $( "#soa_search" ).autocomplete({
        minLength: 2,
        source:'/cydns/record/search/?record_type=SOA',
        select: function( event, ui ) {
            // Save the selected pk so we can use it if the user decides to edit the record.
            console.log('Using: '+ui.item.pk);
            $('#search-soa-dialog').attr('stage_soa_pk', ui.item.pk);
        }
    });

    // Set up search
    $('#launch-search').click(function(){
    var s_dialog = $( "#search-dialog" ).dialog({
                title: 'Search ' + recordType + ' records',
                autoShow: false,
                minWidth: 520,
                buttons: {
                    "Edit Record": function() {
                        //$( this ).dialog( "close" );
                        // Ok, they want to edit the record. Get the saved pk (happened when the user 'selected' from the
                        // drop down, and request that objects form and replace the current form.
                        $.get('/cydns/record/update/',
                            {
                                'record_type': recordType,
                                'record_pk': $('#search-dialog').attr('stage_pk'),
                            },
                            function (data) {
                                $('#current_form_data').empty();
                                $('#current_form_data').append(data);
                                $('#record_search').attr('value',''); // Clear the users selection.
                                fix_css();
                                // Notice how we don't call bind_smart_names here. We don't want the autocomplete to get in the way
                                // It's likely that they are just making a small change.
                            });
                        $(this).dialog("close");
                    },
                    cancel: function() {
                        $('#search-dialog').attr('stage_pk', ''), // we don't want this anymore.
                        $(this).dialog("close");
                    }
                }
            });
        s_dialog.show();
    });
    $('#launch-soa-search').click(function(){
        var soa_dialog = $( "#search-soa-dialog" ).dialog({
                    title: 'Search for a BIND file',  // Click the selected record
                    autoShow: true,
                    minWidth: 520,
                    buttons: {
                        "View ZONE file": function() {
                            //$( this ).dialog( "close" );
                            // Ok, they want to edit the record. Get the saved pk (happened when the user 'selected' from the
                            // drop down, and request that objects form and replace the current form.
                            window.open('/cydns/bind/build_debug/'+$('#search-soa-dialog').attr('stage_soa_pk')+'/');
                            $(this).dialog("close");
                        },
                        cancel: function() {
                            $('#search-dialog').attr('stage_soa_pk', ''), // we don't want this anymore.
                            $(this).dialog("close");
                        }
                    }
                });
        soa_dialog.show();
    });
});
