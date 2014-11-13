$(document).ready(function() {
    var RangeWizard = null;
    function enableRangeWizard() {
    RangeWizard = (function(){
        var csrfToken = $('#view-metadata').attr( 'data-csrfToken' );
        var rng = '#id_range';
        var freeIp = '#id_next_ip';
        var ip = '#id_ip_str';
        var ipv4 = '#id_ip_type_0';
        var ipv6 = '#id_ip_type_1';
        var site = '#id_site';
        var vrf = '#id_vrf';
        var rangeType = "input[type='radio'][name='interface_type']:checked";
        return {
            get_ip: function() {
                if ( $(rng).val() == '' ) {
                    $(ip).val('');
                    return false;
                }
                var postData = {
                    csrfmiddlewaretoken: csrfToken,
                    freeIp: $(freeIp).attr( 'checked' ) ? true : false,
                    range: $(rng).val(),
                };
                $.ajax({
                    type: 'POST',
                    url: '/dhcp/range/range_wizard_get_ip/',
                    data: postData,
                    dataType: 'json',
                    global: false,
                }).done( function( data ) {
                    if ( data.ip_type == $(ipv4).val() ) {
                        $(ipv4).attr( 'checked', 'checked' );
                    } else {
                        $(ipv6).attr( 'checked', 'checked' );
                    }
                    $(ip).val( data.ip_str );
                });
            },
            get_ranges: function() {
                var postData = {
                    csrfmiddlewaretoken: csrfToken,
                    rangeType: $(rangeType).val(),
                    site: $(site).val(),
                    vrf: $(vrf).val(),
                };
                $.ajax({
                    type: 'POST',
                    url: '/dhcp/range/range_wizard_get_ranges/',
                    data: postData,
                    dataType: 'json',
                    global: false,
                }).done( function( data ) {
                    $(rng).find( 'option' ).remove().end();
                    if ( data.ranges[0].length === 0 ) {
                        $(rng)
                           .find( 'option' )
                           .end()
                           .append( "<option value=''>No ranges in " +
                                    $('#id_vrf option:selected').text() +
                                    " and " +
                                    $('#id_site option:selected').text() +
                                    '</option>' );
                    } else {
                        for ( var i in data.ranges[0] ) {
                            $(rng)
                                .find( 'option' )
                                .end()
                                .append( '<option value=' + data.ranges[1][i] +
                                    '>' + data.ranges[0][i] + '</option>');
                        }
                    }
                    $(rng).change();
                });
            }
        }
    }());
    }


    function range_wizard_controller( source ) {
        if ( source.id == 'id_range' || source.id == 'id_next_ip' ) {
            RangeWizard.get_ip();
        } else {
            RangeWizard.get_ranges();
        }
    }


    $( document ).on( 'change', '.wizard', function() {
        if (RangeWizard == null) {
            enableRangeWizard();
        }
        range_wizard_controller( this );
    });
});
