$(document).ready( function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var domainsUrl = metadata.attr( 'data-domainsUrl' );

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    if ( domainsUrl ) {
        make_smart_name_get_domains(
            $('#id_fqdn, #id_target, #id_server'), true, domainsUrl );
    }

    // displays the loading gif on ajax event
    $('.load').ajaxStart( function() {
        $(this).show();
    }).ajaxStop( function() {
        $(this).hide();
    });

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

    // sidebar animation logic
    $('.nav-item.parent').click( function( e ) {
        e.preventDefault();
        var parentsChild = ( '#' + this.id + '-children' );
        $('#dns-sidebar-children, #dhcp-sidebar-children, #core-sidebar-children')
            .not(parentsChild).slideUp( 'slow' );
        $(parentsChild).slideToggle( 'slow' );
    });

    // handles create buttons in dynamic/static interface view and range
    // detail view
    $( document ).on( 'click', '#system_create', function( e ) {
        e.preventDefault();
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        button_to_form( this, csrfToken, function( postForm ){
            $(postForm).submit();
        });
    });

    $( document ).on( 'focus', '#id_attribute', function() {
        $('#id_attribute').autocomplete({
            minLength: 1,
            source: function( request, response ) {
                $.ajax({
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
        $('.js-get-form, .js-create-object, .update, .cancel').addClass( 'hover' );
        if ( $(this).hasClass( 'selected' ) ) {
            $(this).removeClass( 'selected' );
        } else {
            $('.js-get-form, .js-create-object, .update, .cancel').removeClass( 'selected' );
            $(this).removeClass( 'hover' ).addClass( 'selected' );
        }
    }
    $( document ).on('click', '.js-get-form, js-create-object, .update, .cancel', buttonLogic );


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
            kwargs = JSON.parse( $(btn).attr( 'data-kwargs' ) );
            if ( kwargs.pk ) {
                buttonAttrs = 'btn c submit_update js-submit';
                getData = {
                    'obj_type': kwargs.obj_type,
                    'pk': kwargs.pk
                };
            } else {
                buttonAttrs = 'btn c submit_create js-submit';
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
                    setTimeout( function() {
                        $('#hidden-inner-form').empty().append( data.form );
                        initForms();
                    }, 150 );
                    $('#form-title').html( data.form_title );
                    $('.form-btns a.submit, .btn.js-submit').text( data.submit_btn_label );
                    $('.form-btns a.submit').attr( 'class', buttonAttrs );
                    $('#obj-form').slideDown();
                }
            }).done( function() {
                $('#obj-form form :input:visible:last').on( 'keypress', function( e ) {
                    if ( e.which == 13 ) {
                        $('.js-submit').focus().click();
                    }
                });
            });
        }
    };


    function av_form_submit_handler( data ) {
        if ( $('.attrs_table:hidden') ) {
            $('.attrs_table').slideDown();
            $('.attrs_title').slideDown();
        }
        var is_update = false;
        jQuery.each( $('.attrs_table > tbody > tr'), function( i, row ) {
            if ( row.cells[0].innerHTML.indexOf(
                    data.row.data[0][0].value[0] ) >= 0 ) {
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
    $( document ).on( 'submit', '#obj-form form', function( e ) {
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
