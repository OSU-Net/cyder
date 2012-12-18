function add_quicksearch(input, result_div, url) {
    input.closest('form').submit(function() {
        result_div.load(url, {quicksearch: input.val()});
        return false;
    });
}

function add_tablesorter(table) {
    var table = $(table);
    var headers = new Object();
    headers[table.find('th').length - 1] = { sorter: false};
    table.tablesorter({
        widgets: ['zebra'],
        headers: headers
    });
}

function initForms() {
    // Removes 'Hold down' helptext.
    $('.helptext:contains(' + 'Hold down "Control"' + ')').remove();

    // Form stuff.
    $('.cancel').click(function() {
        var $this = $(this);
        $('#' + $this.attr('data-formId')).slideUp();
    });
    $('.submit').click(function() {
        $(this).closest('form').submit();
    });
    $('.submit-on-change').change(function() {
        this.form.submit();
    });
}

$(document).ready(function() {
    initForms();
});
