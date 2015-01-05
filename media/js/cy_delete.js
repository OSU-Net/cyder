$(document).ready( function() {
    // returns dict on completion, bool is stored in dict.last_interface
    function is_last_interface( kwargs, csrfToken ) {
        var last_interface_url = '/dhcp/interface/last_interface/';
        var postData = {
            pk: kwargs.pk,
            obj_type: kwargs.obj_type,
            csrfmiddlewaretoken: csrfToken
        };
        return $.ajax({
            type: 'POST',
            url: last_interface_url,
            data: postData,
            global: false,
            dataType: 'json',
        });
    }

    function is_interface( obj_type ) {
        return ( obj_type == 'static_interface' ||
                 obj_type == 'dynamic_interface' )
    }

    // returns a deferred object, when resolved returns a string
    function get_delete_confirm_msg( kwargs, csrfToken ) {
        var deferred = $.Deferred();
        var msg = "Are you sure you want to delete this?";
        var ret_data = {}
        if ( is_interface( kwargs.obj_type ) ) {
            $.when( is_last_interface( kwargs, csrfToken ) ).done(
                function( data ) {
                    if ( data.last_interface ) {
                        msg = ('Because this is the last interface on ' +
                               'its system, deleting this interface ' +
                              'will also delete its system. Are you ' +
                              'sure you want to continue?');
                    }
                    deferred.resolve( msg );
                });
        } else {
            if ( kwargs.obj_type == "system" ) {
                msg = "Deleting this system will also delete its" +
                    " interfaces. Are you sure you want to continue?";
            }
            deferred.resolve( msg );
        }
        return deferred;
    }

    function delete_object( btn, kwargs, csrfToken, msg ) {
        if ( confirm( msg ) ) {
            $.when( button_to_post( btn, csrfToken ) ).done( function( data ) {
                if ( data.error ) {
                    header_message( data.error );
                } else {
                    // if the object is in a table and not the last element of
                    // that table delete the row
                    if ( $( btn ).hasClass( 'table_delete' ) &&
                            $( btn ).parents( 'tbody' ).find( 'tr' ).length > 1 ) {
                        $( btn ).parents( 'tr' ).remove();
                    } else {
                        window.location.href = data.url;
                    }
                }
            });
        } else {
            return false;
        }
    }

    // handles all delete buttons
    $( document ).on( 'click', '#delete, .delete', function( e ) {
        e.preventDefault();
        var btn = this;
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        $.when( get_delete_confirm_msg( kwargs, csrfToken ) ).done( function( msg ) {
            delete_object( btn, kwargs, csrfToken, msg );
        });
    });
});
