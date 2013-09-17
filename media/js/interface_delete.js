$(document).ready(function() {
    var deletes = $('.delete');
    var obj_type;
    var pk;
    deletes.each(function() {
        if(String(this).indexOf('interface') != -1) {
            if(String(this).indexOf('dynamic') != -1) {
                obj_type = 'dynamic_interface';
            } else {
                obj_type = 'static_interface';
            };
            pk = String(this)[String(this).indexOf('delete') - 2];
            url = this.href;
            this.href = '#';
            var postData = {
                pk: pk,
                obj_type: obj_type,
            };
            this.onclick = function onclick(event) {
                $.post('/dhcp/interface/interface_delete/', postData, function(data) {
                    if(data.last == true) {
                        if(confirm("Because this is the last interface on it's "
                                   + "system, deleting this interface will also "
                                   + "delete it's system. Are you sure you want "
                                   + "to continue?")) {
                            window.location.replace(url);
                        };
                    } else {
                        if(confirm('Are you sure?')) {
                            window.location.replace(url);
                        };
                    };
                }, 'json');
            };
        };
    });
});

