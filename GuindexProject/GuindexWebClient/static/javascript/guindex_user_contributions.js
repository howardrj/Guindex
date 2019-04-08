var g_userContributions = null;
var g_userContributionsTable = null;
var g_retrievingUserContributions = false;
var g_userContributionsTableRendered = false;

function originalbadges(A) {
	A=parseInt(A);
   var image_tag = '<img src="'
  if (A<0.5) {
     image_tag += G_URL_BASE + "/static/images/Trophy0.jpeg";
  } 
  else if (A<4.5) {
   image_tag +=G_URL_BASE + "/static/images/Trophy1.jpeg";
  }
  else if (A<9.5) {
    image_tag +=G_URL_BASE + "/static/images/Trophy5.jpeg";
  }
  else if (A<24.5) {
    image_tag +=G_URL_BASE + "/static/images/Trophy10.jpeg";
  }
  else if (A<49.5) {
   image_tag +=G_URL_BASE + "/static/images/Trophy25.jpeg";
  }
  else if (A<99.5) {
   image_tag +=G_URL_BASE + "/static/images/Trophy50.jpeg";
  }
  else {
	image_tag +=G_URL_BASE + "/static/images/Trophy100.jpeg";;}
  image_tag +='" width=35%>';
  return image_tag;
  console.log(image_tag);
}

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
    table_data.push(["Badges",       	      originalbadges(g_userContributions['originalPrices'])]);

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
