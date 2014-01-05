$(document).ready(function() {
    var formBlock = $('#perm-hidden');
    $('#id_users').tagsInput({'defaultText': 'add a user'});
    $('#clone-perms-btn, #clone-perms-cancel').click(function(e) {
        formBlock.slideToggle("slow", function() {
        });
    });
    $('#clone-perms-submit').click(function(e) {
        e.preventDefault();
        postData = {
            users: ($('#clone-perms-form').find(':input')[0].value),
        };
        var new_users;
        $.post('/core/user/clone_perms_check/', postData, function(data) {
            if (data.confirm_str) {
                if(!confirm((data.confirm_str))) {
                    jQuery.each(data.users, function(i, user) {
                        $('#id_users').removeTag(user);
                    });
                }
            }
        }, 'json');
        var url = $('#clone-perms-form').attr('action');
        return ajax_form_submit(url, $('#clone-perms-form'));
    });
});
