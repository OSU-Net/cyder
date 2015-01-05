$(document).ready(function() {
    var systemForm = null;

    function enable_system_form( data ) {
        systemForm = (function(){
            // avoid duplicate fields id's
            var staticForm = $('<div id=static-form>')
                .html(data.static_form);
            var dynamicForm = $('<div id=dynamic-form>')
                .html(data.dynamic_form);
            var initial_type = data.initial_type;
            return {
                showStaticForm: function( delay, speed ) {
                    setTimeout( function() {
                        $('#hidden-inner-form').append( staticForm );
                        $('#static-form').slideDown( speed );
                    }, delay);
                    $('#dynamic-form').slideUp( function() {
                        $('#dynamic-form').remove();
                    });
                },
                showDynamicForm: function( delay, speed ) {
                    setTimeout( function() {
                        $('#hidden-inner-form').append( dynamicForm );
                        $('#dynamic-form').slideDown( speed );
                    }, delay);
                    $('#static-form').slideUp( function() {
                        $('#static-form').remove();
                    });
                },
                submitForm: function() {
                    var fields;
                    var form = $('#obj-form form');
                    form.find('.error').remove();
                    if ($("input[name=interface_type]:checked").val() === undefined) {
                        $("label[for=id_interface_type_0]:first").after(
                            '<p class="error">This field is required.</p>');
                        return false;
                    } else {
                        fields = form.find(':input:visible').serializeArray();
                    }
                    if ( initial_type.length ) {
                        fields['interface_type'] = initial_type;
                    }

                    var url = '/core/system/create/';
                    var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
                    $.when( ajax_form_submit( url, fields, csrfToken ) ).done(
                            function( ret_data ) {
                        location.href = '/core/system/' + ret_data.system_id.toString();
                    })
                }
            };
        }());
    }

    function changeSystemForm( value, delay, speed ) {
        if ( value == 'static_interface' ) {
            systemForm.showStaticForm( delay, speed );
        } else {
            systemForm.showDynamicForm( delay, speed );
        }
    }

    $( document ).on( 'change', 'input[name="interface_type"]', function() {
        // dont delay on initial page load
        if( $('#dynamic-form').length || $('#static-form').length ) {
            changeSystemForm( this.value, 500, 'slow' );
        } else {
            changeSystemForm( this.value, 0, 'fast' );
        }
    });

    $( document ).on('click', '#system-submit', function( e ) {
        e.preventDefault();
        systemForm.submitForm();
    });

    $( document ).on( 'click', '.system_form', function( e ) {
        e.preventDefault();
        slideUp( $('#obj-form') );
        url = this.href;
        button_to_ajax( this, null, { 'mode': 'GET', 'dataType': 'json' } )
        .done( function( data ) {
            $('#obj-form form')[0].action = url;
            $('#form-title').html( data.form_title );
            $('.form-btns .submit').text( data.submit_btn_label );
            $('.form-btns .submit').attr( 'class', 'btn c system-submit');
            $('#hidden-inner-form').empty().append( data.system_form );
            slideDown( $('#obj-form') );
            enable_system_form( data );
            if ( data.initial_type ) {
                changeSystemForm( data.initial_type, 0, 'fast' );
            }
        });
    });

    // If landing on an empty system list page, bring up create form
    if( $('.table').length == 0 ) {
        $('.system_form').click();
    }
});
