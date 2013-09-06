$(document).ready(function() {
    var rangeWizard = $('#rangeWizard');
    var rangeWizardUrl = rangeWizard.attr('data-rangeWizard');
    var form = document.getElementById('inner-form');
    var interface_type = document.getElementsByName('interface_type');
    var static_form = document.getElementById('static-form');
    var static_clone = static_form.cloneNode(true);
    static_clone.id ="static_clone";
    $(static_clone).removeAttr('style');
    var dynamic_form = document.getElementById('dynamic-form');
    var dynamic_clone = dynamic_form.cloneNode(true);
    dynamic_clone.id ="static_clone";
    $(dynamic_clone).removeAttr('style');
    if ($('#radio').attr('checked') == 'true') {
        alert('firstcheck');
    };
    for(var i = 0; i < interface_type.length; i++) {
        if (interface_type[i].checked) {
            if (form.lastChild.textContent != '') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (interface_type[i].value =='Static') {
                form.appendChild(static_clone);
            } else {
                form.appendChild(dynamic_clone);
            };
        };
        interface_type[i].onclick = function() {
            if (form.lastChild.textContent != '') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (this.value =='Static') {
                form.appendChild(static_clone);
            } else {
                form.appendChild(dynamic_clone);
            };
        };
    };
    if(form.lastChild.id == 'static_clone') {
        $('.wizard').change(function() {
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
                    $('#id_ip_type').val(data.ip[0]).trigger('change');
                    $('#id_ip_str').val(data.ip[1]);
                }
            }, 'json');
        });
    };
});
