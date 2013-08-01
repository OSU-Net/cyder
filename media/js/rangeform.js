$(document).ready(function() {
    var create_btn = document.getElementById('btn create-obj');
    create_btn.onclick = function() {
        var network = document.getElementById('id_network');
        network.onchange = function() {
            var network_str = (network.options[network.selectedIndex].text).split('/');
            var initial = (network_str[0].split('.').slice(0, (~~(network_str[1]/8)))).join('.');
            var start_str = document.getElementById('id_start_str');
            var end_str = document.getElementById('id_end_str');
            start_str.value = initial;
            end_str.value = initial;
        };

    };

});
