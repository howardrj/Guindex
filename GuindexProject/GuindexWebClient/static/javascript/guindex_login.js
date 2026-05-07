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

/** HTML-escape plain text for safe insertion into modal HTML */
function guindexEscapeHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Format DRF / dj-rest-auth validation payloads (strings, arrays, detail-only).
 */
function guindexFormatRestValidationErrors(response) {
    if (response == null || typeof response !== 'object') {
        return '<p>' + guindexEscapeHtml(String(response != null ? response : 'Unknown error')) + '</p>';
    }
    var keys = Object.keys(response);
    if (keys.length === 0) {
        return '<p>Unknown error.</p>';
    }
    var errorTable =
        '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';
    errorTable += '<tr> <th> Field </th> <th> Error </th> </tr>';
    keys.forEach(function (key) {
        var val = response[key];
        var cell;
        if (val == null) {
            cell = '';
        } else if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean') {
            cell = guindexEscapeHtml(String(val));
        } else {
            cell = guindexEscapeHtml(JSON.stringify(val));
        }
        errorTable += '<tr><td>' + guindexEscapeHtml(key) + '</td><td>' + cell + '</td></tr>';
    });
    errorTable += '</tbody></table>';
    return '<p>Please fix the following error(s): </p>' + errorTable;
}

/** Never treat the literal strings "undefined" / "null" or blank as a valid display name */
function guindexSanitizeDisplayName(v) {
    if (v == null) {
        return '';
    }
    var s = String(v).trim();
    if (!s || s === 'undefined' || s === 'null') {
        return '';
    }
    return s;
}

function guindexAuthStorageLooksValid() {
    var u = guindexSanitizeDisplayName(localStorage.getItem('guindexUsername'));
    var t = (localStorage.getItem('guindexAccessToken') || '').trim();
    var id = (localStorage.getItem('guindexUserId') || '').trim();
    var st = localStorage.getItem('guindexIsStaffMember');
    if (!u || !t || !id || st == null) {
        return false;
    }
    if (id === 'undefined' || id === 'null') {
        return false;
    }
    return true;
}

/*********/
/* Login */
/*********/
(function () {

    if (!guindexAuthStorageLooksValid()) {
        localStorage.removeItem('guindexUsername');
        localStorage.removeItem('guindexAccessToken');
        localStorage.removeItem('guindexUserId');
        localStorage.removeItem('guindexIsStaffMember');
        return;
    }

    g_loggedIn = true;
    g_username = guindexSanitizeDisplayName(localStorage.getItem('guindexUsername'));
    g_accessToken = localStorage.getItem('guindexAccessToken');
    g_userId = localStorage.getItem('guindexUserId');
    g_isStaffMember = localStorage.getItem('guindexIsStaffMember');

    onLoginSuccess();
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
                var emailEl = document.getElementById('password_login_email');
                var formEmail = emailEl ? emailEl.value.trim() : '';
                var displayName =
                    guindexSanitizeDisplayName(response['email']) ||
                    guindexSanitizeDisplayName(response['username']) ||
                    guindexSanitizeDisplayName(formEmail) ||
                    'Account';
                var staffRaw = response['isStaff'];
                var isStaff =
                    staffRaw === true ||
                    staffRaw === 'True' ||
                    staffRaw === 'true';

                localStorage.setItem('guindexUsername', displayName);
                localStorage.setItem('guindexAccessToken', response['key']);
                localStorage.setItem(
                    'guindexUserId',
                    response['user'] != null ? String(response['user']) : ''
                );
                localStorage.setItem('guindexIsStaffMember', isStaff ? 'true' : 'false');

                g_loggedIn = true;
                g_username = guindexSanitizeDisplayName(localStorage.getItem('guindexUsername'));
                g_accessToken = localStorage.getItem('guindexAccessToken');
                g_userId = localStorage.getItem('guindexUserId');
                g_isStaffMember = localStorage.getItem('guindexIsStaffMember');

                onLoginSuccess();
            } else {
                displayMessage('Error', guindexFormatRestValidationErrors(response));
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

    // Show pending contributions tab (localStorage stores string "true" / "false")
    if (g_isStaffMember === 'true') {
        document.getElementById('pending_contributions_li').style.display = 'list-item';
    }

    var page_contents = document.getElementsByClassName('page_content');

    for (var i = 0; i < page_contents.length; i++)
    {
        page_contents[i].dispatchEvent(new Event('on_login'));
    }

    // Set login status link to display username (navbar shows Log out when signed in)
    var login_link = document.getElementById('login_link');
    var logout_link = document.getElementById('logout_link');
    var logout_modal_username = document.getElementById('logout_modal_username');

    if (login_link) {
        login_link.style.display = 'none';
    }
    if (logout_link) {
        var logoutName = document.getElementById('logout_link_username');
        var safeName = guindexSanitizeDisplayName(g_username);
        if (logoutName) {
            logoutName.textContent = safeName ? safeName : '';
        }
        logout_link.style.display = 'inline-flex';
    }
    if (logout_modal_username) {
        logout_modal_username.textContent = guindexSanitizeDisplayName(g_username);
    }

    var loginClose = document.getElementById('login_close_button');
    if (loginClose) {
        loginClose.click();
    } else {
        $('#exampleModal').modal('hide');
    }

    var signedInLabel = guindexSanitizeDisplayName(g_username) || 'your account';
    displayMessage(
        'Signed in',
        '<p>You are logged in as <strong>' +
            guindexEscapeHtml(signedInLabel) +
            '</strong>.</p>'
    );
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
    request.setRequestHeader('Accept', 'application/json');
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
                displayMessage("Error", guindexFormatRestValidationErrors(response));
            }
        }
    }
});

