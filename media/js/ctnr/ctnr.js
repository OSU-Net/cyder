$(document).ready(function() {
    var ctnr = $('#ctnr-data');
    var searchUserUrl = ctnr.attr('data-searchUserUrl');
    var addUserUrl = ctnr.attr('data-addUserUrl');
    var ctnrPk = ctnr.attr('data-ctnr-pk');
    var userPk = null;

    // Auto complete for user search dialog.
    $('#user-searchbox').autocomplete({
        minLength: 1,
        source: searchUserUrl,
        select: function(event, ui) {
            userPk = ui.item.pk;
        }
    });

    // Add user to ctnr.
    $('#add-user-ctnr').click(function() {
        var postData = {
            ctnr: ctnrPk,
            user: userPk,
            level: $('#add-user input[name="level"]:checked')[0].value
        };
        $.post(addUserUrl, postData, function(data) {
            console.log(data.error);
        }, 'json');
    });
});
