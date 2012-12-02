function enableEditableGrid() {
    var $eg = $('#eg');
    if (!$eg) {
        return;
    }

    editableGrid = new EditableGrid("My Editable Grid");
    editableGrid.load(JSON.parse($eg.attr('data-metadata')));
    editableGrid.attachToHTMLTable('htmlgrid');
    editableGrid.renderGrid();
}

$(document).ready(function() {
    var $enableEg = $('#enable-eg');
    $enableEg.change(function() {
        $this = $(this);
        if ($this.attr('checked')) {
            enableEditableGrid();
            $this.attr('disabled', true);
        }
    });
});
