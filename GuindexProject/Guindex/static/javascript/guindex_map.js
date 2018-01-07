MAP_ICON_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/static/images/';

var initMap = function () {
    
    console.log("Initializing Map");

    navigator.geolocation.getCurrentPosition(onSuccess, onError);
}

var onSuccess = function (position)
{
    console.log("Successfully retrieved current position: " + position.coords);

    // Set map center to user's location
    var map_center = {lat: position.coords.latitude, lng: position.coords.longitude};

    setMarkers(map_center, true);
}

var onError = function (error)
{
    console.log("Failed to get current position");

    // Set map center to center of Dublin
    var map_center = {lat: 53.345280, lng: -6.272161};

    setMarkers(map_center, false);
}

var setMarkers = function (mapCenter, foundUserLocation)
{
    var map_options = {
        zoom: 17,
        center: mapCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    }

    var guindex_map = new google.maps.Map(document.getElementById('guindex_map'), map_options);

    if (foundUserLocation)
    {
        // If we have user's location, add a marker
        var mymarker = new google.maps.Marker({
                position: mapCenter,
                map: guindex_map,
                icon: MAP_ICON_BASE + 'my_location2.png',
                title: 'My Location',
                zIndex: google.maps.Marker.MAX_ZINDEX + 1
        });
    }
    
    google.maps.event.trigger(guindex_map, "resize");

    var request = new XMLHttpRequest();
    request.open('GET', 'https://guindex.ie/pubs/', true); 

    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = processRequest;

    function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            pubs = JSON.parse(request.responseText);    

            getPints(pubs, guindex_map);
        }
    }
}

var getPints = function (pubs, guindexMap) {

    var request = new XMLHttpRequest();
    request.open('GET', 'https://guindex.ie/guinness/', true); 

    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = processRequest;

    function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            pints = JSON.parse(request.responseText);    

            markPubs(pubs, pints, guindexMap);
        }
    }
}

var markPubs = function (pubs, pints, guindexMap)
{
    console.log(guindexMap);

    // Loop over all pub JSON objects
    for (var i = 0; i < pubs.length; i++)
    {
        console.log("Marking pub: " + pubs[i]['name']);

        if (pubs[i].closed)
        {
            var icon_to_use   = MAP_ICON_BASE + 'closed_icon.png';
            var price_of_pint = "Closed";
        }
        else
        {
            for (var j = pints.length - 1; j >= 0; j--)
            {
                if (pints[j]['pub'] === pubs[i]['id']) 
                {
                    var visited       = true
                    var price_of_pint = "Price: " + pints[j].price;
                    break;
                }
                else
                {
                    var visited       = false;
                    var price_of_pint = "Not yet visited";
                }
            }

            // Define Which Icons to use
            if (visited)
            {
                var icon_to_use = MAP_ICON_BASE + 'green_icon.jpg';
            }
            else
            {
                var icon_to_use = MAP_ICON_BASE + 'add_icon.png';
            }
        }

        var marker = new google.maps.Marker({
                position: {lat: parseFloat(pubs[i]['latitude']), lng: parseFloat(pubs[i]['longitude'])},
                map: guindexMap,
                icon: icon_to_use,
                title: pubs[i]['name'],
                zIndex: pubs[i]['id'],
            });


        console.log("Set marker");

        var content = '<h3>'+ "Pub: " + pubs[i]['name'] + '</h3>' + '<p>' + price_of_pint + '</p>';

        var info_window = new google.maps.InfoWindow();

        google.maps.event.addListener(marker, 'mouseover', (function (marker, content, info_window) {

            return function() {
                info_window.setContent(content);
                info_window.open(guindexMap, marker);
            };

        }) (marker, content, info_window));

        // assuming you also want to hide the info_window when user mouses-out
        google.maps.event.addListener(marker, 'mouseout', (function (marker, content, info_window) {

            return function() {
                info_window.close();
            };

        }) (marker, content, info_window));
    }
}
