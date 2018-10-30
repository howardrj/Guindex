var g_userContributions = null;
var g_userContributionsTable = null;
var g_retrievingUserContributions = false;
var g_userContributionsTableRendered = false;

// Can only be called if user is logged in
function populateUserContributionsTable ()
{
    if (g_loggedIn)
    {
        var contributions_page = document.getElementById('contributions_page');

        contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';
    }
    else
    {
        return;
    }

    if (g_userContributionsTableRendered)
        return;

    function getUserContributions (callback)
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

                if (callback)
                    callback();
            }
        }
    }

    if (g_userContributions == null)
    {
        getUserContributions(populateUserContributionsTable);
        return;
    }

    var table_data = [];

    table_data.push(["Pubs Visited",          g_userContributions['pubsVisited']]);
    table_data.push(["Current Verifications", g_userContributions['currentVerifications']]);
    table_data.push(["Original Prices",       g_userContributions['originalPrices']]);
    table_data.push(["Trophies",       	      if (parseFloat(g_userContributions['originalPrices'])==0)
							{trophy="None";}
				       	      else if (parseFloat(g_userContributions['originalPrices'])<4.5)
							{trophy="1PubTrophy";}
			 		      else if (4.5<parseFloat(g_userContributions['originalPrices'])<9.5)
							{trophy="5PubTrophy";}
					      else if (9.5<parseFloat(g_userContributions['originalPrices'])<24.5)
							{trophy="10PubTrophy";}
					      else if (24.5<parseFloat(g_userContributions['originalPrices'])<49.5)
							{trophy="25PubTrophy";}
					      else if (49.5<parseFloat(g_userContributions['originalPrices'])<99.5)
							{trophy="50PubTrophy";}
					      else (parseFloat(g_userContributions['originalPrices'])>99.5)
							{trophy="100PubTrophy";}
						
					      trophy]);     

    // Check if table is being drawn from scratch or refreshed
    if (!g_userContributionsTable)
    {
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

    g_userContributionsTableRendered = true;
}
