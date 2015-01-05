$(document).ready(function() {
    var systemForm = (function(){
        // avoid duplicate fields id's
        var staticForm = $('#static-form')
            .clone().wrap( '<div>' ).parent().html();
        var dynamicForm = $('#dynamic-form')
            .clone().wrap( '<div>' ).parent().html();
        $('#static-form').remove();
        $('#dynamic-form').remove();
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
            }
        };
    }());

    function changeSystemForm( value, delay, speed ) {
        if ( value == 'static_interface' ) {
            systemForm.showStaticForm( delay, speed );
        } else {
            systemForm.showDynamicForm( delay, speed );
        }
    }

    // if initial page load
    jQuery.each( $("input[name='interface_type']:checked"), function() {
        changeSystemForm( this.value, 0, 'fast' );
    });

    $("input[name='interface_type']").change( function() {
        // dont delay on initial page load
        if( $('#dynamic-form').length || $('#static-form').length ) {
            changeSystemForm( this.value, 500, 'slow' );
        } else {
            changeSystemForm( this.value, 0, 'fast' );
        }
    });

    $( document ).on('submit', '#system-form form', function( e ) {
        e.preventDefault();
        var fields;
        $(this).find('.error').remove();
        if ($("input[name=interface_type]:checked").val() === undefined) {
            $("label[for=id_interface_type_0]:first").after(
                '<p class="error">This field is required.</p>');
            return false;
        } else {
            fields = $(this).find(':input:visible').serializeArray();
        }

        var url = '/core/system/create/';
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        $.when( ajax_form_submit( url, fields, csrfToken ) ).done( function( ret_data ) {
            location.href = '/core/system/' + ret_data.system_id.toString();
        })
    });
});
