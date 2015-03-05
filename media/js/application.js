function add_quicksearch(input, result_div, url) {
    input.closest('form').submit(function() {
        result_div.load(url, {quicksearch: input.val()});
        return false;
    });
}

function add_tablesorter(table) {
    var table = $(table);
    var headers = {};
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
        $('#' + $this.attr('data-formId')).slideUp('fast', 'easeOutExpo');
    });
    $('.submit').click(function() {
        $(this).closest('form').submit();
    });
    $('.submit-on-change').change(function() {
        this.form.submit();
    });
    $('#obj-form form :input:visible:last').on( 'keypress', function(e) {
        if (e.keyCode == 13) {
            $('.js-submit').focus().click();
        }
    });
}

function slideUp($e) {
    $e.slideUp(200, 'easeOutExpo');
}


function slideDown($e) {
    $e.slideDown(500, 'easeOutExpo');
}

$(document).ready(function() {
    initForms();
});
