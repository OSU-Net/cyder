$(document).ready(function() {

    $('#id_users').tagsInput( {
        'defaultText': 'add a user',
        'autocomplete_url': '/core/user/search'
    } );

    $('#clone-perms-btn, #clone-perms-cancel').click( function ( e ) {
        $('#permissions-form-hidden').slideToggle( "slow", function() {
        } );
    } );

    $('#clone-perms-submit').click( function( e ) {
        e.preventDefault();
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        postData = {
            users: $('#clone-perms-form').find( ':input' )[0].value,
            csrfmiddlewaretoken: csrfToken,
        };
        $.post( '/core/user/clone_perms_check/', postData, function( data ) {
            if ( data.confirm_str ) {
                var confirmation = confirm( data.confirm_str );
                if ( !confirmation ) {
                    jQuery.each( data.users, function( i, user ) {
                        $('#id_users').removeTag( user );
                    } );
                }
            }
            var url = $('#clone-perms-form').attr( 'action' );
            var fields = $('#clone-perms-form')
                .find( ':input' ).serializeArray();

            $.when( ajax_form_submit( url, fields, csrfToken ) )
                    .done( function() {
                location.reload();
            });
        }, 'json' );
    });
});
