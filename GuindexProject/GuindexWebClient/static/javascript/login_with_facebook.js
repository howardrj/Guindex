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
        var username     = null;

        // Retrieve user name through facebook API
        FB.api(
            '/' + user_id,
            'GET',
            {},
            function(response) {
                username = response.name;
            }
        );

        // Use REST API to login to guindex.ie
        var request = new XMLHttpRequest();

        request.open('POST', G_API_BASE + 'rest-auth/facebook/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'access_token': access_token}));

        // Pull in contributins widgets once user is authenticated
        // and display log out button
        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                // We have successfully logged in
                // Get token from response JSON object
                var response = JSON.parse(request.responseText);

                g_loggedIn = true;
                g_accessToken = response['key'];

                var login_link = document.getElementById('login_link');
                login_link.innerHTML = username;

                // Hide facebook button
                document.getElementById('facebook_login_modal_body').innerHTML = 'Logged in as ' + username + '.';
                document.getElementById('login_with_facebook_button').style.display = 'none';
            }
        }
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
        appId      : '940061452839208',
        cookie     : true,  // enable cookies to allow the server to access 
                          // the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.8' // use graph api version 2.8
    });

    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};
