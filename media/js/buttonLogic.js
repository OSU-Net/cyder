$(document).ready( function() {
    // button behavior logic, see css
    var selectors = '.js-get-form, .js-create-object, .update, ' +
        '.cancel, .system_form, .ctnr_form';
    function buttonLogic() {
        $(selectors).addClass( 'hover' );
        if ( $(this).hasClass( 'selected' ) ) {
            $(this).removeClass( 'selected' );
        } else {
            $(selectors).removeClass( 'selected' );
            $(this).removeClass( 'hover' ).addClass( 'selected' );
        }
    }

    $( document ).on( 'click', selectors, buttonLogic );
});
