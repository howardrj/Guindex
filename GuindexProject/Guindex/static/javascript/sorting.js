(function () {

    // Store these HTML symbols here to make code more readable
    var up_arrow   = '\u25B2'
    var down_arrow = '\u25BC'

    var guindex_table = document.getElementsById('guindex_table');

    var sortable_column_headers = guindex_table.getElementsByClassName('sortable_column_header');
       
    for (var i = 0; i < sortable_column_headers.length; i++)
    {
        sortable_column_headers[i].addEventListener('click', function () { sortRows(event); });
    }

    function sortRows (evt)
    {
        var time_stamp = false;

        if (evt.target.classList.contains('timestamp_column'))
            time_stamp = true        

        var node = evt.target;
        
        while (!node.classList.contains("projects_table"))
            node = node.parentNode;

        var table = node;
       
        // Get position of target cell in first row 
        var first_row = table.rows[0]; 

        for (var i=0; i<first_row.cells.length; i++)
        {
            if (first_row.cells[i] === evt.target.parentNode)
            {
                // Set column we want to sort by
                var column_index = i;
                break;
            }
        } 

        var table_rows_content = [];

        for (var i=0; i<table.rows.length-2; i++)
        {
            if (table.rows[i+1].cells[column_index].children.length > 0)
                table_rows_content[i] = table.rows[i+1].cells[column_index].children[0].innerHTML;
            else
                table_rows_content[i] = table.rows[i+1].cells[column_index].innerHTML;
        }

        if (time_stamp)
        {
            table_rows_content.sort(
                function(a,b)
                {
                    return Date.parse(a) - Date.parse(b);
                }
            );
        }
        else
        {
            table_rows_content.sort();
        }

        if (evt.target.innerHTML.indexOf('\u25BC') != -1)
        {
            table_rows_content.reverse(); 
            evt.target.innerHTML = evt.target.innerHTML.slice(0, evt.target.innerHTML.indexOf('\u25BC')) + ' \u25B2';
            resetOtherColumnHeaders(evt);
        }
        else if (evt.target.innerHTML.indexOf('\u25B2') != -1)
        {
            evt.target.innerHTML = evt.target.innerHTML.slice(0, evt.target.innerHTML.indexOf('\u25B2')) + ' \u25BC';
            resetOtherColumnHeaders(evt);
        }
        else
        {
            evt.target.innerHTML += '\u25BC';
            resetOtherColumnHeaders(evt);
        }

        var updated_table_rows = new Array();
        var table_rows_copy = Array.from(table.rows);

        // Loop through sorted table rows content list
        for (var i=0; i<table_rows_content.length; i++)
        {
            for (var j=0; j<table_rows_copy.length; j++)
            {
                if (table_rows_copy[j].cells[column_index].children.length > 0)
                {
                    if (table_rows_copy[j].cells[column_index].children[0].innerHTML === table_rows_content[i])
                    {
                        updated_table_rows[i] = table_rows_copy[j];
                        table_rows_copy.splice(j, 1); 
                        break;
                    }
                }
                else
                {
                    if (table_rows_copy[j].cells[column_index].innerHTML === table_rows_content[i])
                    {
                        updated_table_rows[i] = table_rows_copy[j];
                        table_rows_copy.splice(j, 1); 
                        break;
                    }
                }
            }
        }

        // Remove previous rows
        var last_row = table.rows[table.rows.length - 1];

        while(table.rows[1]) {
            table.rows[1].parentNode.removeChild(table.rows[1]);   
        }

        // Append sorted rows to table    
        for (var i=0; i<updated_table_rows.length; i++)
        {
            $('#' + table.id).append(updated_table_rows[i]);
        }

        // Append last row
        $('#' + table.id).append(last_row);

    }

    function resetOtherColumnHeaders(evt)
    {
        var node = evt.target;
        
        while (!node.classList.contains("projects_table"))
            node = node.parentNode;

        var table = node;
       
        var first_row = table.rows[0]; 

        for (var i=1; i<first_row.cells.length; i++)
        {
            if (first_row.cells[i] === evt.target.parentNode)
            {
                continue;
            }
            else if (first_row.cells[i].innerHTML.indexOf(up_arrow) != -1)
            {
                first_row.cells[i].children[0].innerHTML = first_row.cells[i].children[0].innerHTML.slice(0, first_row.cells[i].children[0].innerHTML.indexOf(' ' + up_arrow));
            }
            else if (first_row.cells[i].innerHTML.indexOf(down_arrow) != -1)
            {
                first_row.cells[i].children[0].innerHTML = first_row.cells[i].children[0].innerHTML.slice(0, first_row.cells[i].children[0].innerHTML.indexOf(' ' + down_arrow));
            }
        } 
    }

})();
