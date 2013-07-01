$(document).ready(function() {
    var ctnr = $('#ctnr-data');
    var searchUserUrl = ctnr.attr('data-searchUserUrl');
    var addUserUrl = ctnr.attr('data-addUserUrl');
    var ctnrPk = ctnr.attr('data-ctnr-pk');
    var userPk = null;
    var username = null;
    // Auto complete for user search dialog.
    $('#user-searchbox').autocomplete({
        minLength: 1,
        source: searchUserUrl,
        delay: 400,
        select: function(event, ui) {
            userPk = ui.item.pk;
            username = ui.item.label;
        }
    });
    // Add user to ctnr.
    $('#add-user-ctnr').click(function(event) {
        if (username != ($('#user-searchbox').val())) {
            userPk = null;
        }
        var postData = {
            ctnr: ctnrPk,
            user: userPk,
            level: $('#add-user input[name="level"]:checked')[0].value
        };
        $.post(addUserUrl, postData, function(data) {
            if (data.error) {
                $('#add-user-errorlist').empty();
                // Put error message.
                console.log(data.error);
                var forms = document.getElementById('add-user-errorlist');
                forms.innerHTML = "<li><font color='red'>" + data.error +"</font></li>" + forms.innerHTML;
                $('#user-searchbox').val('');
                userPk = null;
            } else {
                // Append row to user table.
                if ($('.user-table tbody')[0]) {
                    insertTablefyRow(data.user, $('.user-table tbody'));
                    event.preventDefault();
                    $('#user-searchbox').val('');
                    userPk = null;
                } else {
                    document.location.reload();
                }
            }
        }, 'json');
    });
});
