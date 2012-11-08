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

$(document).ready(function() {
    $('input, select').mouseover(function(){
        $(this).next('span.helptext').toggle();
    }).mouseout(function() {
        $(this).next('span.helptext').toggle();
    });

    $('.submit-on-change').change(function() {
        this.form.submit();
    });
});
