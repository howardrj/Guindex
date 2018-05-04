$('#add_pub_submit_button').on('click', function () {

    if (!g_loggedIn || !g_accessToken)
        return;

    var name      = document.getElementById('add_pub_name').value;
    var latitude  = document.getElementById('add_pub_latitude').value;
    var longitude = document.getElementById('add_pub_longitude').value;

    var new_pub_data = {
        'name'     : name,
        'latitude' : latitude,
        'longitude': longitude, 
    }

    var request = new XMLHttpRequest();

    request.open('POST', G_API_BASE + 'pubs/', true); 
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    request.send(JSON.stringify(new_pub_data));

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
                if (g_isStaffMember)
                {
                    displayMessage("Info", "Thank you. Your submission was successful.");
                }
                else
                {
                    displayMessage("Info", "Thank you. A member of staff will verify your submission shortly.");
                }

                // Clear form
                document.getElementById('add_pub_name').value      = "";
                document.getElementById('add_pub_latitude').value  = "";
                document.getElementById('add_pub_longitude').value = "";
    
                // Reload relevant tables
                getPubInfo();
                initMap();
                getContributorInfo();
                getPendingContributionsInfo();
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
