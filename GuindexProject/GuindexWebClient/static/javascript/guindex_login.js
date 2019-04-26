g_loginAccountInfo = null;

/******************/
/* Facebook Login */
/******************/
// Callback provided to Facebook login button
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response, connectProcedureCallback = null) {

    if (response.status === 'unknown' || response.status === 'not_authorized')
    {
        // The person is not logged into facebook or has not authorized your app 
        // Carry on as normal ...
    }
    else if (response.status === 'connected')
    {
        // User has logged into Facebook and has authorised app.
        var access_token = response['authResponse']['accessToken'];
        var user_id      = response['authResponse']['userID'];

        // Retrieve username and email through Facebook API
        FB.api(
            '/' + user_id,
            'GET',
            {fields: 'name, email'},
            function(response) {

                // Make sure connection doesn't work with any facebook account
                if (g_email != response.email & connectProcedureCallback != null)
                {
                    displayMessage("Error", "Account emails do not match. Cannot complete connection procedure.");
                    return;
                }

                g_username = response.name;
                g_email    = response.email;

                loginToGuindexViaFacebook(access_token, connectProcedureCallback);
            }
        );
    }
    else
    {
        console.log("Unknown status: " + response.status);
    }
}

function loginToGuindexViaFacebook (accessToken, connectProcedureCallback = null)
{
    // Use REST API to login to guindex.ie
    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/facebook/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify({'access_token': accessToken}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            var response = JSON.parse(request.responseText);

            if (request.status == 200)
            {
                if (!connectProcedureCallback)
                {
                    // We have successfully logged in
                    // Get token from response JSON object

                    g_loggedIn      = true;
                    g_accessToken   = response['key'];
                    g_userId        = response['user'];
                    g_isStaffMember = response['isStaff'] == "True" ? true : false;

                    onLoginSuccess('facebook');
                }
                else
                {
                    connectProcedureCallback(1, response['key']);
                }
                
            }    
            else if (request.status == 400 && response['non_field_errors'][0].startsWith("User is already registered with this email address."))
            {
                var error_message = response['non_field_errors'][0];
                var split_location = error_message.indexOf('-');
                var account_info_json_string = error_message.slice(split_location + 1).trim();

                var login_account_info = JSON.parse(account_info_json_string);
                login_account_info['account_to_connect'] = 'facebook';
                onAccountConnectRequired(login_account_info);
            }
            else
            {
                if (connectProcedureCallback)
                {
                    connectProcedureCallback(0, '');
                }
            }
        }
    } 
}

/****************/
/* Google Login */
/****************/
// This function is called by Google login button after successful access token retrieval
function onGoogleSignIn (response)
{
    // access_token used by our backend for authenticating the user with Google
    var access_token = response['Zi']['access_token'];

    // TODO Are we guaranteed to have these?
    g_email = response['w3']['U3'];
    g_username = g_email.split('@')[0];

    loginToGuindexViaGoogle(access_token);
}

function loginToGuindexViaGoogle (accessToken, connectProcedureCallback = null)
{
    // Use REST API to login to guindex.ie
    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/google/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify({'access_token': accessToken}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            var response = JSON.parse(request.responseText);

            if (request.status == 200)
            {
                if (!connectProcedureCallback)
                {
                    // We have successfully logged in
                    // Get token from response JSON object

                    g_loggedIn      = true;
                    g_accessToken   = response['key'];
                    g_userId        = response['user'];
                    g_isStaffMember = response['isStaff'] == "True" ? true : false;

                    onLoginSuccess('google');
                }
                else
                {
                    connectProcedureCallback(1, response['key']);
                }
            }    
            else if (request.status == 400 && response['non_field_errors'][0].startsWith("User is already registered with this email address."))
            {
                var error_message = response['non_field_errors'][0];
                var split_location = error_message.indexOf('-');
                var account_info_json_string = error_message.slice(split_location + 1).trim();

                var login_account_info = JSON.parse(account_info_json_string);
                login_account_info['account_to_connect'] = 'google';
                onAccountConnectRequired(login_account_info);
            }
            else
            {
                if (connectProcedureCallback)
                {
                    connectProcedureCallback(0, '');
                }
            }
        }
    } 
}

/******************/
/* Password Login */
/******************/
(function () {

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
})();

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

/*****************/
/* Login Success */
/*****************/

function onLoginSuccess (method)
{
    if (document.readyState != "complete")
    {
        var timeout = 1;

        setTimeout(function () {
            onLoginSuccess(method);
        }, timeout * 1000);

        return;
    }

    // Show pending contributions tab 
    if (g_isStaffMember)
    {
        document.getElementById('pending_contributions_li').style.display = 'list-item';
    }

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

    // Hide connect button
    document.getElementById('account_connect_nav_item').style.display = 'none';

    // Toggle log in message
    document.getElementById('logged_out_message').style.display = 'none';
    document.getElementById('logged_in_message').style.display = 'block';
    document.getElementById('logged_in_message').innerHTML = 'Logged in as <b>' + g_username + '</b>.';

    // Clean up remnants of other log in methods
    if (method != 'google')
    {
        var auth2 = gapi.auth2.getAuthInstance();

        auth2.signOut().then(function () {
        });
    }

    if (method != 'facebook')
    {
        FB.logout(function (response) {
        });
    }

    if (method != 'password')
    {
        clearLocalStorage();
    }
}

