$(document).ready(function() {
    function rangeWizardResult( data ) {
        if ( data.ranges ) {
            $('#id_range').find( 'option' ).remove().end();
            if ( data.ranges[0].length === 0 ) {
                $('#id_range')
                   .find( 'option' )
                   .end()
                   .append( "<option value=''>No ranges in " +
                            $('#id_vrf option:selected').text() +
                            " and " +
                            $('#id_site option:selected').text() +
                            '</option>' );
            } else {
                for ( var i in data.ranges[0] ) {
                $('#id_range')
                    .find( 'option' )
                    .end()
                    .append( '<option value=' + data.ranges[1][i] +
                             '>' + data.ranges[0][i] + '</option>');
                }
            }
        }
        if ( data.ip_type ) {
            if ( data.ip_type == $('#id_ip_type_0').val() ) {
                $('#id_ip_type_0').attr( 'checked', 'checked' );
            } else {
                $('#id_ip_type_1').attr( 'checked', 'checked' );
            }

            $('#id_ip_str').val( data.ip_str );
        }
    }


    function rangeWizardController( source ) {
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        var rangeType = $(
            "input[type='radio'][name='interface_type']:checked" ).val();

        if ( source.id == 'id_range' && $('#id_range').val() == '') {
            $('#id_ip_str').val('');
            return false;
        }

        var postData = {
            csrfmiddlewaretoken: csrfToken,
            freeIp: $('#id_next_ip').attr( 'checked' ) ? true : false,
            range: $('#id_range').val(),
            rangeType: rangeType,
            site: $('#id_site').val(),
            vrf: $('#id_vrf').val(),
        };
        if ( source.id == 'id_next_ip' && $('#id_range').val() !== '' ||
             source.id != 'id_next_ip' ) {
            $.ajax({
                type: 'POST',
                url: '/dhcp/range/range_wizard/',
                data: postData,
                dataType: 'json',
                global: false,
                success: rangeWizardResult
            });
        }
    }


    $( document ).on( 'change', '.wizard', function() {
        rangeWizardController( this );
    });
});
