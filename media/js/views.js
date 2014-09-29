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

    // handles all delete buttons
    $( document ).on( 'click', '#delete, .delete', function( e ) {
        e.preventDefault();
        var button = this;
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        var msg = "Are you sure you want to delete this?";
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        if ( kwargs.obj_type.indexOf( 'interface' ) != -1) {
            var postData = {
                pk: kwargs.pk,
                obj_type: kwargs.obj_type,
                csrfmiddlewaretoken: csrfToken,
            };
            $.post( '/dhcp/interface/last_interface/', postData, function( data ) {
                if ( data == "true" ) {
                    msg = "Because this is the last interface on " +
                          "its system, deleting this interface " +
                          "will also delete its system. Are you " +
                          "sure you want to continue?";
                }
                if ( confirm( msg ) ) {
                    button_to_form( button, csrfToken, function ( postForm ) {
                        $(postForm).submit();
                    });
                } else {
                    return false;
                }
            });
        } else {
            if ( kwargs.obj_type == "system" ) {
                msg = "Deleting this system will also delete its" +
                    " interfaces. Are you sure you want to continue?";
            }
            if ( confirm( msg ) ) {
                button_to_form( this, csrfToken, function ( postForm ) {
                    $(postForm).submit();
                });
            } else {
                return false;
            }
        }
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
        $('.js-get-form, .js-create-object, .update, .cancel').addClass( 'hover' )
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
        var kwargs;
        var formTitle;
        var buttonLabel;
        var getData;
        var buttonAttrs;
        var initData;
        var objPk = metadata.attr( 'data-objPk' );
        var objType = metadata.attr( 'data-objType' );
        slideUp( $('#obj-form') );
        e.preventDefault();
        form.action = this.href;
        if ( $(this).hasClass( 'selected' ) ||
                $(this).parents().attr( 'class' ) == 'actions_column') {
            kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
            // #TODO move all this logic to get_update_form
            if ( kwargs.pk ) {
                formTitle = 'Updating ' + kwargs.pretty_obj_type + ' ' + kwargs.obj_name;
                buttonLabel = 'Update ' + kwargs.pretty_obj_type;
                buttonAttrs = 'btn c submit_update js-submit';
                getData = { 'obj_type': kwargs.obj_type, 'pk': kwargs.pk };
            } else {
                formTitle = 'Creating ' + kwargs.pretty_obj_type;
                buttonLabel = 'Create ' + kwargs.pretty_obj_type;
                buttonAttrs = 'btn c submit_create js-submit';
                if ( $(this).attr( 'data-init' ) ) {
                    initData = $(this).attr( 'data-init' );
                }

                getData = {
                    'data': initData,
                    'obj_type': kwargs.obj_type,
                    'related_pk': objPk,
                    'related_type': objType,
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
                        $('#form-title').html( formTitle );
                        $('#hidden-inner-form').empty().append( data.form );
                        initForms();
                    }, 150 );
                    $('.form-btns a.submit, .btn.js-submit').text( buttonLabel );
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
    });


    // Form submit handler, special logic for attributes
    $( document ).on( 'submit', '#obj-form form', function( e ) {
        e.preventDefault();
        var url = $('#obj-form form')[0].action;
        var fields = $('#obj-form form').find( ':input' ).serializeArray();
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        $.when( ajax_form_submit( url, fields, csrfToken ) ).done( function( data ) {
            // for av forms
            if ( $('#obj-form form').attr( 'action' ).indexOf( '_av' ) >= 0 ) {
                var style = $('.attrs_table').attr( 'style' );
                if ( style !== undefined && style !== false &&
                        $('.attrs_table').attr( 'style' ).indexOf(
                        'display:none' ) < 0 ) {
                    $('#attr_title').slideDown();
                    $('.attrs_table').attr( 'style', '' );
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
            } else {
                location.reload();
            }
        });
    });
});
