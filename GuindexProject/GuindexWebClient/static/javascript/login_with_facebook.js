// Below code is borrowed from the Facbook javascript SDK
// SDK is loaded in login_with_facebook.html

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {

    if (response.status === 'unknown')
    {
        // The person is not logged into facebook or authorized your app 
    }
    else if (response.status === 'not_authorized')
    {
        // The person is logged into facebook but has not authorized your app
    }
    else if (response.status === 'connected')
    {
        // Logged into your app and Facebook.
        var access_token = response['authResponse']['accessToken'];
        var user_id      = response['authResponse']['userID'];

        // Assign access token to global variable 
        g_facebookAccessToken = access_token;

        // Retrieve user name through facebook API
        FB.api(
            '/' + user_id,
            'GET',
            {fields: 'name, email'},
            function(response) {
                g_username = response.name;
                g_email    = response.email;
                loginToGuindex();
            }
        );
    }
}

// This function is called when someone finishes with the Login Button
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

window.fbAsyncInit = function() {

    FB.init({
        appId      : G_FACEBOOK_APP_ID,
        cookie     : true,  // enable cookies to allow the server to access 
                          // the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.8' // use graph api version 2.8
    });

    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};


// Add event listener for facebook connect button
(function () {

    document.getElementById('facebook_connect_button').addEventListener('click', function (evt) {

        var password = document.getElementById('facebook_connect_password_input').value;

        // Don't post empty password
        if (!password)
            return;

        // Change buttons to loader
        var connect_button = evt.target;
        toggleLoader(connect_button);

        // Use REST API to check password is correct
        var request = new XMLHttpRequest();

        request.open('POST', G_API_BASE + 'rest-auth/login/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'email': g_email, 'password': password}));

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4)
            {
                var response = JSON.parse(request.responseText);

                if (request.status == 200)
                {
                    g_accessToken = response['key'];

                    connectAccounts(connect_button);
                }
                else if (request.status == 400 && response['non_field_errors'][0] === "Unable to log in with provided credentials.")
                {
                    // Incorrect password
                    toggleLoader(connect_button);

                    displayMessage("Error", "Incorrect password. Try again.");
                }
            }
        }
    });

    var connectAccounts = function (connectButton)
    {
        // Use REST API to connect accounts
        var request = new XMLHttpRequest();

        request.open('POST', G_API_BASE + 'rest-auth/facebook/connect/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

        request.send(JSON.stringify({'access_token': g_facebookAccessToken}));

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4)
            {
                toggleLoader(connectButton);

                if (request.status == 200)
                {
                    var response = JSON.parse(request.responseText);

                    g_loggedIn    = true;
                    g_accessToken = response['key'];
                    g_userId      = response['user'];

                    var login_link = document.getElementById('login_link');
                    login_link.innerHTML = g_username;

                    // Hide facebook button
                    document.getElementById('facebook_login_modal_body').innerHTML = 'Logged in as ' + g_username + '.';
                    document.getElementById('login_with_facebook_button').style.display = 'none';

                    // Hide connect button and close modal
                    document.getElementById('facebook_connect_nav_item').style.display = 'none';
                    document.getElementById('facebook_connect_cancel_button').click();

                    displayMessage("Info", "Succesfully connected accounts. You are now logged in as " + g_username + ".");

                    getContributorInfo();
                    getDetailedContributorInfo();
                    getPendingContributionsInfo();

                    // Call these in a loop
                    setInterval(getContributorInfo, G_GUI_REFRESH_INTERVAL);
                    setInterval(getDetailedContributorInfo, G_GUI_REFRESH_INTERVAL);
                    setInterval(getPendingContributionsInfo, G_GUI_REFRESH_INTERVAL);
                }
                else
                {
                    displayMessage("Error", "Failed to connect accounts.");
                }
            }
        }
    }
})();

var loginToGuindex = function ()
{
    // Use REST API to login to guindex.ie
    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/facebook/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify({'access_token': g_facebookAccessToken}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            var response = JSON.parse(request.responseText);

            if (request.status == 200)
            {
                // We have successfully logged in
                // Get token from response JSON object

                g_loggedIn    = true;
                g_accessToken = response['key'];
                g_userId      = response['user'];

                var login_link = document.getElementById('login_link');
                login_link.innerHTML = g_username;

                // Hide facebook button
                document.getElementById('facebook_login_modal_body').innerHTML = 'Logged in as ' + g_username + '.';
                document.getElementById('login_with_facebook_button').style.display = 'none';

                // Get contributor info
                getContributorInfo();
                getDetailedContributorInfo();
                getPendingContributionsInfo();

                // Call these in a loop
                setInterval(getContributorInfo, G_GUI_REFRESH_INTERVAL);
                setInterval(getDetailedContributorInfo, G_GUI_REFRESH_INTERVAL);
                setInterval(getPendingContributionsInfo, G_GUI_REFRESH_INTERVAL);
            }    
            else if (request.status == 400 && response['non_field_errors'][0] === "User is already registered with this e-mail address.")
            {
                document.getElementById('facebook_email').innerHTML = g_email;
                document.getElementById('facebook_connect_nav_item').style.display = 'block';
                document.getElementById('facebook_connect_modal_link').click();
            }
        }
    } 
}
