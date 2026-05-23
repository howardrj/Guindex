g_loginAccountInfo = null;

function guindexParseJsonResponse(responseText) {
    var raw = (responseText || "").trim();
    if (!raw) {
        return { ok: true, data: {} };
    }
    try {
        return { ok: true, data: JSON.parse(raw) };
    } catch (e) {
        return { ok: false, data: null };
    }
}

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

var g_passwordLoginBusy = false;

function submitPasswordLogin() {
    if (g_passwordLoginBusy) {
        return;
    }
    g_passwordLoginBusy = true;

    var email = document.getElementById('password_login_email').value;
    var password = document.getElementById('password_login_password').value;

    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/login/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('Accept', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify({ email: email, password: password }));

    var button = document.getElementById('password_login_button');
    toggleLoader(button);

    request.onreadystatechange = function processRequest() {
        if (request.readyState == 4) {
            g_passwordLoginBusy = false;
            toggleLoader(button);

            var parsed = guindexParseJsonResponse(request.responseText);
            if (!parsed.ok) {
                displayMessage(
                    'Error',
                    '<p>Login failed: the server did not return valid JSON (HTTP ' +
                        request.status +
                        '). Check the network tab or try again later.</p>'
                );
                return;
            }
            var response = parsed.data;

            if (request.status >= 200 && request.status < 300) {
                localStorage.setItem('guindexUsername', response['username']);
                localStorage.setItem('guindexAccessToken', response['key']);
                localStorage.setItem('guindexUserId', response['user']);
                localStorage.setItem(
                    'guindexIsStaffMember',
                    response['isStaff'] == 'True' ? true : false
                );

                g_loggedIn = true;
                g_username = localStorage.getItem('guindexUsername');
                g_accessToken = localStorage.getItem('guindexAccessToken');
                g_userId = localStorage.getItem('guindexUserId');
                g_isStaffMember = localStorage.getItem('guindexIsStaffMember');

                onLoginSuccess();
            } else {
                var error_message =
                    '<p>Please fix the following error(s): </p>';

                var error_table =
                    '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';

                error_table += '<tr> <th> Field </th> <th> Error </th> </tr>';

                Object.keys(response).forEach(function (key) {
                    error_table += '<tr>';
                    error_table += '<td>' + key + '</td>';
                    error_table += '<td>' + response[key] + '</td>';
                    error_table += '</tr>';
                });

                error_table += '</tbody></table>';

                displayMessage('Error', error_message + error_table);
            }
        }
    };
}

$(document).on('submit', '#password_login_form', function (e) {
    e.preventDefault();
    submitPasswordLogin();
});

$(document).on('click', '#password_login_button', function (e) {
    e.preventDefault();
    submitPasswordLogin();
});

function guindexCloseLoginModal()
{
    var login_close_button = document.getElementById('login_close_button');

    if (login_close_button)
    {
        login_close_button.click();
    }
    else if (typeof $ !== 'undefined')
    {
        $('#exampleModal').modal('hide');
    }
}

$(document).on('click', '#password_login_forgot_toggle', function (e) {
    e.preventDefault();
    $('#password_login_forgot_section').toggle();
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
        var pending_contributions_li = document.getElementById('pending_contributions_li');

        if (pending_contributions_li)
        {
            pending_contributions_li.style.display = 'list-item';
        }
    }

    var page_contents = document.getElementsByClassName('page_content');

    for (var i = 0; i < page_contents.length; i++)
    {
        if (typeof window.guindexDispatchEvent === 'function') {
            window.guindexDispatchEvent(page_contents[i], 'on_login');
        } else {
            page_contents[i].dispatchEvent(new Event('on_login', { bubbles: true }));
        }

        if (typeof window.guindexInitTabContent === 'function') {
            window.guindexInitTabContent(page_contents[i]);
        }
    }

    // Set login status link to display username
    var login_link = document.getElementById('login_link');
    var logout_link = document.getElementById('logout_link');
    var logout_modal_username = document.getElementById('logout_modal_username');
    var password_login_username = document.getElementById('password_login_username');
    var password_login_button = document.getElementById('password_login_button');
    var logout_button = document.getElementById('logout_button');

    if (login_link)
    {
        login_link.style.display = 'none';
    }

    if (logout_link)
    {
        logout_link.innerHTML = '<i class="fa fa-fw fa-user"></i>' + g_username;
        logout_link.style.display = 'inline';
    }

    if (logout_modal_username)
    {
        logout_modal_username.innerHTML = g_username;
    }

    if (password_login_username)
    {
        password_login_username.innerHTML = g_username;
    }

    if (password_login_button)
    {
        password_login_button.style.display = 'none';
    }

    if (logout_button)
    {
        logout_button.style.display = 'inline';
    }

    guindexCloseLoginModal();
}

