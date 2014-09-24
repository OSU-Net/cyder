$(document).ready(function() {
    var objPk = null;
    var confirmation = false;
    var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );

    $('.minus, .plus, .remove.user, .remove.object').click( function( e ) {
        e.preventDefault();
        var ctnrName = $('#ctnr-data').attr( 'data-ctnrName' );
        var url = $(this).attr( 'href' );
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        var lvl;
        var action = 'user_level';
        var acknowledge = true;
        if ( kwargs.lvl ) {
            lvl = kwargs.lvl;
        } else {
            action = 'obj_remove';
            if ( kwargs.name ) {
                acknowledge = confirm(
                    "Are you sure you want to remove " + kwargs.obj_type +
                    ", " + kwargs.name + ", from " + ctnrName + "?");
            } else {
                acknowledge = confirm(
                    "Are you sure you want to remove this " +
                    kwargs.obj_type + " from " + ctnrName + "?");
            }
        }

        if ( acknowledge ) {
            postData = {
                action: action,
                csrfmiddlewaretoken: csrfToken,
                lvl: lvl,
                obj_type: kwargs.obj_type,
                pk: kwargs.pk,
            };

            $.post( url, postData, function( data ) {
                if ( data.error ) {
                    if ( $('.container.message').find( '.messages' ).length ) {
                        $('.container.message').find( '.messages' ).remove();
                    }
                    $('.container.message').append(
                        '<ul class="messages"><li class="error">' +
                        data.error + '</li></ul>');
                } else {
                    location.reload();
                }
            }, 'json' );
        }
        return false;
    });

    function changeCtnrForm ( value ) {
        if ( value == 'user' ) {
            $('#add-user-form').slideDown();
        } else {
            $('#add-user-form').slideUp();
        }
        $('label[for="object-searchbox"]').text( value + '*:' );
        search( $('#ctnr-data').attr( 'data-search' + value + 'Url' ) );

    };

    jQuery.each( $("input[name='obj_type']:checked"), function() {
        changeCtnrForm( this.value );
    });

    $("input[name='obj_type']").change( function() {
        changeCtnrForm( this.value );
    });

    // Auto complete for object search dialog.
    function search( searchUrl ) {
        $('#object-searchbox').autocomplete({
            minLength: 1,
            source: searchUrl,
            delay: 400,
            select: function( event, ui ) {
                objPk = ui.item.pk;
            }
        });
    }

    // Add object to ctnr.
    $( document ).on( 'submit', '#obj-form form', function( event ) {
        var fields = $(this).find( ':input' ).serializeArray();
        var postData = {};
        var addObjectUrl = $('#ctnr-data').attr( 'data-addObjectUrl' );
        jQuery.each( fields, function ( i, field ) {
            postData[field.name] = field.value;
        });
        postData.obj_pk = objPk;
        postData.csrfmiddlewaretoken = csrfToken;
        postData.confirmation = confirmation;
        confirmation = false;
        $.post( addObjectUrl, postData, function( data ) {
            if ( data.acknowledge ) {
                if ( confirm( data.acknowledge ) ) {
                    confirmation = true;
                    $('#add-object-ctnr').click();
                    data.removeClass( "error" );
                }
            }
            if ( data.error ) {
                $('.error').empty();
                $('#add-object-errorlist').empty();
                var forms = $('#add-object-errorlist');
                forms.append( '<li><font color="red">' + data.error +'</font></li>' );
            }
            if ( data.success ) {
                $('.error').empty();
                document.location.reload();
            }
        }, 'json' );
    });

});
