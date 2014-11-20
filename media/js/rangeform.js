$(document).ready(function() {
    $( document ).on( 'change', '.networkWizard', function() {
        var selectedNetwork = $('#id_network').find(':selected');
        if (selectedNetwork.val() == '') {
            $('#id_start_str').val('');
            $('#id_end_str').val('');
        } else {
            var networkStr = selectedNetwork.text().split('/')[0];
            var initial = networkStr.split('.');
            initial.pop();
            initial = initial.join('.');
            $('#id_start_str').val(initial);
            $('#id_end_str').val(initial);
        }
    });
});
