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

//----------------------------------------------------------------------------
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

    // returns a deferred object, when resolved returns a string
    function get_delete_confirm_msg( kwargs, csrfToken ) {
        var deferred = $.Deferred();
        var msg = "Are you sure you want to delete this?";
        var ret_data = {}
        if ( kwargs.obj_type.indexOf( 'interface' ) != -1) {
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
                // if the object is in a table and not the last element of
                // that table delete the row
                if ( $( btn ).hasClass( 'table_delete' ) &&
                        $( btn ).parents( 'tbody' ).find( 'tr' ).length > 1 ) {
                    $( btn ).parents( 'tr' ).remove();
                } else {
                    window.location.href = data.url;
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
//----------------------------------------------------------------------------

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
        var kwargs;
        var formTitle;
        var buttonLabel;
        var getData;
        var buttonAttrs;
        var initData;
        slideUp( $('#obj-form') );
        e.preventDefault();
        form.action = this.href;
        if ( $(this).hasClass( 'selected' ) ||
                $(this).parents().attr( 'class' ) == 'actions_column') {
            kwargs = JSON.parse( $(this).attr( 'data-kwargs' ) );
            // #TODO move all this logic to get_update_form
            if ( kwargs.pk ) {
                buttonAttrs = 'btn c submit_update js-submit';
                getData = {
                    'obj_type': kwargs.obj_type,
                    'pk': kwargs.pk
                };
            } else {
                buttonAttrs = 'btn c submit_create js-submit';
                if ( $(this).attr( 'data-init' ) ) {
                    initData = $(this).attr( 'data-init' );
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
    });


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
