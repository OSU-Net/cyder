$(document).ready(function() {
    var btn = document.getElementById('System');
    btn.onclick = function() {
        var form = document.getElementById('hidden-inner-form');
        var interface_type = document.getElementsByName('interface_type');
        alert('form');
        for(var i = 0; i < interface_type.length; i++){
            interface_type[i].onclick = function() {
                alert(this.value);
                if (this.value == 'None') {
                    alert('none!');
                } else {
                    alert('test');
                }
            };
        };
    //$('#CreateSystem').click(function(event) {
      //  alert('yup');
      //  var postData = {
      //      name: document.getElementById('id_name').value,
     //       department: document.getElementById('id_department').value,
     //       location: document.getElementById('id_location').value
     //   };
        $.post();
    };
});
