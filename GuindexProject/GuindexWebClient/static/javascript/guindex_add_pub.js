class GuindexAddPubMap
{
    static singleton = null;

    constructor (user,
                 map_center={lat: 53.345280, lng: -6.272161}, // Dublin Center
                 zoom=17)
    {
        if (GuindexAddPubMap.singleton)
            throw new Error("Cannot have more than one GuindexAddPubMap instance");

        GuindexAddPubMap.singleton = this;
        this.map_center = map_center;
        this.user = user;
        this.zoom = zoom;
        this.map_icon_base = this.user.url_base + '/static/images/'; 
        this.add_pub_map_container = document.getElementById('add_pub_map');
        this.add_pub_google_map = null
        this.pub_location_marker = null;
        this.pub_location_marker_title = 'New Pub Location';

        this._create_add_pub_google_map()
        this._add_on_form_submit_cb()
    }

    _create_add_pub_google_map ()
    {
        var map_options = {
            zoom: this.zoom,
            center: this.map_center,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            fullscreenControl: false,
            gestureHandling: 'greedy'
        }

        // Create Map object
        this.add_pub_google_map = new google.maps.Map(this.add_pub_map_container,
                                                      map_options);

        // If we have user's location, add a marker
        this.pub_location_marker = new google.maps.Marker({position: this.map_center,
                                                           map: this.add_pub_google_map,
                                                           title: this.pub_location_marker_title,
                                                           zIndex: google.maps.Marker.MAX_ZINDEX + 1});

        this._add_on_new_map_location_click_cb()
    }

    _add_on_new_map_location_click_cb ()
    {
        // Create map click event listener
        google.maps.event.addListener(this.add_pub_google_map,
                                      'click',
                                      this._on_new_map_location_click_cb);

    }

    _on_new_map_location_click_cb (evt)
    {
        let map = GuindexAddPubMap.singleton;

        // Hide old marker
        if (map.pub_location_marker)
            map.pub_location_marker.setVisible(false);    
    
        map.pub_location_marker = new google.maps.Marker({position: evt.latLng,
                                                          map: map.add_pub_google_map,
                                                          title: map.pub_location_marker_title,
                                                          zIndex: google.maps.Marker.MAX_ZINDEX + 1});
    }

    _add_on_form_submit_cb ()
    {
        $('#add_pub_submit_button').on('click',
                                       this._on_form_submit_cb);
    }

    _on_form_submit_cb ()
    {
        let button = this;
        let map = GuindexAddPubMap.singleton;
        let user = map.user;

        if (!user.access_token)
        {
            displayMessage("Error", "You must be logged in to add a pub.");
            return;
        }

        var name      = document.getElementById('add_pub_name').value;
        var county    = document.getElementById('add_pub_county').value;
        var latitude  = map.pub_location_marker.getPosition().lat();
        var longitude = map.pub_location_marker.getPosition().lng();

        var new_pub_data = {
            'name'     : name,
            'county'   : county,
            'latitude' : latitude,
            'longitude': longitude, 
        }

        map._post_new_pub_data(new_pub_data,
                               button)
    }
     
    async _post_new_pub_data (new_pub_data,
                              button)
    {

        toggleLoader(button);

        let response = await fetch(this.user.api_base + 'access_token/', 
                                   {
                                       method: 'POST',
                                       headers: {
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Token ' + this.user.access_token,
                                       },
                                       body: JSON.stringify(new_pub_data),
                                   });

        toggleLoader(button);

        let response_body = await response.json();

        if (response.status == 201)
        {
            this._on_add_pub_success()
        }
        else
        {
            this._on_add_pub_failure()
        }
    }

    _on_add_pub_success ()
    {
        if (this.user.is_staff_member)
        {
            displayMessage("Info", "Thank you. Your submission was successful.");
        }
        else
        {
            displayMessage("Info", "Thank you. A member of staff will verify your submission shortly.");
        }

        // Clear form
        document.getElementById('add_pub_name').value = "";
    }

    _on_add_pub_failure (response_body)
    {
        // Display errors
        var error_message = '<p>Please fix the following error(s): </p>'

        var error_table = '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';

        error_table += '<tr> <th> Field </th> <th> Error </th> </tr>';

        Object.keys(response_body).forEach(function(key) {

            error_table += '<tr>';

            error_table += '<td>' + key + '</td>';

            error_table += '<td>' + response_body[key] + '</td>';

            error_table += '</tr>';
        });

        error_table += '</tbody></table>';

        displayMessage("Error", error_message + error_table);
    }
}

function guindex_init_add_pub_map ()
{
    navigator.geolocation.getCurrentPosition(on_success, on_error);

    function on_success (position)
    {
        // Set map center to user's location
        let map_center = {lat: position.coords.latitude, lng: position.coords.longitude};

        let map = new GuindexAddPubMap(g_guindex_user,
                                       map_center);
    }

    function on_error (error)
    {
        // Set map center to center of Dublin

        let map = new GuindexAddPubMap(g_guindex_user);
    }
}
