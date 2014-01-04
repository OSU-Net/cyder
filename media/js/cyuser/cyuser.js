$(document).ready(function() {
    var formBlock = $('#perm-hidden');
    $('#user-perms-btn, #clone-perms-cancel').click(function(e) {
        formBlock.slideToggle("slow", function() {
        });
    });
});
