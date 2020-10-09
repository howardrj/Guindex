g_loginAccountInfo = null;

/*********/
/* Login */
/*********/
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

        onLoginSuccess();
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

                onLoginSuccess();
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

function onLoginSuccess ()
{
    if (document.readyState != "complete")
    {
        var timeout = 1;

        setTimeout(function () {
            onLoginSuccess();
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
    var logout_link = document.getElementById('logout_link');
    var logout_modal_username = document.getElementById('logout_modal_username');

    login_link.style.display = 'none';
    logout_link.innerHTML = g_username;
    logout_link.style.display = 'inline';
    logout_modal_username.innerHTML = g_username;

    document.getElementById('login_close_button').click();
}

/**********/
/* Signup */
/**********/

$(document).on('click', '#password_signup_button', function () {
    
    var username  = document.getElementById('password_signup_username').value;
    var email     = document.getElementById('password_signup_email').value;
    var password1 = document.getElementById('password_signup_password1').value;
    var password2 = document.getElementById('password_signup_password2').value;

    // Use REST API to login to guindex.ie
    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/registration/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    var signup_data = {
        'username': username,
        'email': email,
        'password1': password1,
        'password2': password2,
    }

    request.send(JSON.stringify(signup_data));

    var button = this;
    toggleLoader(button);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            toggleLoader(button);

            var response = JSON.parse(request.responseText);

            if (request.status == 201)
            {
                onSignupSuccess();
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

function onSignupSuccess ()
{
    document.getElementById('login_close_button').click();

    displayMessage('Account Verificatiom Email Sent', 
                   "Please check your email and verify your account before logging in");
}

/**********/
/* Logout */
/**********/

$(document).on('click', '#logout_button', function () {

    toggleLoader(this);

    clearLocalStorage();

    // Reload page (easiest thing to do here)
    location.reload();
});

function clearLocalStorage ()
{
    // Remove login paremeters from local storage
    localStorage.removeItem('guindexUsername');
    localStorage.removeItem('guindexAccessToken');
    localStorage.removeItem('guindexUserId');
    localStorage.removeItem('guindexIsStaffMember');
}
