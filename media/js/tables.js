function enableEditableGrid() {
    var $eg = $('#eg');
    if (!$eg) {
        return;
    }

    // Strip links and paragraph tags, remove table cell markdown until
    // we do CellRenderers.
    $('#egtable').find('td').each(function (i, td) {
        var $td = $(td);
        $td.text($td.children()[0].innerHTML);
    });

    editableGrid = new EditableGrid("My Editable Grid");
    editableGrid.load(JSON.parse($eg.attr('data-metadata')));
    editableGrid.attachToHTMLTable('egtable');
    editableGrid.renderGrid();
}

$(document).ready(function() {
    var $enableEg = $('#enable-eg');
    $enableEg[0].reset();

    $enableEg.find('input').removeAttr('disabled').change(function() {
        $this = $(this);
        if ($this.attr('checked')) {
            enableEditableGrid();
            $this.attr('disabled', true);
        }
    });
});
