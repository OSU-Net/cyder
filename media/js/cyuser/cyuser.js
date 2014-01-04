$(document).ready(function() {
    var formBlock = $('#perm-hidden');
    $('#id_users').tagsInput({'defaultText': 'add a user'});
    $('#user-perms-btn, #clone-perms-cancel').click(function(e) {
        formBlock.slideToggle("slow", function() {
        });
    });
});
