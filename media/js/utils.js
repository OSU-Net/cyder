function insertTablefyRow(tablefy, tbody) {
    /* Takes a tablefy object and treats it as a row to insert to specified
     * table.
     */
    for (row in tablefy.data) {
        var row = tablefy.data[row];
        var newRow = $('<tr></tr>');

        for (col in row) {
            var col = row[col];
            var newCol = $('<td>');
            if (col.url) {
                for (i in col.value) {
                    if (col.url[i] == '') {
                        newCol.text(col.value[i]);
                    } else {
                        if (col.img) {
                            if (col.img[i] == '') {
                                var newLink = $('<a>' + col.value[i] + '</a>');
                            } else {
                                var newLink = $('<a><img src=' + col.img[i] + '></a>');
                            }
                        } else {
                            var newLink = $('<a>' + col.value[i] + '</a>');
                        }
                        newLink.attr('href', col.url[i]);
                        newCol.append(newLink);
                    }
                }
            } else {
                newCol.text(col.value);
            }
            newCol.append('</td>');
            newRow.append(newCol);
        }
        // Add row to table.
        tbody.prepend(newRow);
    }
}

function make_smart_name(elements, domains, append) {
    // Autocomplete domains.
    $(elements).autocomplete({
        focus: function(event, ui) {
            // Save matching part to ui.item.value.
            var name = elements.val();

            if (!append) {
                elements.attr('value', ui.item.label);
            } else if (ui.item.value !== '') {
                var foo = name.substring(0, name.lastIndexOf(ui.item.value));
                elements.attr('value', foo + ui.item.label);
            } else {
                if (name.lastIndexOf('.') == name.length - 1) {
                    elements.attr('value',  name + ui.item.label);
                } else {
                    elements.attr('value',  name + '.' + ui.item.label);
                }
            }
            return false;
        },
        select: function(event, ui) {
            return false;
        },
        autoFocus: false,
        source: function (li, callback) {
            var labels = li.term.split('.')
            var suggested_domains = [];
            var domain_name = '';
            var search_name = '';

            while (labels) {
                search_name = labels.join('.');
                for (var domain in domains.sort(function(a,b) { return (a.length < b.length) ? 0 : 1; })) {
                    domain_name = domains[domain];
                    if (domain_name.indexOf(search_name) == 0) {
                        suggested_domains.push({label: domain_name, value: search_name});
                    }
                }
                if (suggested_domains.length === 0) {
                    labels.shift();
                } else {
                    return callback(suggested_domains.slice(0, 20));
                }
            }
            return callback([]);
        }
    });
}


function make_smart_name_get_domains(element, append, domainsUrl){
    $.get(domainsUrl, function(domains) {
        make_smart_name(element, $.parseJSON(domains), append);
    });
}


function clear_form_all(form) {
    $('.errorlist').empty();

    for (i = 0; i < form.length; i++) {
        field_type = form[i].type.toLowerCase();
        switch (field_type) {
            case "text":
            case "password":
            case "textarea":
            case "hidden":
                form[i].value = "";
                break;
            case "radio":
            case "checkbox":
                if (form[i].checked) {
                    form[i].checked = false;
                }
                break;
            default:
                break;
        }
    }
}