function onSignupSuccess ()
{
    document.getElementById('login_close_button').click();

    displayMessage(
        'Verification email sent',
        '<p>Please check your email and verify your account before logging in.</p>'
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
            email: email,
        };

        var button = this;
        button.disabled = true;
        request.send(JSON.stringify(forgot_password_data));

        toggleLoader(button);

        request.onreadystatechange = function processRequest() {
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
                    'Error',
                    '<p>Password reset request failed: the server did not return JSON (HTTP ' +
                        request.status +
                        '). This often means a server error or proxy page — check server logs and email configuration.</p>'
                );
                return;
            }
            var response = parsed.data;

            if (request.status >= 200 && request.status < 300) {
                onForgotPasswordSubmitSuccess();
            } else {
                displayMessage('Error', guindexFormatRestValidationErrors(response));
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

/**
 * Invalidate server token (POST rest-auth/logout/) then clear client and reload.
 * @param {HTMLElement|null} buttonEl optional node for toggleLoader (e.g. modal Logout button)
 */
function guindexPerformLogout(buttonEl) {
    var token = localStorage.getItem('guindexAccessToken');
    if (!token) {
        clearLocalStorage();
        location.reload();
        return;
    }
    if (buttonEl) {
        toggleLoader(buttonEl);
    }
    var req = new XMLHttpRequest();
    req.open('POST', G_API_BASE + 'rest-auth/logout/', true);
    req.setRequestHeader('Authorization', 'Token ' + token);
    req.setRequestHeader('Accept', 'application/json');
    req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    req.send(null);
    req.onreadystatechange = function () {
        if (req.readyState !== 4) {
            return;
        }
        if (buttonEl) {
            toggleLoader(buttonEl);
        }
        clearLocalStorage();
        location.reload();
    };
}

$(document).on('click', '#logout_button', function () {
    guindexPerformLogout(this);
});

$(document).on('click', '#logout_link', function (e) {
    e.preventDefault();
    guindexPerformLogout(null);
});

function clearLocalStorage ()
{
    // Remove login paremeters from local storage
    localStorage.removeItem('guindexUsername');
    localStorage.removeItem('guindexAccessToken');
    localStorage.removeItem('guindexUserId');
    localStorage.removeItem('guindexIsStaffMember');
}
