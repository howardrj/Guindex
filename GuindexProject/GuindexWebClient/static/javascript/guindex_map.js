// Global constants
var G_MAP_ICON_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/static/images/';
var G_ZOOM          = 16;
var G_DUBLIN_CENTER = {lat: 53.345280, lng: -6.272161};

// Globally accessible objects
var g_guindexMap          = null; // Google maps object
var g_guindexMapContainer = document.getElementById('guindex_map');
var g_pubMarkers          = [];
var popup, Popup;

var initMap = function ()
{
    navigator.geolocation.getCurrentPosition(onSuccess, onError);
}

var checkPubListForMap = function ()
{
    if (g_pubsList.length)
    { 
        populateMap();
    }
    else
    {
        // Check later if pub data has been retrieved
        setTimeout(checkPubListForMap, 1000);
    }
}

var onSuccess = function (position)
{
    // Set map center to user's location
    var map_center = {lat: position.coords.latitude, lng: position.coords.longitude};

    createMap(map_center, true);

    createAddPubMap(map_center);

    if (g_pubsList.length)
    { 
        populateMap();
    }
    else
    {
        // Check later if pub data has been retrieved
        setTimeout(checkPubListForMap, 500);
    }
}

var onError = function (error)
{
    // Set map center to center of Dublin
    var map_center = G_DUBLIN_CENTER;
    
    createMap(map_center, false);

    createAddPubMap(map_center);

    if (g_pubsList.length)
    { 
        populateMap();
    }
    else
    {
        // Check later if pub data has been retrieved
        setTimeout(checkPubListForMap, 500);
    }
}

var createMap = function (mapCenter, foundUserLocation)
{
    // Map already created, return
    if (g_guindexMap)
        return;
        
	var map_options = {
        zoom: G_ZOOM,
        center: mapCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        fullscreenControl: false,
        gestureHandling: 'greedy'
	}

    // Create Map object
    g_guindexMap = new google.maps.Map(g_guindexMapContainer, map_options);

    // If we have user's location, add a marker
    if (foundUserLocation)
    {
        var my_marker =  new google.maps.Marker({position: mapCenter,
                                                 map: g_guindexMap,
                                                 icon: G_MAP_ICON_BASE + 'my_location.png',
                                                 title: 'My Location',
                                                 zIndex: google.maps.Marker.MAX_ZINDEX + 1});
    }
}

var populateMap = function ()
{
    // Delete old markers from map
    if (g_pubMarkers.length)
    {
        for (var i = 0; i < g_pubMarkers.length; i++)
        {
            g_pubMarkers[i].setMap(null);
        }
    }

    g_pubMarkers = [];

    // Loop over all pub JSON objects
    for (var i = 0; i < g_pubsList.length; i++)
    {
        var icon_to_use;
        var pub_label;

        if (g_pubsList[i].closed)
        {
            icon_to_use = G_MAP_ICON_BASE + 'closed_icon.png';
            pub_label   = "Closed";
        }
	    else if (!g_pubsList[i].servingGuinness)
	    {
		    icon_to_use = G_MAP_ICON_BASE + 'not_available.png';
            pub_label   = "Not Serving Guinness";
	    }
        else if (g_pubsList[i]['prices'].length)
        {
            var number_of_prices = g_pubsList[i]['prices'].length;

            icon_to_use = G_MAP_ICON_BASE + 'green_icon.jpg';
            pub_label   = "Price: €" + g_pubsList[i]['prices'][number_of_prices - 1]['price'];
        }
        else
        {
            icon_to_use = G_MAP_ICON_BASE + 'add_icon.png';
            pub_label   = 'Not yet visited';
        }

        var marker = new google.maps.Marker({position: {lat: parseFloat(g_pubsList[i]['latitude']), lng: parseFloat(g_pubsList[i]['longitude'])},
                                             map: g_guindexMap,
                                             icon: icon_to_use,
                                             title: g_pubsList[i]['name'],
                                             zIndex: g_pubsList[i]['id'],
                                             disableAutoPan: true});

        var content = '<h5>' + g_pubsList[i]['name'] + '</h5>' + '<p>' + pub_label + '</p>';

        var info_window = new google.maps.InfoWindow({
      		disableAutoPan: true,
            maxWidth:200
	    });

        google.maps.event.addListener(marker, 'click', (function (marker, content, info_window) {

            return function() {
                info_window.setContent(content);
                info_window.open(g_guindexMap, marker);
            };

        }) (marker, content, info_window));

        // Push marker to global list
        g_pubMarkers.push(marker);
    }

    // Show filter
    document.getElementById('floating_panel').style.display = 'block';

    // Apply filter
    applyMapFilter();
}

var applyMapFilter = function ()
{
    var filter_value = document.getElementById('map_search_filter').value.toUpperCase();

    for (var i = 0; i < g_pubMarkers.length; i++)
    {
        var marker = g_pubMarkers[i];

        var marker_title = marker.title.toUpperCase();

        if (marker_title.indexOf(filter_value) != -1)
        {
            marker.setVisible(true);
        }
        else
        {
            marker.setVisible(false);
        }
    }
}

var showHide = function ()
{
    var x = document.getElementById("filterArea");
	var ShowButton = document.getElementById("ShowButton");
	var HideButton = document.getElementById("HideButton");
    if (x.style.display === "none") {
        x.style.display = "inline-block";
		ShowButton.style.display = "none";
		HideButton.style.display = "inline-block";
    } else {
        x.style.display = "none";
		ShowButton.style.display = "inline-block";
		HideButton.style.display = "none";
    }
}

// Add event listeners
document.getElementById('map_search_filter').addEventListener('input', applyMapFilter);
