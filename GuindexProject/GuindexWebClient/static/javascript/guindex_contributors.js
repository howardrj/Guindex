var getContributorInfo = function ()
{
    // Clear contributors list
    g_contributorsList = [];

    // Use REST API to get contributor information list
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'contributors/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    request.send(JSON.stringify({'access_token': g_facebookAccessToken}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            g_contributorsList = JSON.parse(request.responseText); 

            populateContributorsTable();            
        }
    }
}

var populateContributorsTable = function ()
{
    // Copy global list
    var contributors_list = g_contributorsList.slice();

    // Sort alphabetically
    contributors_list.sort(function(a, b) {
        return a['username'].localeCompare(b['username']);
    });

    var contributors_table_data = [];

    for (var i = 0; i < contributors_list.length; i++)
    {
        var contributors_table_data_local = [];

        var username               = contributors_list[i]['username'];
        var pubs_visited           = contributors_list[i]['pubsVisited'] ? contributors_list[i]['pubsVisited'] : 0;
        var current_verifications  = contributors_list[i]['currentVerifications'] ? contributors_list[i]['currentVerifications'] : 0;
        var original_verifications = contributors_list[i]['originalVerifications'] ? contributors_list[i]['originalVerifications'] : 0;

        // Make own row appear bold
        if (contributors_list[i]['id'] == g_userId)
        {
            contributors_table_data_local.push('<em>' + username + '</em>');
            contributors_table_data_local.push('<em>' + pubs_visited + '</em>');
            contributors_table_data_local.push('<em>' + current_verifications + '</em>');
            contributors_table_data_local.push('<em>' + original_verifications + '</em>');
        }
        else
        {
            contributors_table_data_local.push(username);
            contributors_table_data_local.push(pubs_visited);
            contributors_table_data_local.push(current_verifications);
            contributors_table_data_local.push(original_verifications);
        }

        contributors_table_data.push(contributors_table_data_local.slice());
    } 

    // Check if table is being drawn from scratch or refreshed
    if (!g_contributorsTable)
    {
       g_contributorsTable = $('#GuindexContributorsTable').DataTable({
                                responsive: true,
                                data: contributors_table_data,
                                columns: [
                                    { title: "Username" },
                                    { title: "Pubs Visited" },
                                    { title: "Current Verifications" },
                                    { title: "Original Verifications" },
                                ]
                             });
    }
    else
    {
        // Redraw table
        g_contributorsTable.clear().draw();
        g_contributorsTable.rows.add(contributors_table_data);
        g_contributorsTable.columns.adjust().draw();
    }
}
