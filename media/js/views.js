$(document).ready( function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var objType = metadata.attr( 'data-objType' );
    var objPk = metadata.attr( 'data-objPk' );
    var searchUrl = metadata.attr( 'data-searchUrl' );
    var domainsUrl = metadata.attr( 'data-domainsUrl' );
    var csrfToken = metadata.attr( 'data-csrfToken' );

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
        if ( $(parentsChild).css( 'display' ) != 'none' ) {
            $(parentsChild).slideUp( 'slow' );
        } else {
            var children = [
                '#dns-sidebar-children',
                '#dhcp-sidebar-children',
                '#core-sidebar-children'];
            $.each( children, function( i, child ) {
                if ( parentsChild != child ) {
                    if ( $(child).css( 'display' ) != 'none' ) {
                        $(child).slideToggle( 'slow' );
                    }
                }
            });
            $(parentsChild).slideToggle( 'slow' );
        }
    });

    // handles create buttons in dynamic/static interface view and range
    // detail view
    $('#system_create').live( 'click', function( e ) {
        e.preventDefault();
        button_to_form( this, csrfToken, function ( postForm ) {
            $(postForm).submit();
        });
    });

    // handles all delete buttons
    $('#delete, .delete').live( 'click', function( e ) {
        e.preventDefault();
        var button = this;
        var kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
        var msg = "Are you sure you want to delete this?";
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

    $('#id_attribute').live( 'focus', function() {
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

    $('#id_attribute_type').live( 'change', function() {
        $('#id_attribute').val( '' );
    });

    // button behavior logic, see css
    $('.getForm, .create-obj, .update, .cancel').each( function() {
        $('.getForm, .create-obj, .update, .cancel').addClass( 'hover' );
        $(this).click( function( e ) {
            if ( $(this).hasClass( 'selected' ) ) {
                $(this).removeClass( 'selected' );
            } else {
                $('.getForm, .create-obj, .update, .cancel').removeClass( 'selected' );
                $(this).removeClass( 'hover' ).addClass( 'selected' );
            }
        });
    });

    $('.getForm').live( 'click', function( e ) {
        // Show update form on clicking update icon.
        var kwargs;
        var formTitle;
        var buttonLabel;
        var getData;
        var buttonAttrs;
        slideUp($('#obj-form'));
        e.preventDefault();
        form.action = this.href;
        if ( $(this).hasClass( 'selected' ) ||
                $(this).parents().attr( 'class' ) == 'actions_column') {
            kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
            if ( kwargs.pk ) {
                formTitle = 'Updating ' + kwargs.pretty_obj_type + ' ' + kwargs.obj_name;
                buttonLabel = 'Update ' + kwargs.pretty_obj_type;
                buttonAttrs = 'btn c submit_update ajax';
                getData = { 'obj_type': kwargs.obj_type, 'pk': kwargs.pk };
            } else {
                formTitle = 'Creating ' + kwargs.pretty_obj_type;
                buttonLabel = 'Create ' + kwargs.pretty_obj_type;
                buttonAttrs = 'btn c submit_create ajax';
                getData = {
                    'data': $(this).attr( 'data-kwargs' ),
                    'obj_type': kwargs.obj_type,
                    'related_pk': objPk,
                    'related_type': objType,
                };
            }

            $.get( kwargs.get_url , getData, function( data ) {
                setTimeout( function() {
                    $('#form-title').html( formTitle );
                    $('#hidden-inner-form').empty().append( data.form );
                    initForms();
                }, 150 );
                $('.form-btns a.submit, .btn.ajax').text( buttonLabel );
                $('.form-btns a.submit').attr( 'class', buttonAttrs );
                $('#obj-form').slideDown();
            }, 'json' );

            $('#id_value').live( "keypress", function( e ) {
                if ( e.which == 13 ) {
                    jQuery('.ajax').focus().click();
                }
            });

            $('.form').append(
                $('<input>',
                {
                    type: 'hidden',
                    name: 'csrfmiddlewaretoken',
                    value: csrfToken
                } ) );
        }
    });

    // Form submit handler, special logic for attributes
    $('#obj-form form').live( 'submit', function( e ) {
        var url = $('#obj-form form')[0].action;
        var fields = $('#obj-form form').find( ':input' ).serializeArray();
        e.preventDefault();
        ajax_form_submit( url, fields, csrfToken, function( data ) {
            if ( !data.errors ) {
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
            }
        });
    });
});
