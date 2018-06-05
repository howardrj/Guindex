var getContributorInfo = function ()
{
    // Clear contributors list
    g_contributorsList = [];

    if (g_isStaffMember == null) // Has not been set yet
    {
        setTimeout(getContributorInfo, 1000);
        return;
    }

    if (g_isStaffMember == false)
        return;

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
        }
    }
}
