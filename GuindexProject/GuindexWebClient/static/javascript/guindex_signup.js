var g_signUpBusy = false;

function signUpUsernameFromEmail(email) {
    var trimmed = (email || '').trim();
    if (!trimmed) {
        return '';
    }
    if (trimmed.length <= 150) {
        return trimmed;
    }
    return trimmed.substring(0, 150);
}

function submitSignUp() {
    if (g_signUpBusy) {
        return;
    }
    g_signUpBusy = true;

    var email = document.getElementById('sign_up_email').value;
    var password1 = document.getElementById('sign_up_password1').value;
    var password2 = document.getElementById('sign_up_password2').value;
    var username = signUpUsernameFromEmail(email);

    var request = new XMLHttpRequest();
    request.open('POST', G_API_BASE + 'rest-auth/registration/', true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('Accept', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    var payload = {
        username: username,
        email: email.trim(),
        password1: password1,
        password2: password2,
    };
    request.send(JSON.stringify(payload));

    var button = document.getElementById('sign_up_submit_button');
    toggleLoader(button);

    request.onreadystatechange = function () {
        if (request.readyState !== 4) {
            return;
        }
        g_signUpBusy = false;
        toggleLoader(button);

        var parsed = guindexParseJsonResponse(request.responseText);
        if (!parsed.ok) {
            displayMessage(
                'Error',
                '<p>Sign up failed: the server did not return valid JSON (HTTP ' +
                    request.status +
                    ').</p>'
            );
            return;
        }
        var response = parsed.data;

        if (request.status >= 200 && request.status < 300) {
            displayMessage(
                'Account created',
                '<p>Your account is ready. Use <strong>Login</strong> in the menu, choose ' +
                    '<strong>Login with Password</strong>, and sign in with this email and password.</p>'
            );
            document.getElementById('sign_up_email').value = '';
            document.getElementById('sign_up_password1').value = '';
            document.getElementById('sign_up_password2').value = '';
        } else {
            var errorMessage = '<p>Please fix the following error(s): </p>';
            var errorTable =
                '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';
            errorTable += '<tr> <th> Field </th> <th> Error </th> </tr>';

            Object.keys(response).forEach(function (key) {
                errorTable += '<tr><td>' + key + '</td><td>' + response[key] + '</td></tr>';
            });
            errorTable += '</tbody></table>';
            displayMessage('Error', errorMessage + errorTable);
        }
    };
}

$(document).on('submit', '#sign_up_form', function (e) {
    e.preventDefault();
    submitSignUp();
});

$(document).on('click', '#sign_up_submit_button', function (e) {
    e.preventDefault();
    submitSignUp();
});
