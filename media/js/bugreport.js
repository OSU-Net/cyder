$(document).ready( function() {
    $( document ).on( 'submit', '#js-bugReport', function( e ) {
        e.preventDefault();
        url = $( location ).attr( 'href' );
        var csrfToken = $('#view-metadata').attr('data-csrfToken');
        var fields = $('#js-bugReport').find( ':input' ).serializeArray();
        $.when( ajax_form_submit( url, fields, csrfToken ) )
                .done( function( data ) {
            alert('Your bug report was sent successfully. ' +
                  'Thank you for your input!');
            window.location.href = '/';
        });
    });
});
