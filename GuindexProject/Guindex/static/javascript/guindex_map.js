MAP_ICON_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/static/images/';

var initMap = function () {
    
    navigator.geolocation.getCurrentPosition(onSuccess, onError);
}

function goBack() {
    window.history.back();
}

var onSuccess = function (position)
{
    // Set map center to user's location
    var map_center = {lat: position.coords.latitude, lng: position.coords.longitude};
    var zoom = 16;

    setMarkers(map_center, true, zoom);
}

var onError = function (error)
{
    // Set map center to center of Dublin
    var map_center = {lat: 53.345280, lng: -6.272161};
    var zoom = 12;
    
    setMarkers(map_center, false, zoom);
}

var setMarkers = function (mapCenter, foundUserLocation, zoom)
{
    var myLocationCoord = mapCenter;
	var input = document.getElementById("myInput");
	var filter = input.value.toUpperCase();
	if(filter !== "")
	{
		// if search then Set map center to default location
		var map_center = {lat: 53.345280, lng: -6.272161};
		var zoom = 12;
		
	}
	
	var map_options = {
        zoom: zoom,
        center: mapCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
	}
	
    

    var guindex_map_container = document.getElementById('guindex_map');
    //var guindex_map_tab       = document.getElementById('guindex_map_link');

    var guindex_map = new google.maps.Map(guindex_map_container, map_options);

    //guindex_map_tab.addEventListener('click', function (event) {

        //google.maps.event.trigger(guindex_map, 'resize');

    //});

    if (foundUserLocation)
    {
        // If we have user's location, add a marker
        var mymarker = new google.maps.Marker({
                position: myLocationCoord,
                map: guindex_map,
                icon: MAP_ICON_BASE + 'my_location.png',
                title: 'My Location',
                zIndex: google.maps.Marker.MAX_ZINDEX + 1
        });
    }
    
    var request = new XMLHttpRequest();
    request.open('GET', 'https://guindex.ie/api/pubs/', true); 

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

function searchFunction(marker) {
	var input, filter, ul, li, a, i;
	input = document.getElementById("myInput");
	filter = input.value.toUpperCase();
			//ul = document.getElementById("myUL");
			//li = ul.getElementsByTagName("li");
			//for (i = 0; i < li.length; i++) {
	a = marker.title;
				//console.log(a);
	if (a.toUpperCase().indexOf(filter) > -1) {
		marker.visible = true;
	} else {
		marker.visible = false;
	}
}

var getPints = function (pubs, guindexMap) {

    var request = new XMLHttpRequest();
    request.open('GET', 'https://guindex.ie/api/guinness/', true); 

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
    // Loop over all pub JSON objects
    for (var i = 0; i < pubs.length; i++)
    {
        if (pubs[i].closed)
        {
            var icon_to_use   = MAP_ICON_BASE + 'closed_icon.png';
            var price_of_pint = "Closed";
        }
	else if(pubs[i].servingGuinness === false)
	{
		var icon_to_use   = MAP_ICON_BASE + 'not_available.png';
       		 var price_of_pint = "Not Serving Guin :(";
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
                disableAutoPan: true,
            });

	searchFunction(marker);

        var content = '<h3>'+ "Pub: " + pubs[i]['name'] + '</h3>' + '<p>' + price_of_pint + '</p>';

        var info_window = new google.maps.InfoWindow({
      		disableAutoPan: true
	});

        google.maps.event.addListener(marker, 'click', (function (marker, content, info_window) {

            return function() {
                info_window.setContent(content);
                info_window.open(guindexMap, marker);
            };

        }) (marker, content, info_window));

        // assuming you also want to hide the info_window when user mouses-out
        // google.maps.event.addListener(marker, 'mouseout', (function (marker, content, info_window) {

        //    return function() {
        //        info_window.close();
        //    };

        //}) (marker, content, info_window));
    }
}

function showHide() {
    var x = document.getElementById("filterArea");
	var ShowButton = document.getElementById("ShowButton");
	var HideButton = document.getElementById("HideButton");
    if (x.style.display === "none") {
        x.style.display = "block";
		ShowButton.style.display = "none";
		HideButton.style.display = "block";
    } else {
        x.style.display = "none";
		ShowButton.style.display = "block";
		HideButton.style.display = "none";
    }
}
