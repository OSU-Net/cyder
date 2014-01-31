$(document).ready(function() {
    var formBlock = $('#perm-hidden');
    var csrfToken = $('#view-metadata').attr('data-csrfToken');
    $('#id_users').tagsInput({
        'defaultText': 'add a user',
        'autocomplete_url': '/core/user/search'});
    $('#clone-perms-btn, #clone-perms-cancel').click(function(e) {
        formBlock.slideToggle("slow", function() {
        });
    });
    $('#clone-perms-submit').click(function(e) {
        e.preventDefault();
        postData = {
            users: ($('#clone-perms-form').find(':input')[0].value),
            csrfmiddlewaretoken: csrfToken,
        };
        $.post('/core/user/clone_perms_check/', postData, function(data) {
            if (data.confirm_str) {
                var confirmation = confirm(data.confirm_str);
                if (!confirmation) {
                    jQuery.each(data.users, function(i, user) {
                        $('#id_users').removeTag(user);
                    });
                };
            };
            var url = $('#clone-perms-form').attr('action');
            clone_perms_data = ajax_form_submit(
                url, $('#clone-perms-form'), csrfToken);
            if (clone_perms_data.success) {
                location.reload();
            };
        }, 'json');
    });
});
