function insertTablefyRow(tablefy, tbody) {
    /* Takes a tablefy object and treats it as a row to insert to specified
     * table.
     */
    for (row in tablefy.data) {
        var row = tablefy.data[row];
        var newRow = $('<tr></tr>');

        for (col in row) {
            var col = row[col];
            var newCol = $('<td></td>');

            if (col.url) {
                // Make link if has url.
                var newLink = $('<a></a>');
                newLink.attr('href', col.url);
                newLink.text(col.value);
                newCol.append(newLink);
            } else {
                newCol.text(col.value);
            }
            newRow.append(newCol);
        }
        // Add row to table.
        tbody.append(newRow);
    }
}
