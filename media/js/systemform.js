$(document).ready(function() {
    var form = document.getElementById('hidden-inner-form');
    var interface_type = document.getElementsByName('interface_type');
    var static_form = document.getElementById('static-form');
    var static_clone = static_form.cloneNode(true);
    static_clone.id ="static_clone";
    $(static_clone).removeAttr('style');
    var dynamic_form = document.getElementById('dynamic-form');
    var dynamic_clone = dynamic_form.cloneNode(true);
    dynamic_clone.id ="static_clone";
    $(dynamic_clone).removeAttr('style');
    initial_interface_type = $('#view-metadata').attr(
        'data-initial_interface_type');
    if (initial_interface_type) {
        $('input[name=interface_type][value=' +
            initial_interface_type + ']').attr('checked', true);
    };
    for(var i = 0; i < interface_type.length; i++) {
        if (interface_type[i].checked) {
            if (form.lastChild.textContent != '') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (interface_type[i].value =='static_interface') {
                form.appendChild(static_clone);
            } else {
                form.appendChild(dynamic_clone);
            };
        };
        interface_type[i].onclick = function() {
            if (form.lastChild.textContent != '') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (this.value =='static_interface') {
                form.appendChild(static_clone);
            } else {
                form.appendChild(dynamic_clone);
            };
        };
    };

    $('form#system-form').live('submit', function(event) {
        event.preventDefault();

        var url = $('form#system-form')[0].action;
        var data = ajax_form_submit(url, $('form#system-form'),
            $('#csrfToken').val());
        if (!data.errors) {
            location.href = '/core/system/' + data.system_id.toString();
        };

        if ($("input[name=interface_type]:checked").val() === undefined) {
            $("label[for=id_interface_type_0]:first").after(
                '<p id="error"><font color="red">This field is required.' +
                '</font></p>')
        };
    });
});
