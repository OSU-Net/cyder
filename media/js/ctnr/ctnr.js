$(document).ready(function() {
    var objPk = null;
    var confirmation = false;
    var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );

    $( document ).on( 'click', '.minus, .plus', function( e ) {
        e.preventDefault();
        var ctnrName = $('#ctnr-data').attr( 'data-ctnrName' );
        var url = $(this).attr( 'href' );
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        postData = {
            action: 'user_level',
            csrfmiddlewaretoken: csrfToken,
            lvl: kwargs.lvl,
            obj_type: kwargs.obj_type,
            pk: kwargs.pk,
        };
        $.ajax({
            type: 'POST',
            url: url,
            data: postData,
            dataType: 'json',
            global: false,
            success: handle_error_message
        });
    });

    $( document ).on( 'click', '.remove.user, .remove.object', function( e ) {
        e.preventDefault();
        var ctnrName = $('#ctnr-data').attr( 'data-ctnrName' );
        var url = $(this).attr( 'href' );
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        var msg;
        var args = [];
        args.push( kwargs.obj_type );
        if ( kwargs.name ) {
            args.push( kwargs.name );
        }
        args.push( ctnrName );
        var msg = getMsg( 'CtnrDetail', 'Confirmation', args );

        if ( confirm( msg ) ) {
            postData = {
                action: 'obj_remove',
                csrfmiddlewaretoken: csrfToken,
                obj_type: kwargs.obj_type,
                pk: kwargs.pk,
            };
            $.ajax({
                type: 'POST',
                url: url,
                data: postData,
                dataType: 'json',
                global: false,
                success: handle_error_message
            });
        }
        return false;
    });

    function handle_error_message ( data ) {
        if ( data.error ) {
            header_message( data.error );
        } else {
            location.reload();
        }
    }

    function change_ctnr_form ( value ) {
        if ( value == 'user' ) {
            $('#add-user-form').slideDown();
        } else {
            $('#add-user-form').slideUp();
        }
        $('label[for="object-searchbox"]').text( value + '*:' );
        search( $('#ctnr-data').attr( 'data-search' + value + 'Url' ) );

    };

    $( document ).on( 'change', "input[name='obj_type']", function() {
        change_ctnr_form( this.value );
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
        $.ajax({
            type: 'POST',
            url: addObjectUrl,
            data: postData,
            dataType: 'json',
            success: handle_add_object_errors
        });
    });

    function handle_add_object_errors( data ) {
        if ( data.acknowledge ) {
            if ( confirm( data.acknowledge ) ) {
                confirmation = true;
                $('.ctnr-submit').click();
            }
        }
        if ( data.error ) {
            $('.error').empty();
            $('#add-object-errorlist').empty();
            var forms = $('#add-object-errorlist');
            forms.append( '<li class="error">' + data.error +'</li>' );
        }
        if ( data.success ) {
            document.location.reload();
        }
    }

});
