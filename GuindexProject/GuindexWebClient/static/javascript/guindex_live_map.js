(function () {

    var config = window.GUINDEX_MAP_CONFIG || {};
    var map = null;
    var statusEl = document.getElementById('map_status');

    function setStatus(message) {
        if (statusEl) {
            statusEl.textContent = message;
        }
    }

    function hideStatus() {
        if (statusEl) {
            statusEl.style.display = 'none';
        }
    }

    function markerIcon(color) {
        return L.divIcon({
            className: 'guindex-map-marker guindex-map-marker-' + color,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        });
    }

    function parsePubs(responseText) {
        var raw = (responseText || '').trim();
        if (!raw) {
            return [];
        }
        var data = JSON.parse(raw);
        if (Array.isArray(data)) {
            return data;
        }
        if (data && Array.isArray(data.results)) {
            return data.results;
        }
        return [];
    }

    function addPubsToMap(pubs) {
        var cluster = L.markerClusterGroup({ disableClusteringAtZoom: 14 });
        var bounds = [];

        for (var i = 0; i < pubs.length; i++) {
            var pub = pubs[i];
            var lat = parseFloat(pub.latitude);
            var lng = parseFloat(pub.longitude);

            if (isNaN(lat) || isNaN(lng)) {
                continue;
            }

            var color = pub.markerColor || 'darkgray';
            var label = pub.label || pub.name || 'Pub';
            var marker = L.marker([lat, lng], {
                icon: markerIcon(color),
                title: label
            });

            marker.bindPopup(label);
            cluster.addLayer(marker);
            bounds.push([lat, lng]);
        }

        map.addLayer(cluster);

        if (bounds.length) {
            map.fitBounds(bounds, { padding: [24, 24] });
        }
    }

    function initMap() {
        map = L.map('map', {
            center: [config.centerLat, config.centerLng],
            zoom: config.zoom,
            zoomControl: true
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        L.control.scale().addTo(map);
    }

    function loadPubs() {
        var apiUrl = config.apiUrl;

        if (!apiUrl) {
            setStatus('Map API URL is not configured.');
            return;
        }

        var request = new XMLHttpRequest();
        request.open('GET', apiUrl, true);
        request.setRequestHeader('Accept', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.onreadystatechange = function () {
            if (request.readyState !== 4) {
                return;
            }

            if (request.status < 200 || request.status >= 300) {
                setStatus('Failed to load map data (HTTP ' + request.status + ').');
                return;
            }

            try {
                var pubs = parsePubs(request.responseText);
                addPubsToMap(pubs);
                hideStatus();
            } catch (e) {
                setStatus('Failed to parse map data from server.');
            }
        };

        request.onerror = function () {
            setStatus('Network error while loading map data.');
        };

        request.send(null);
    }

    initMap();
    loadPubs();

})();
