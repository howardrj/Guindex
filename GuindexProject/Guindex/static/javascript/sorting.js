(function () {

    // NB: This code is a mess but it works
    // Edit at your peril

    // Store these HTML symbols here to make code more readable
    var UP_ARROW   = '\u25B2'
    var DOWN_ARROW = '\u25BC'

    var sortable_column_headers = document.getElementsByClassName('sortable_column_header');
       
    for (var i = 0; i < sortable_column_headers.length; i++)
    {
        sortable_column_headers[i].addEventListener('click', function () { sortRows(event); });
    }

    function sortRows(evt)
    {
        // Find corresponding table
        var node = evt.target;

        while (!node.classList.contains('guindex_table'))
            node = node.parentNode;

        var table = node;
        
        var time_stamp = false;

        if (evt.target.classList.contains('timestamp_column'))
            time_stamp = true        

        // Get position of target cell in first row 
        var first_row = table.rows[0]; 

        for (var i = 0; i < first_row.cells.length; i++)
        {
            if (first_row.cells[i].children[0] === evt.target)
            {
                // Set column we want to sort by
                column_index = i;
                break;
            }
        } 

        // Loop through all rows of this column and get content payload
        var table_rows_content = [];

        for (var i = 0; i < table.rows.length - 2; i++)
        {
            table_rows_content[i] = table.rows[i + 1].cells[column_index].getElementsByClassName('payload')[0].innerHTML;
        }

        // Remove any TBD content and append it after sort (not interesting to have at top. Always put it at the end)
        var tbd_content = []
        var indices_to_remove = []
        for (var i = 0; i < table_rows_content.length; i++)
        {
            if (table_rows_content[i].indexOf("TBD") != -1)
            {
                tbd_content.push(table_rows_content[i]);
                indices_to_remove.push(i);
            }
        }

        for (var i = indices_to_remove.length - 1; i >= 0; i--)
            table_rows_content.splice(indices_to_remove[i], 1);
        
        // Sort table_rows_content array
        if (time_stamp)
        {
            table_rows_content.sort(
                function(a, b)
                {
                    return Date.parse(a) - Date.parse(b);
                }
            );
        }
        else
        {
            table_rows_content.sort();
        }

        if (evt.target.innerHTML.indexOf(DOWN_ARROW) != -1) // Column is in descending order
        {
            table_rows_content.reverse(); 
            evt.target.innerHTML = evt.target.innerHTML.slice(0, evt.target.innerHTML.indexOf(DOWN_ARROW)) + ' ' + UP_ARROW;
            resetOtherColumnHeaders(evt, table);
        }
        else if (evt.target.innerHTML.indexOf(UP_ARROW) != -1) // Column is in ascending order
        {
            evt.target.innerHTML = evt.target.innerHTML.slice(0, evt.target.innerHTML.indexOf(UP_ARROW)) + ' ' + DOWN_ARROW;
            resetOtherColumnHeaders(evt, table);
        }
        else // Column is not ordered
        {
            evt.target.innerHTML += ' ' + DOWN_ARROW;
            resetOtherColumnHeaders(evt, table);
        }

        // Append TBD content
        for (var i = 0; i < tbd_content.length; i++)
        {
            table_rows_content.push(tbd_content[i]);
        }

        var updated_table_rows = new Array(); // Array to store new table rows
        var table_rows_copy = Array.from(table.rows); // Create copy of current table rows

        // Loop through sorted table rows content list
        // Get row from table that matches current index and append to updated_table_rows array
        // updated_table_rows will then be sorted
        for (var i = 0; i < table_rows_content.length; i++)
        {
            for (var j = 1; j < table_rows_copy.length - 1; j++) // Skip first and last rows
            {
                if (table_rows_copy[j].cells[column_index].getElementsByClassName('payload')[0].innerHTML === table_rows_content[i])
                {
                    updated_table_rows[i] = table_rows_copy[j];
                    table_rows_copy.splice(j, 1); 
                    break;
                }
            }
        }

        // Remove previous rows
        var last_row = table.rows[table.rows.length - 1];

        while(table.rows[1]) {
            table.rows[1].parentNode.removeChild(table.rows[1]);   
        }

        // Append sorted rows to table    
        for (var i = 0; i < updated_table_rows.length; i++)
        {
            $('#' + table.id).append(updated_table_rows[i]);
        }

        // Append last row
        $('#' + table.id).append(last_row);
    }

    function resetOtherColumnHeaders(evt, table)
    {
        var first_row = table.rows[0]; 

        for (var i = 0; i < first_row.cells.length; i++)
        {
            if (first_row.cells[i].children[0] === evt.target)
            {
                continue;
            }
            else if (first_row.cells[i].innerHTML.indexOf(UP_ARROW) != -1)
            {
                first_row.cells[i].children[0].innerHTML = first_row.cells[i].children[0].innerHTML.slice(0, first_row.cells[i].children[0].innerHTML.indexOf(' ' + UP_ARROW));
            }
            else if (first_row.cells[i].innerHTML.indexOf(DOWN_ARROW) != -1)
            {
                first_row.cells[i].children[0].innerHTML = first_row.cells[i].children[0].innerHTML.slice(0, first_row.cells[i].children[0].innerHTML.indexOf(' ' + DOWN_ARROW));
            }
        } 
    }

})();
