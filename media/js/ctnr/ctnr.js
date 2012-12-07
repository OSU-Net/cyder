$(document).ready(function() {
    var ctnr = $('#ctnr-data');
    var searchUserUrl = ctnr.attr('data-searchUserUrl');
    var ctnrName = ctnr.attr('data-ctnrName');

    // Record-search dialogs to find records to update.
    $('#add-user-ctnr').click(function() {
        $('#add-user-dialog').dialog({
            title: 'Search for a user to add to container ' + ctnrName + '.',
            autoShow: false,
            minWidth: 520,
            buttons: {
                'Cancel': function() {
                    $(this).attr('pk', ''),
                    $(this).dialog('close');
                },
                'Add User': function() {
                    // Get pk from dropdown and send request to add user.
                    var pk = $(this).attr('pk');
                    $.post('', {'pk': pk}, function(data) {
                        $('#record-searchbox').attr('value', '');
                    });
                    $(this).attr('pk', ''),
                    $(this).dialog('close');
                }
            }
        }).show();
    });

    // Auto complete for user search dialog.
    $('#user-searchbox').autocomplete({
        minLength: 1,
        source: searchUserUrl,
        select: function( event, ui ) {
            $('#add-user-dialog').attr('pk', ui.item.pk);
        }
    });
});
