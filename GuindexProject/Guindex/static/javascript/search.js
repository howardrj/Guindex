(function () {

    var search_bar = document.getElementById('pubs_search_bar');

    search_bar.addEventListener('input', function (evt) { filterTable(evt); });

    var filterTable = function(evt)
    {
        var table = document.getElementById('guindex_table'); 

        var table_rows = table.rows;

        var count_hidden_rows = 0;

        for (var i = 1; i < table_rows.length - 1; i++)
        { 
            // Do case insensitive search
            var pub_name = table_rows[i].getElementsByClassName('payload')[0].innerHTML.toLowerCase();

            if (pub_name.indexOf(evt.target.value.toLowerCase()) == -1)
            {
                table_rows[i].style.display = "none";

                count_hidden_rows++;
            }
            else
            {
                table_rows[i].style.display = "";
            }
        }

        var last_row = document.getElementById('guindex_table_last_row');

        if (count_hidden_rows === table_rows.length - 2)
        {
            last_row.style.display = ""        
            
        }
        else if (table_rows.length >= 3)
        {
            last_row.style.display = "none"        
        }
    }

})();
