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
function statusChangeCallback(response) {

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
                g_username = response.name;
                g_email    = response.email;

                loginToGuindexViaFacebook(access_token);
            }
        );
    }
    else
    {
        console.log("Unknown status: " + response.status);
    }
}

function loginToGuindexViaFacebook (accessToken)
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
                // TODO How do we connect accounts?
            }
            else
            {
                // TODO How do we handle this?
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
    console.log(response);

    // access_token used by our backend for authenticating the user with Google
    var access_token = response['Zi']['access_token'];

    // TODO Are we guaranteed to have these?
    g_email = response['w3']['U3'];
    g_username = g_email.split('@')[0];

    loginToGuindexViaGoogle(access_token);
}

function loginToGuindexViaGoogle (accessToken)
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
                // We have successfully logged in
                // Get token from response JSON object

                g_loggedIn      = true;
                g_accessToken   = response['key'];
                g_userId        = response['user'];
                g_isStaffMember = response['isStaff'] == "True" ? true : false;

                onLoginSuccess('google');
            }    
            else if (request.status == 400 && response['non_field_errors'][0] === "User is already registered with this e-mail address.")
            {
                // TODO How do we connect accounts?
            }
            else
            {
                // TODO How do we handle this?
            }
        }
    } 
}

/******************/
/* Password Login */
/******************/

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

/**********/
/* Logout */
/**********/

$(document).on('click', '#logout_button', function () {

    toggleLoader(this);

    if (getAttribute(this, 'login_method') == 'facebook')
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
    else if (getAttribute(this, 'login_method') == 'password')
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
// TODO
