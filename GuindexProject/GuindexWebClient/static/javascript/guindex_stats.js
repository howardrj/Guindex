var getStats = function ()
{
    g_stats = {};

    // Function to get detailed info about this user using REST API
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'statistics/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            g_stats = JSON.parse(request.responseText)[0];
            populateStatsTable();
            populatePriceTable();
        }
    }
}

var populateStatsTable = function ()
{
    var table_data = [];

    var last_calculated               = new Date(g_stats['lastCalculated']).toString().split(' ');
    var last_calculated_pretty_format = last_calculated[0] + ' ' + last_calculated[2] + ' ' + last_calculated[1] + ' ' + last_calculated[3] + ' ' + last_calculated[4];

    table_data.push(["Number of Pubs in Database",          g_stats['pubsInDb']]);
    table_data.push(["Percentage Visited",                  g_stats['percentageVisited'] + '%']);
    table_data.push(["Average Price",                       "\u20AC" + g_stats['averagePrice']]);
    table_data.push(["Standard Deviation",                  "\u20AC" + g_stats['standardDeviation']]);
    table_data.push(["Number of Closed Pubs",               g_stats['closedPubs']]);
    table_data.push(["Number of Pubs not Serving Guinness", g_stats['notServingGuinness']]);
    table_data.push(["Last Calculated",                     last_calculated_pretty_format]);
    table_data.push(["Number of Users",                     g_stats['numUsers']]);

    // Check if table is being drawn from scratch or refreshed
    if (!g_guindexStatsTable)
    {
        data_columns = [
            {title: "Statistic", "orderable": false},
            {title: "Value",     "orderable": false},
        ]

        g_guindexStatsTable = $('#GuindexStatisticsTable').DataTable({
                                    responsive: true,
                                    data: table_data,
                                    columns: data_columns,
                                    paging: false,
                                });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_guindexStatsTable.clear().draw();
        g_guindexStatsTable.rows.add(table_data);
        g_guindexStatsTable.columns.adjust().draw();
    }
}

var populatePriceTable = function ()
{
    var table_data = [];

    for (var i = 0; i < g_stats['pubsWithPrices'].length; i++)
    {
        table_data.push([
            g_stats['pubsWithPrices'][i]['name'],
            g_stats['pubsWithPrices'][i]['county'],
            g_stats['pubsWithPrices'][i]['price'],
        ]);
    }

    // Check if table is being drawn from scratch or refreshed
    if (!g_guindexPriceTable)
    {
        data_columns = [
            {title: "Pub Name", "orderable": false},
            {title: "County",   "orderable": false},
            {title: "Price (€)"},
        ]

        g_guindexPriceTable = $('#GuindexPriceTable').DataTable({
                                    responsive: true,
                                    data: table_data,
                                    columns: data_columns,
                                    "order": [[ 2, "desc" ]]
                                });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_guindexPriceTable.clear().draw();
        g_guindexPriceTable.rows.add(table_data);
        g_guindexPriceTable.columns.adjust().draw();
    }
}
