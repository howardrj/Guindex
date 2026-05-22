(function () {

    var config = window.GUINDEX_MAP_CONFIG || {};
    var map = null;
    var statusEl = document.getElementById('map_status');
    var iconCache = {};

    function setStatus(message) {
        if (statusEl) {
            statusEl.style.display = 'block';
            statusEl.textContent = message;
        }
    }

    function hideStatus() {
        if (statusEl) {
            statusEl.style.display = 'none';
        }
    }

    function refreshMapSize() {
        if (!map) {
            return;
        }
        map.invalidateSize(true);
    }

    window.guindexMapInvalidateSize = refreshMapSize;

    function markerIcon(color) {
        if (!iconCache[color]) {
            iconCache[color] = L.divIcon({
                className: 'guindex-map-marker guindex-map-marker-' + color,
                iconSize: [14, 14],
                iconAnchor: [7, 7]
            });
        }
        return iconCache[color];
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
        if (data && Array.isArray(data.data)) {
            return data.data;
        }
        return [];
    }

    function addPubsToMap(pubs) {
        setStatus('Placing ' + pubs.length + ' markers...');

        var cluster = L.markerClusterGroup({
            disableClusteringAtZoom: 14,
            chunkedLoading: true,
            chunkInterval: 150,
            chunkDelay: 30,
            maxClusterRadius: 50
        });

        var markers = [];
        var i;
        var pub;
        var lat;
        var lng;
        var color;
        var label;
        var marker;

        for (i = 0; i < pubs.length; i++) {
            pub = pubs[i];
            lat = parseFloat(pub.latitude);
            lng = parseFloat(pub.longitude);

            if (isNaN(lat) || isNaN(lng)) {
                continue;
            }

            color = pub.markerColor || 'darkgray';
            label = pub.label || pub.name || 'Pub';
            marker = L.marker([lat, lng], {
                icon: markerIcon(color),
                title: label
            });
            marker.bindPopup(label);
            markers.push(marker);
        }

        if (markers.length) {
            cluster.addLayers(markers);
            map.addLayer(cluster);

            window.setTimeout(function () {
                try {
                    map.fitBounds(cluster.getBounds().pad(0.05));
                } catch (e) {
                    map.setView([config.centerLat, config.centerLng], config.zoom);
                }
                refreshMapSize();
                hideStatus();
            }, 0);
        } else {
            map.setView([config.centerLat, config.centerLng], config.zoom);
            refreshMapSize();
            setStatus('No pubs with valid coordinates to display.');
        }
    }

    function initMap() {
        map = L.map('map', {
            center: [config.centerLat, config.centerLng],
            zoom: config.zoom,
            zoomControl: true,
            preferCanvas: true
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxNativeZoom: 18,
            maxZoom: 18
        }).addTo(map);

        L.control.scale().addTo(map);
        refreshMapSize();
    }

    function loadPubs() {
        var apiUrl = config.apiUrl;

        if (!apiUrl) {
            setStatus('Map API URL is not configured.');
            return;
        }

        setStatus('Loading pubs from server...');

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

            window.setTimeout(function () {
                try {
                    var pubs = parsePubs(request.responseText);
                    if (!pubs.length) {
                        setStatus('No pub data returned from server.');
                        console.warn('Guindex map: empty pub list from', apiUrl);
                        return;
                    }
                    addPubsToMap(pubs);
                } catch (e) {
                    console.error('Guindex map parse error:', e);
                    setStatus('Failed to parse map data from server.');
                }
            }, 0);
        };

        request.onerror = function () {
            setStatus('Network error while loading map data.');
        };

        request.send(null);
    }

    function startMap() {
        initMap();
        loadPubs();

        window.setTimeout(refreshMapSize, 100);
        window.setTimeout(refreshMapSize, 400);
        window.setTimeout(refreshMapSize, 1200);
        window.addEventListener('resize', refreshMapSize);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startMap);
    } else {
        startMap();
    }

})();
