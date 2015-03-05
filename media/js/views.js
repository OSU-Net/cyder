$(document).ready( function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var domainsUrl = metadata.attr( 'data-domainsUrl' );

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    $( document ).on( 'click', '#id_fqdn, #id_target, #id_server', function() {
        if ( domainsUrl ) {
            make_smart_name_get_domains(
                $('#id_fqdn, #id_target, #id_server'), true, domainsUrl );
        }
    });

    // displays the loading gif on ajax event
    $(document).ajaxStart( function() {
        $('#busy-spinner').stop().fadeIn( 160 );
    }).ajaxStop( function() {
        $('#busy-spinner').stop().fadeOut( 160 );
    });

    // sidebar animation logic
    $('.nav-item.parent').click( function( e ) {
        e.preventDefault();
        var parentsChild = ( '#' + this.id + '-children' );
        $('#dns-sidebar-children, #dhcp-sidebar-children, #core-sidebar-children')
            .not(parentsChild).slideUp( 'slow' );
        $(parentsChild).slideToggle( 'slow' );
    });

    $( document ).on( 'click', '.exit-message', function( e ) {
        slideUp_and_remove( $(this).parent() );
    });

    $( document ).on( 'focus', '#id_attribute', function() {
        $('#id_attribute').autocomplete({
            minLength: 1,
            source: function( request, response ) {
                $.ajax({
                    global: false,
                    url: '/eav/search',
                    dataType: 'json',
                    data: {
                        term: request.term,
                        attribute_type: $('#id_attribute_type').val()
                    },
                    success: response
                });
            },
            delay: 400,
            select: function( event, ui ) {
                attributeName = ui.item.label;
            }
        });
    });

    $( document ).on( 'change', '#id_attribute_type', function() {
        $('#id_attribute').val( '' );
    });

    // button behavior logic, see css
    function buttonLogic() {
        var selectors = '.js-get-form, .js-create-object, .update, ' +
            '.cancel, .system_form';
        $(selectors).addClass( 'hover' );
        if ( $(this).hasClass( 'selected' ) ) {
            $(this).removeClass( 'selected' );
        } else {
            $(selectors).removeClass( 'selected' );
            $(this).removeClass( 'hover' ).addClass( 'selected' );
        }
    }
    $( document ).on('click',
        '.js-get-form, .js-create-object, .update, .cancel, .system_form',
        buttonLogic );


    $( document ).on( 'click', '.js-get-form', function( e ) {
        // Show update form on clicking update icon.
        e.preventDefault();
        get_update_form( this );
    });

    function btn_not_toggle_close( btn ) {
        return ($(btn).hasClass( 'selected' ) ||
            $(btn).parents().attr( 'class' ) == 'actions_column');
    };

    function get_update_form( btn ) {
        var kwargs;
        var formTitle;
        var buttonLabel;
        var getData;
        var buttonAttrs;
        var initData;
        slideUp( $('#obj-form') );
        form.action = btn.href;
        if ( btn_not_toggle_close( btn ) ) {
            buttonAttrs = 'btn c js-submit';
            kwargs = JSON.parse( $(btn).attr( 'data-kwargs' ) );
            if ( kwargs.pk ) {
                getData = {
                    'obj_type': kwargs.obj_type,
                    'pk': kwargs.pk
                };
            } else {
                if ( $(btn).attr( 'data-init' ) ) {
                    initData = $(btn).attr( 'data-init' );
                }

                getData = {
                    'data': initData,
                    'obj_type': kwargs.obj_type,
                    'related_pk': metadata.attr( 'data-objPk' ),
                    'related_type': metadata.attr( 'data-objType' ),
                };
            }

            $.ajax({
                type: 'GET',
                url: kwargs.get_url,
                data: getData,
                global: false,
                dataType: 'json',
                success: function( data ) {
                    metaData = $('<div id="form-metadata">')
                        .attr( 'objType', kwargs.obj_type )
                        .attr( 'style', 'display:none' );
                    setTimeout( function() {
                        $('#hidden-inner-form')
                            .empty()
                            .append( data.form )
                            .append( metaData );
                        initForms();
                    }, 150 );
                    $('#form-title').html( data.form_title );
                    $('.form-btns .btn').not('.cancel').text( data.submit_btn_label );
                    $('.form-btns .btn').not('.cancel').attr( 'class', buttonAttrs );
                    $('#obj-form').slideDown();
                }
            });
        }
    };


    function av_form_submit_handler( data ) {
        var is_update = false;
        var id = data.row.postback_urls[0].match(/[1-9]+/g);
        var kwargs;
        if ( $('.attrs_table:hidden') ) {
            $('.attrs_table').slideDown();
            $('.attrs_title').slideDown();
        }
        jQuery.each( $('.attrs_table > tbody > tr'), function( i, row ) {
            kwargs = JSON.parse(
                $(row).find( '.table_delete' ).attr( 'data-kwargs') );
            if ( kwargs.pk == id ) {
                $(this).remove();
                is_update = true;

            }
        });
        insertTablefyRow( data.row, $('.attrs_table > tbody') );
        if ( is_update ) {
            $('#obj-form form').find( '.cancel' ).click();
        } else {
            $('#obj-form form').trigger( 'reset' );
            $('#id_attribute').focus();
        }
    }

    // Form submit handler, special logic for attributes
    $( document ).on( 'click', '.js-submit', function( e ) {
        e.preventDefault();
        var url = $('#obj-form form')[0].action;
        var fields = $('#obj-form form').find( ':input' ).serializeArray();
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        $.when( ajax_form_submit( url, fields, csrfToken ) ).done( function( data ) {
            // for av forms
            if ( $('#obj-form form').attr( 'action' ).indexOf( '_av' ) >= 0 ) {
                av_form_submit_handler( data );
            } else {
                location.reload();
            }
        });
    });
});
