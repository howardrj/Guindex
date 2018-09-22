var g_userContributions = null;
var g_userContributionsTable = null;
var g_retrievingUserContributions = false;

// Can only be called if user is logged in
function populateUserContributionsTable ()
{
    function getUserContributions ()
    {
        if (g_retrievingUserContributions)
            return;
        
        g_userContributions = null;

        // Function to get detailed info about this user using REST API
        var request = new XMLHttpRequest();

        request.open('GET', G_API_BASE + 'contributors/' + g_userId + '/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

        request.send(null);

        g_retrievingUserContributions = true;

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                g_userContributions = JSON.parse(request.responseText);
                g_retrievingUserContributions = false;
            }
        }
    }

    getUserContributions();

    if (g_userContributions == null)
    {
        getUserContributions();
        setTimeout(populateUserContributionsTable, 1000);
        return;
    }

    var table_data = [];

    table_data.push(["Pubs Visited",          g_userContributions['pubsVisited']]);
    table_data.push(["Current Verifications", g_userContributions['currentVerifications']]);
    table_data.push(["Original Prices",       g_userContributions['originalPrices']]);

    // Check if table is being drawn from scratch or refreshed
    if (!g_userContributionsTable)
    {

        var contributions_page = document.getElementById('contributions_page');

        contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        data_columns = [
            {title: "Statistic", "orderable": false},
            {title: "Value",     "orderable": false},
        ]

        g_userContributionsTable = $('#GuindexContributionsTable').DataTable({
                                       responsive: true,
                                       data: table_data,
                                       columns: data_columns,
                                       "paging": false,
                                       "ordering": false,
                                       "searching": false,
                                   });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_userContributionsTable.clear().draw();
        g_userContributionsTable.rows.add(table_data);
        g_userContributionsTable.columns.adjust().draw();
    }
}
