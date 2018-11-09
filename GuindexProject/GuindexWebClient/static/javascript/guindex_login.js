// Below code is borrowed from the Facbook javascript SDK
// SDK is loaded in login_with_facebook.html

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {

    if (response.status === 'unknown' || response.status === 'not_authorized')
    {
        // The person is not logged into facebook or authorized your app 

        // Need all four parameters
        if (localStorage.hasOwnProperty('guindexUsername') &&
            localStorage.hasOwnProperty('guindexAccessToken') &&
            localStorage.hasOwnProperty('guindexUserId') &&
            localStorage.hasOwnProperty('guindexIsStaffMember'))
        {
            g_loggedIn      = true;
            g_username      = localStorage.getItem('guindexUsername');
            g_accessToken   = localStorage.getItem('guindexAccessToken');
            g_userId        = localStorage.getItem('guindexUserId');
            g_isStaffMember = localStorage.getItem('guindexIsStaffMember');

            onLoginSuccess('password');
        }
        else
        {
            // Remove login paremeters from local storage to be safe
            localStorage.removeItem('guindexUsername');
            localStorage.removeItem('guindexAccessToken');
            localStorage.removeItem('guindexUserId');
            localStorage.removeItem('guindexIsStaffMember');

            // Carry on as normal ...
        }
    }
    else if (response.status === 'connected')
    {
        // N.B: Facebook takes precedence
        // If user is connected, log them in using Facebook credentials
        // Only give user the option of logging in with password if
        // not connected via Facebook
        // If this an inconvenience for some users we can change the logic accordingly.

        // Logged into Facebook and user has authorised app.
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

                loginToGuindexViaFacebook();
            }
        );
    }
    else
    {
        console.log("Unknown status: " + response.status);
    }
}

// This function is called when someone finishes with the Login Button
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

var loginToGuindexViaFacebook = function ()
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

                g_loggedIn      = true;
                g_accessToken   = response['key'];
                g_userId        = response['user'];
                g_isStaffMember = response['isStaff'] == "True" ? true : false;

                onLoginSuccess('facebook');
            }    
            else if (request.status == 400 && response['non_field_errors'][0] === "User is already registered with this e-mail address.")
            {
                document.getElementById('facebook_connect_email').innerHTML = g_email;
                document.getElementById('facebook_connect_nav_item').style.display = 'block';
                document.getElementById('facebook_connect_modal_link').click();
            }
            else
            {
                // TODO How do we handle this?
            }
        }
    } 
}

// Add event listener for facebook connect button
$(document).on('click', '#facebook_connect_button', function () {

    var password = document.getElementById('facebook_connect_password_input').value;

    // Don't post empty password
    if (!password)
        return;

    var connect_button = this;
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
            else
            {
                // TODO How do we handle this?
            } 
        }
    }

    function connectAccounts (connectButton)
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

                    displayMessage("Info", "Succesfully connected accounts. You are now logged in as " + g_username + ".");

                    // Hide connect button and close modal
                    document.getElementById('facebook_connect_nav_item').style.display = 'none';
                    document.getElementById('facebook_connect_cancel_button').click();

                    onLoginSuccess('facebook');
                }
                else
                {
                    displayMessage("Error", "Failed to connect accounts.");
                }
            }
        }
    }
});

// Add event listeners for login via password button
$(document).on('click', '#password_login_button', function () {
    
    var email    = document.getElementById('password_login_email').value;
    var password = document.getElementById('password_login_password').value;

    // Use REST API to login to guindex.ie
    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/login/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify({'email': email, 'password': password}));

    var button = this;
    toggleLoader(button);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            toggleLoader(button);

            var response = JSON.parse(request.responseText);

            if (request.status == 200)
            {
                localStorage.setItem('guindexUsername',      response['username']);
                localStorage.setItem('guindexAccessToken',   response['key']);
                localStorage.setItem('guindexUserId',        response['user']);
                localStorage.setItem('guindexIsStaffMember', response['isStaff'] == "True" ? true : false);

                // Do login stuff
                g_loggedIn      = true;
                g_username      = localStorage.getItem('guindexUsername');
                g_accessToken   = localStorage.getItem('guindexAccessToken');
                g_userId        = localStorage.getItem('guindexUserId');
                g_isStaffMember = localStorage.getItem('guindexIsStaffMember');

                onLoginSuccess('password');
            }
            else
            {
                // Display errors
                var error_message = '<p>Please fix the following error(s): </p>'

                var error_table = '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';

                error_table += '<tr> <th> Field </th> <th> Error </th> </tr>';

                Object.keys(response).forEach(function(key) {

                    error_table += '<tr>';

                    error_table += '<td>' + key + '</td>';

                    error_table += '<td>' + response[key] + '</td>';

                    error_table += '</tr>';
                });

                error_table += '</tbody></table>';

                displayMessage("Error", error_message + error_table);
            }
        }
    }
});

// Add event listener for logout button
$(document).on('click', '#logout_button', function () {

    toggleLoader(this);

    if (getAttribute(this, 'login_method') == 'password')
    {
        // Remove login paremeters from local storage
        localStorage.removeItem('guindexUsername');
        localStorage.removeItem('guindexAccessToken');
        localStorage.removeItem('guindexUserId');
        localStorage.removeItem('guindexIsStaffMember');

        // Reload page (easiest thing to do here)
        location.reload();
    }
    else if (getAttribute(this, 'login_method') == 'facebook')
    {
        FB.logout(function (response) {
            // Reload page (easiest thing to do here)
            location.reload();
        });
    }
    else if (getAttribute(this, 'login_method') == 'google')
    {
        var auth2 = gapi.auth2.getAuthInstance();

        auth2.signOut().then(function () {
            // Reload page (easiest thing to do here)
            location.reload();
        });
    }
    else
    {
        // ERROR
        toggleLoader(this);
    }
});

function onLoginSuccess (method)
{
    // Show pending contributions tab 
    if (g_isStaffMember)
        document.getElementById('pending_contributions_li').style.display = 'list-item';

    var page_contents = document.getElementsByClassName('page_content');

    for (var i = 0; i < page_contents.length; i++)
    {
        page_contents[i].dispatchEvent(new Event('on_login'));
    }

    // Set login status link to display username
    var login_link = document.getElementById('login_link');
    login_link.innerHTML = g_username;

    // Display logout button
    document.getElementById('logout_button').style.display = 'inline';
    document.getElementById('logout_button').setAttribute('login_method', method);

    hideLoginCards();

    // Toggle log in message
    document.getElementById('logged_out_message').style.display = 'none';
    document.getElementById('logged_in_message').style.display = 'block';
    document.getElementById('logged_in_message').innerHTML = 'Logged in as <b>' + g_username + '</b>.';
}

function hideLoginCards ()
{
    var login_cards = document.getElementsByClassName('login_card');

    for (var i = 0; i < login_cards.length; i++)
    {
        login_cards[i].style.display = 'none';
    }
}
