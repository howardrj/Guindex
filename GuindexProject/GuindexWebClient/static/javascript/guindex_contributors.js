var getContributorInfo = function ()
{
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

            g_isStaffMember = g_contributorsList[parseInt(g_userId)]['is_staff'];

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

        // TODO Make own row appear bold
        contributors_table_data_local.push(contributors_list[i]['username']);
        contributors_table_data_local.push(contributors_list[i]['pubsVisited'] ? contributors_list[i]['pubsVisited'] : 0);
        contributors_table_data_local.push(contributors_list[i]['currentVerifications'] ? contributors_list[i]['currentVerifications'] : 0);
        contributors_table_data_local.push(contributors_list[i]['originalVerifications'] ? contributors_list[i]['originalVerifications'] : 0);

        contributors_table_data.push(contributors_table_data_local.slice());
    } 

    $('#GuindexContributorsTable').DataTable({
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
