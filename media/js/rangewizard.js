$(document).ready(function() {
    var rangeWizard = $('#rangeWizard');
    var rangeWizardUrl = rangeWizard.attr('data-rangeWizard');
    $('.wizard').live('change', function() {
        var rng;
        if(this.id == 'id_range') {
            rng = $('#id_range').val();
        } else {
            rng = '';
        };
        var postData = {
            vrf: $('#id_vrf').val(),
            site: $('#id_site').val(),
            range: rng,
        };
        $.post(rangeWizardUrl, postData, function(data) {
            if(data.ranges) {
                $('#id_range').find('option').remove().end();
                for(i in data.ranges[0]) {
                    $('#id_range').find('option').end().append('<option value=' + data.ranges[1][i] + '>' + data.ranges[0][i] + '</option>');
                };
            };
            if(data.ip) {
                if(data.ip[0] == $('#id_ip_type_0').val()) {
                    $('#id_ip_type_0').attr('checked', 'checked');
                } else {
                    $('#id_ip_type_1').attr('checked', 'checked');
                };

                $('#id_ip_str').val(data.ip[1]);
            }
        }, 'json');
    });
});
