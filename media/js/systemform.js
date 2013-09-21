$(document).ready(function() {
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
});
