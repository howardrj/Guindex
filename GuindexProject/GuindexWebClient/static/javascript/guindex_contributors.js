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
        var original_verifications = contributors_list[i]['originalPrices'] ? contributors_list[i]['originalPrices'] : 0;

        // Make own row appear bold
        if (contributors_list[i]['id'] == g_userId)
        {
            contributors_table_data_local.push('<em>' + username + '</em>');
        }
        else
        {
            contributors_table_data_local.push(username);
        }

        contributors_table_data_local.push(pubs_visited);
        contributors_table_data_local.push(current_verifications);
        contributors_table_data_local.push(original_verifications);

        contributors_table_data.push(contributors_table_data_local.slice());
    } 

    // Check if table is being drawn from scratch or refreshed
    if (!g_contributorsTable)
    {
       // Clear log in warning
       var contributors_page = document.getElementById('contributors_page');

       contributors_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
       contributors_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

       g_contributorsTable = $('#GuindexContributorsTable').DataTable({
                                responsive: true,
                                data: contributors_table_data,
                                columns: [
                                    { title: "Username" },
                                    { title: "Pubs Visited", "type": "num"},
                                    { title: "Current Verifications", "type": "num" },
                                    { title: "Original Verifications", "type": "num" },
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