function hideLoginCards ()
{
    var login_cards = document.getElementsByClassName('login_card');

    for (var i = 0; i < login_cards.length; i++)
    {
        login_cards[i].style.display = 'none';
    }
}

/**********/
/* Logout */
/**********/

$(document).on('click', '#logout_button', function () {

    toggleLoader(this);

    if (this.getAttribute('login_method') == 'facebook')
    {
        FB.logout(function (response) {
            // Reload page (easiest thing to do here)
            location.reload();
        });
    }
    else if (this.getAttribute('login_method') == 'google')
    {
        var auth2 = gapi.auth2.getAuthInstance();

        auth2.signOut().then(function () {
            // Reload page (easiest thing to do here)
            location.reload();
        });
    }
    else if (this.getAttribute('login_method') == 'password')
    {
        clearLocalStorage();

        // Reload page (easiest thing to do here)
        location.reload();
    }
    else
    {
        // ERROR
        toggleLoader(this);
    }
});

function clearLocalStorage ()
{
    // Remove login paremeters from local storage
    localStorage.removeItem('guindexUsername');
    localStorage.removeItem('guindexAccessToken');
    localStorage.removeItem('guindexUserId');
    localStorage.removeItem('guindexIsStaffMember');
}

/********************/
/* Connect Accounts */
/********************/
function onAccountConnectRequired(loginAccountInfo)
{
    g_loginAccountInfo = loginAccountInfo;

    document.getElementById('account_connect_email').innerHTML = loginAccountInfo['email'];
    document.getElementById('account_connect_nav_item').style.display = 'block';

    document.getElementById('connect_with_facebook_card').style.display = loginAccountInfo['has_fb_login'] ? 'block' : 'none'; 
    document.getElementById('connect_with_google_card').style.display   = loginAccountInfo['has_google_login'] ? 'block' : 'none';
    document.getElementById('connect_with_password_card').style.display = loginAccountInfo['has_password_login'] ? 'block' : 'none';

    document.getElementById('account_connect_modal_link').click();
}

// Connecting with Facebook
function checkLoginStateForConnect ()
{
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response, previousMethodLoginResultCallback);
    });
}

// Connecting with Google
function onGoogleSignInForConnect (response)
{
    // Avoid this callback triggering automatically
    // g_loginAccountInfo only set when account connection is required
    if (!g_loginAccountInfo)
    {
        return;
    }

    // access_token used by our backend for authenticating the user with Google
    var access_token = response['Zi']['access_token'];

    // Make sure connection doesn't work with any google account
    if (g_email != response['w3']['U3'])
    {
        displayMessage("Error", "Account emails do not match. Cannot complete connection procedure.");
        return;
    }

    // TODO Are we guaranteed to have these?
    g_email = response['w3']['U3'];
    g_username = g_email.split('@')[0];

    loginToGuindexViaGoogle(access_token, previousMethodLoginResultCallback);
}

// Connecting with password
$(document).on('click', '#connect_with_password_button', function () {

    var email = g_loginAccountInfo['email']; 
    var password = document.getElementById('password_connect_password').value;

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
                previousMethodLoginResultCallback(1, response['key']);
            }
            else
            {
                previousMethodLoginResultCallback(0, '');
            }
        }
    }

});

function previousMethodLoginResultCallback(result, accessToken)
{
    if (result != 1)
    {
        displayMessage("Error", "Connecting accounts procedure failed");
        return;
    }

    connectAccounts(g_loginAccountInfo['account_to_connect'], accessToken);
}

function connectAccounts (accountType, accessToken) 
{
    var request = new XMLHttpRequest();

    // Use REST API to connect accounts
    if (accountType == 'facebook')
    {
        request.open('POST', G_API_BASE + 'rest-auth/facebook/connect/', true);

    }
    else if (accountType == 'google')
    {
        request.open('POST', G_API_BASE + 'rest-auth/google/connect/', true);
    }
    else
    {
        // TODO How should we handle this?
        return;
    }

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + accessToken);

    request.send(JSON.stringify({'access_token': g_loginAccountInfo['account_to_connect_access_token']}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            if (request.status == 200)
            {
                var response = JSON.parse(request.responseText);

                g_loggedIn      = true;
                g_accessToken   = response['key'];
                g_userId        = response['user'];
                g_isStaffMember = response['isStaff'] == "True" ? true : false;

                displayMessage("Info", "Succesfully connected accounts. You are now logged in as " + g_username + ".");

                // Hide connect modal
                document.getElementById('account_connect_modal_link').click();

                onLoginSuccess(accountType);
            }
            else
            {
                displayMessage("Error", "Failed to connect accounts.");
            }
        }
    }
}
