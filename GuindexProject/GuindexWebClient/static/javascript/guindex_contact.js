$('#contact_form_submit_button').on('click', function () {

    var name    = document.getElementById('contact_form_name').value;
    var email   = document.getElementById('contact_form_email').value;
    var subject = document.getElementById('contact_form_subject').value;
    var message = document.getElementById('contact_form_message').value;

    var contact_data = {
        'name'   : name,
        'email'  : email,
        'subject': subject,
        'message': message,
    }

    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'contact/', true); 
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(JSON.stringify(contact_data));

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
                displayMessage("Info", "Thank you for your message. A member of the Guindex team will be in touch with you shortly.");
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
}) 
