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

    $( document ).on( 'change', "input[name='obj_type']", function() {
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

    function get_add_form( btn ) {
        var formTitle;
        var buttonLabel;
        var buttonAttrs = 'btn c ctnr-submit';
        slideUp( $('#obj-form') );
        $(document).scrollTop(0);
        $.ajax({
            type: 'GET',
            url: btn.href,
            global: false,
            dataType: 'json',
            success: function( data ) {
                var add_user_form = $('<div id="add-user-form">')
                    .append( data.add_user_form );
                if ( !data.only_user ) {
                    add_user_form.attr( 'style', 'display:none' );
                }
                setTimeout( function() {
                    $('#hidden-inner-form')
                        .empty()
                        .append( data.object_form )
                        .append( add_user_form );
                    initForms();
                }, 150 );
                $('#form-title').html( data.form_title );
                $('.form-btns .btn').not('.cancel')
                    .text( data.submit_btn_label )
                    .attr( 'class', buttonAttrs );
                $('#obj-form').slideDown();
            }
        });
    };

    $( document ).on( 'click', '#ctnr-get-add-form', function( e ) {
        e.preventDefault();
        get_add_form( this );
    });


    // Add object to ctnr.
    $( document ).on( 'click', '.ctnr-submit', function() {
        var fields = $('#obj-form').find( ':input' ).serializeArray();
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
