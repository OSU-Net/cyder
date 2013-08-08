$(document).ready(function() {
    var form = document.getElementById('add-object-inner-form');
    var ctnr = $('#ctnr-data');
    var searchUrl = null;
    var addObjectUrl = ctnr.attr('data-addObjectUrl');
    var ctnrPk = ctnr.attr('data-ctnr-pk');
    var objPk = null;
    var objName = null;
    var objType = null;
    var confirmation = false;
    var obj_select = document.getElementsByName('obj_type');
    var add_user_form = document.getElementById('add-user-form');
    var user_clone = add_user_form.cloneNode(true);
    user_clone.id="user_clone";
    $(user_clone).removeAttr('style');

    for(var i = 0; i < obj_select.length; i++) {
        if (obj_select[i].checked) {
            if (form.lastChild.tagName == 'DIV') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (obj_select[i].value == 'user') {
                 form.appendChild(user_clone);
            };
            objType = obj_select[i].value;
            searchUrl = ctnr.attr(('data-search' + obj_select[i].value + 'Url'));
            $('label[for="object-searchbox"]').text(obj_select[i].value + ':');
        };
        obj_select[i].onclick = function() {
            if (form.lastChild.tagName == 'DIV') {
                form.removeChild(form.childNodes[form.childNodes.length -1]);
            };
            if (this.value == 'user') {
                 form.appendChild(user_clone);
            };
            objType = this.value;
            searchUrl = ctnr.attr(('data-search' + this.value + 'Url'));
            $('label[for="object-searchbox"]').text(this.value + ':');
            // Auto complete for object search dialog.
        };
        $('#object-searchbox').autocomplete({
            minLength: 1,
            source: searchUrl,
            delay: 400,
            select: function(event, ui) {
                objPk = ui.item.pk;
                objName = ui.item.label;
            }
        });
    };
    // Add object to ctnr.
    $('#add-object-ctnr').click(function(event) {
        if (objName != ($('#object-searchbox').val())) {
            objPk = null;
            objName = ($('#object-searchbox').val());
        }

        var postData = {
            obj_pk: objPk,
            obj_name: objName,
            obj_type: objType,
        };
        if (objType == 'user') {
            postData.level = $('#user_clone input[name="level"]:checked')[0].value;
            postData.confirmation = confirmation;
        };
        confirmation = false;

        $.post(addObjectUrl, postData, function(data) {
            if (data.acknowledge) {
                if (confirm(data.acknowledge)) {
                    confirmation = true;
                    document.getElementById('add-object-ctnr').click();
                    data.removeClass("error");
                }
            }
            if (data.error) {
                $('#add-object-errorlist').empty();
                // Put error message.
                console.log(data.error);
                var forms = document.getElementById('add-object-errorlist');
                forms.innerHTML = "<li><font color='red'>" + data.error +"</font></li>" + forms.innerHTML;
                $('#object-searchbox').val('');
                userPk = null;
            };
            if (data.redirect) {
                document.location.reload();
            };
            if (data.user) {
                $('#add-object-errorlist').empty();
                // Append row to user table.
                if ($('.user-table tbody')[0]) {
                    insertTablefyRow(data.user, $('.user-table tbody'));
                    event.preventDefault();
                    $('#object-searchbox').val('');
                    userPk = null;
                } else {
                    document.location.reload();
                }
            }
        }, 'json');
    });
});