/**********/
/* Signup */
/**********/

$(document).on('click', '#password_signup_button', function () {
    var email     = document.getElementById('password_signup_email').value;
    var password1 = document.getElementById('password_signup_password1').value;
    var password2 = document.getElementById('password_signup_password2').value;

    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'rest-auth/registration/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('Accept', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    // Username is optional (ACCOUNT_USERNAME_REQUIRED=False); server derives it from email.
    var signup_data = {
        'email': email,
        'password1': password1,
        'password2': password2,
    };

    request.send(JSON.stringify(signup_data));

    var button = this;
    toggleLoader(button);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            toggleLoader(button);

            var parsed = guindexParseJsonResponse(request.responseText);
            if (!parsed.ok) {
                displayMessage(
                    "Error",
                    "<p>Signup failed: the server did not return valid JSON (HTTP " +
                        request.status +
                        ").</p>"
                );
                return;
            }
            var response = parsed.data;

            if (request.status >= 200 && request.status < 300)
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
    guindexCloseLoginModal();

    displayMessage(
        'Account created',
        '<p>Your account was created. If email verification is enabled, check your inbox before logging in; otherwise you can log in now with your email and password.</p>'
    );
}

/*******************/
/* Forgot Password */
/*******************/

$(document).off('click.guindexForgotPassword', '#forgot_password_button').on(
    'click.guindexForgotPassword',
    '#forgot_password_button',
    function () {
        var emailEl = document.getElementById('forgot_password_email');
        var email = emailEl ? emailEl.value.trim() : '';
        var fbClear = document.getElementById('forgot_password_feedback');
        if (fbClear) {
            fbClear.style.display = 'none';
            fbClear.textContent = '';
            fbClear.className = 'small mt-2 mb-0';
        }
        if (!email) {
            var fb = document.getElementById('forgot_password_feedback');
            if (fb) {
                fb.style.display = 'block';
                fb.className = 'small mt-2 mb-0 text-danger';
                fb.textContent = 'Please enter your email address.';
            }
            return;
        }

        if (window.__guindexForgotPasswordPending) {
            return;
        }
        window.__guindexForgotPasswordPending = true;

        var request = new XMLHttpRequest();
        request.open('POST', G_API_BASE + 'rest-auth/password/reset/', true);
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('Accept', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        var forgot_password_data = {
            'email': email
        };

        var button = this;
        button.disabled = true;
        request.send(JSON.stringify(forgot_password_data));
        toggleLoader(button);

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState !== 4) {
                return;
            }

            window.__guindexForgotPasswordPending = false;
            button.disabled = false;
            toggleLoader(button);

            var parsed = guindexParseJsonResponse(request.responseText);
            if (!parsed.ok) {
                var fbErr = document.getElementById('forgot_password_feedback');
                if (fbErr) {
                    fbErr.style.display = 'block';
                    fbErr.className = 'small mt-2 mb-0 text-danger';
                    fbErr.textContent =
                        'Something went wrong (HTTP ' + request.status + '). Try again later.';
                }
                displayMessage(
                    "Error",
                    "<p>Password reset request failed: the server did not return JSON (HTTP " +
                        request.status +
                        "). This often means a server error or proxy page — check server logs and email configuration.</p>"
                );
                return;
            }
            var response = parsed.data;

            if (request.status >= 200 && request.status < 300)
            {
                onForgotPasswordSubmitSuccess();
            }
            else
            {
                displayMessage("Error", guindexFormatRestValidationErrors(response));
                var fbBad = document.getElementById('forgot_password_feedback');
                if (fbBad) {
                    fbBad.style.display = 'block';
                    fbBad.className = 'small mt-2 mb-0 text-danger';
                    fbBad.textContent = 'Could not send reset email. See the message above.';
                }
            }
        };
    }
);

function onForgotPasswordSubmitSuccess ()
{
    var fb = document.getElementById('forgot_password_feedback');
    if (fb) {
        fb.style.display = 'block';
        fb.className = 'small mt-2 mb-0 text-success';
        fb.innerHTML =
            '<strong>Check your email.</strong> If an account exists for that address, we sent a link to choose a new password. ' +
            'Also check your spam folder. You can close this window when you are done.';
    }

    displayMessage(
        'Password reset',
        '<p>If that email is registered with Guindex, we sent a reset link. Check your inbox and spam folder.</p>'
    );

    setTimeout(function () {
        var closeBtn = document.getElementById('login_close_button');
        if (closeBtn) {
            closeBtn.click();
        }
    }, 2500);
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
