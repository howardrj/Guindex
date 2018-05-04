var g_addPubMap          = null;
var g_addPubMapContainer = document.getElementById('add_pub_map');
var g_pubLocationMarker  = null;

$('#add_pub_submit_button').on('click', function () {

    if (!g_loggedIn || !g_accessToken)
    {
        displayMessage("Error", "You must be logged in to add a pub.");
        return;
    }

    var name      = document.getElementById('add_pub_name').value;
    var latitude  = g_pubLocationMarker.getPosition().lat();
    var longitude = g_pubLocationMarker.getPosition().lng();

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
                document.getElementById('add_pub_name').value = "";
    
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

function createAddPubMap (mapCenter) 
{
	var map_options = {
        zoom: G_ZOOM,
        center: mapCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        fullscreenControl: false,
	}

    // Create Map object
    g_addPubMap = new google.maps.Map(g_addPubMapContainer, map_options);

    // If we have user's location, add a marker
    g_pubLocationMarker = new google.maps.Marker({position: mapCenter,
                                                  map: g_addPubMap,
                                                  title: 'New Pub Location',
                                                  zIndex: google.maps.Marker.MAX_ZINDEX + 1});

    // Create map click event listener
    google.maps.event.addListener(g_addPubMap, 'click', function(evt) {

        // Hide old marker
        if (g_pubLocationMarker)
        {
            g_pubLocationMarker.setVisible(false);    
        }
        
        g_pubLocationMarker = new google.maps.Marker({position: evt.latLng,
                                                      map: g_addPubMap,
                                                      title: 'New Pub Location',
                                                      zIndex: google.maps.Marker.MAX_ZINDEX + 1});
    });
}
