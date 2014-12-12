$(document).ready( function() {
    // toggles the settings menu in mobile view
    $('#settings-btn').click( function() {
        $('.settings-menu').slideToggle();
        $('#settings-btn').toggleClass( 'selected' );
    });

    // toggles the sidebar in mobile view
    $('#menu-btn').click( function() {
        $('#menu-btn').toggleClass( 'selected' );
        $('#sidebar_div').toggleClass( 'displayed' );
    });
});
