$(document).ready(function() {
    var metadata = $('#view-metadata');
    var form = $('#obj-form form')[0];
    var hidden_inner_form = document.getElementById('hidden-inner-form');
    if(hidden_inner_form) {
        var defaults = hidden_inner_form.innerHTML;
    }
    var objType = metadata.attr('data-objType');
    var objName = metadata.attr('data-objName');
    var prettyObjType = metadata.attr('data-prettyObjType');
    var searchUrl = metadata.attr('data-searchUrl');
    var getUrl = metadata.attr('data-getUrl');
    var domainsUrl = metadata.attr('data-domainsUrl');
    var objPk = metadata.attr('data-objPk');
    var csrfToken = metadata.attr('data-csrfToken');

    // For inputs with id = 'id_fqdn' | 'id_target' | server, make smart names.
    if (domainsUrl) {
        make_smart_name_get_domains(
            $('#id_fqdn, #id_target, #id_server'), true, domainsUrl);
    }

    // displays the loading gif on ajax event
    $('.load').ajaxStart(function() {
        $(this).show();
    }).ajaxStop(function() {
        $(this).hide();
    });

    // toggles the settings menu in mobile view
    $('#settings-btn').click( function(e) {
        $('.settings-menu').slideToggle();
        $('#settings-btn').toggleClass('selected');
    });

    // toggles the sidebar in mobile view
    $('#menu-btn').click( function(e) {
        $('#menu-btn').toggleClass('selected');
        $('#sidebar_div').toggleClass('displayed');
    });

    // sidebar animation logic
    $('.nav-item.parent').click( function(e) {
        e.preventDefault();
        var parentsChild = ('#' + this.id + '-children');
        if ($(parentsChild).css('display') != 'none') {
            $(parentsChild).slideUp('slow');
        } else {
            var children = [
                '#dns-sidebar-children',
                '#dhcp-sidebar-children',
                '#core-sidebar-children'];
            $.each(children, function(i, child) {
                if (parentsChild != child) {
                    if ($(child).css('display') != 'none') {
                        $(child).slideToggle('slow');
                    }
                }
            });
            $(parentsChild).slideToggle('slow');
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

    $('#delete, .delete').live( 'click', function(e) {
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
                          "sure you want to continue?"
                };
                if ( confirm( msg ) ) {
                    button_to_form( button, csrfToken, function ( postForm ) {
                        $(postForm).submit();
                    });
                } else {
                    return false;
                };
            });
        } else {
            if ( kwargs.obj_type == "system" ) {
                msg = "Deleting this system will also delete its" +
                    " interfaces. Are you sure you want to continue?";
            };
            if ( confirm( msg ) ) {
                button_to_form( this, csrfToken, function ( postForm ) {
                    $(postForm).submit();
                });
            } else {
                return false;
            };
        };
    });

    $('#id_attribute').live('focus', function() {
        $('#id_attribute').autocomplete({
            minLength: 1,
            source: function(request, response) {
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
            select: function(event, ui) {
                attributeName = ui.item.label;
            }
        });
    });

    $('#id_attribute_type').live('change', function() {
        $('#id_attribute').val('');
    });

    $('.create-obj, .update, .cancel').each(function() {
        $('.create-obj, .update, .cancel').addClass('hover');
        $(this).click(function(e) {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
            } else {
                $('.create-obj, .update, .cancel').removeClass('selected');
                $(this).removeClass('hover').addClass('selected');
            }
        });
    });

    $('.create-obj').click(function(e) {
        // Show create form on clicking create button.
        e.preventDefault();

        slideUp($('#obj-form'));
        if ($(this).hasClass('selected')) {
            form.action = this.href;
            if(this.hasAttribute('data-objType')) {
                var $createBtn = $(this);
                var formPrettyObjType = $createBtn.attr('data-prettyobjtype');
                var formObjType = $createBtn.attr('data-objType');
                $('#obj-form form').attr('objType', formObjType);
                var formGetUrl = $createBtn.attr('data-getUrl');
                var data_to_post = $createBtn.attr('data-kwargs');
                var formTitle = 'Creating ' + formPrettyObjType;

                $.get(formGetUrl,
                    {
                        'obj_type': formObjType,
                        'related_type': objType,
                        'related_pk': objPk,
                        'data': data_to_post
                    },
                    function(data) {
                        setTimeout(function() {
                            $('#form-title').html(formTitle);
                            data.form.action = $createBtn.attr('href');
                            $('.inner-form').empty().append(data.form);
                            initForms();
                        }, 150);
                        $('#obj-form form')[0].action = $createBtn.attr('href');
                        $('.form-btns a.submit, .btn.ajax').text(
                            'Create ' + formPrettyObjType);
                        $('.form-btns a.submit').attr('class', 'btn c submit_create ajax');
                        $('#obj-form').slideToggle();
                    }, 'json');
            } else {
                $('#obj-form form').attr('objType', objType);
                setTimeout(function() {
                    $('#form-title').html('Creating ' + prettyObjType);

                    if(defaults) {
                        $('#hidden-inner-form').empty().html(defaults);
                    } else {
                        clear_form_all(form);
                    }
                }, 150);
                $('.form-btns a.submit, .btn.ajax').text('Create ' + prettyObjType);

                $('.form-btns a.submit').attr('class', 'btn c submit_create ajax');
                $('#obj-form').slideToggle();
            }
            $('#id_value').live("keypress", function(e) {
                if (e.which == 13) {
                    jQuery('.submit_create').focus().click();
                }
            });
            $('.form').append($('<input>',
                              {type: 'hidden', name: 'csrfmiddlewaretoken',
                               value: csrfToken}));
        }
    });

    $('.update').live( 'click', function(e) {
        // Show update form on clicking update icon.
        slideUp($('#obj-form'));
        e.preventDefault();
        if ($(this).hasClass('selected') ||
                $(this).parents().attr('class') == 'actions_column') {
            form.action = this.href;
            var formObjName = $(this).attr('data-objName') || objName;
            var formObjType = $(this).attr('data-objType');
            $('#obj-form form').attr('objType', formObjType);
            var formPrettyObjType = $(this).attr('data-prettyObjType');
            var formTitle = 'Updating ' + formPrettyObjType + ' ' + formObjName;

            $.get($(this).attr('data-getUrl') || getUrl,
                    {'obj_type': formObjType, 'pk': $(this).attr('data-pk')},
                    function(data) {
                setTimeout(function() {
                    $('#form-title').html(formTitle);
                    $('#hidden-inner-form').empty().append(data.form);
                    initForms();
                }, 150);
                $('.form-btns a.submit, .btn.ajax').text('Update ' + formPrettyObjType);

                $('.form-btns a.submit').attr('class', 'btn c submit_update ajax');
                $('#obj-form').slideDown();
            }, 'json');
            $('#id_value').live("keypress", function(e) {
                if (e.which == 13) {
                    jQuery('.submit_update').focus().click();
                }
            });

            $('.form').append($('<input>', {type: 'hidden',
                name: 'csrfmiddlewaretoken', value: csrfToken}));
        }
    });
    $('#Bug-Report').live('submit', function(event) {
        event.preventDefault();
        url = $(location).attr('href');
        var data = ajax_form_submit(url, $('#Bug-Report'), csrfToken, function(data) {
            if (!data.errors) {
                alert('Your bug report was sent successfully. ' +
                      'Thank you for your input!');
                $('#Bug-Report')[0].reset();
                window.location.href = '/';
            }
        });
    });

    $('#obj-form form').live('submit', function(event) {
        var url = $('#obj-form form')[0].action;
        event.preventDefault();
        ajax_form_submit(url, $('#obj-form'), csrfToken,
                         function(data) {
            if (!data.errors) {
                if ($('#obj-form form').attr('action').indexOf('_av') >= 0) {
                    var style = $('.attrs_table').attr('style');
                    if (style !== undefined && style !== false &&
                            $('.attrs_table').attr('style').indexOf(
                            'display:none') < 0) {
                        $('#attr_title').slideDown();
                        $('.attrs_table').attr('style', '');
                    }
                    var is_update = false;
                    jQuery.each($('.attrs_table > tbody > tr'), function(i, row) {
                        if (row.cells[0].innerHTML.indexOf(
                                data.row.data[0][0].value[0]) >= 0) {
                            $(this.remove());
                            is_update = true;

                        }
                    });
                    insertTablefyRow(data.row, $('.attrs_table > tbody'));
                    if (is_update) {
                        $('#obj-form form').find('.cancel').click();
                    } else {
                        $('#obj-form form').trigger('reset');
                        $('#id_attribute').focus();
                    }
                } else {
                    location.reload();
                }
            }
        });
    });
});
