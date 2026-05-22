/* guindex-live-map-v4: county filter on /api/map/pubs/ */
(function () {

    var config = window.GUINDEX_MAP_CONFIG || {};
    var MAP_PAGE_SIZE = 250;
    var map = null;
    var statusEl = null;
    var iconCache = {};
    var activeClusterLayer = null;
    var loadGeneration = 0;
    var selectedCounty = '';

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

    function markerIcon(color, iconName) {
        var cacheKey = color + ':' + (iconName || '');

        if (!iconCache[cacheKey]) {
            if (typeof L.AwesomeMarkers === 'undefined') {
                console.error('Guindex map: Leaflet.AwesomeMarkers is not loaded');
                iconCache[cacheKey] = L.divIcon({
                    className: 'guindex-map-fallback-icon',
                    iconSize: [12, 12],
                    iconAnchor: [6, 6]
                });
            } else {
                iconCache[cacheKey] = L.AwesomeMarkers.icon({
                    icon: iconName || 'beer',
                    markerColor: color || 'lightgray',
                    prefix: 'fa',
                    iconColor: 'white',
                    extraClasses: 'fa-rotate-0'
                });
            }
        }

        return iconCache[cacheKey];
    }

    function getCountyViewport(county) {
        if (!county || !config.countyViewports) {
            return null;
        }
        return config.countyViewports[county] || null;
    }

    function applyCountyViewport(county) {
        var vp = getCountyViewport(county);

        if (vp) {
            map.fitBounds(
                [[vp.minLat, vp.minLng], [vp.maxLat, vp.maxLng]],
                { padding: [24, 24] }
            );
            return;
        }

        map.setView([config.centerLat, config.centerLng], config.zoom);
    }

    function clearMarkers() {
        if (activeClusterLayer) {
            map.removeLayer(activeClusterLayer);
            activeClusterLayer = null;
        }
    }

    function appendQueryParam(url, key, value) {
        return url + (url.indexOf('?') >= 0 ? '&' : '?') + key + '=' + encodeURIComponent(value);
    }

    function getCountyFromApiUrl() {
        if (!config.apiUrl || config.apiUrl.indexOf('county=') < 0) {
            return '';
        }

        var query = config.apiUrl.split('?')[1] || '';
        var match = /(?:^|&)county=([^&]*)/.exec(query);

        if (!match) {
            return '';
        }

        try {
            return decodeURIComponent(match[1].replace(/\+/g, ' '));
        } catch (e) {
            return match[1];
        }
    }

    function effectiveCounty(county) {
        if (isLoadAllFromUrl()) {
            return '';
        }

        return (county || config.initialCounty || getCountyFromUrl() ||
            getCountyFromApiUrl() || '').trim();
    }

    function buildApiUrl(county, pageUrl) {
        var url = pageUrl || config.apiUrl;
        var countyFilter = effectiveCounty(county);

        if (!pageUrl) {
            url = appendQueryParam(url, 'page_size', String(MAP_PAGE_SIZE));
        }

        if (countyFilter && url.indexOf('county=') < 0) {
            url = appendQueryParam(url, 'county', countyFilter);
        }

        return url;
    }

    function getQueryParam(name) {
        var search = window.location.search || '';
        var pattern = new RegExp('[?&]' + name + '=([^&]*)');
        var match = pattern.exec(search);

        if (!match) {
            return '';
        }

        try {
            return decodeURIComponent(match[1].replace(/\+/g, ' '));
        } catch (e) {
            return match[1];
        }
    }

    function isLoadAllFromUrl() {
        return getQueryParam('load') === 'all';
    }

    function getCountyFromUrl() {
        return (getQueryParam('county') || '').trim();
    }

    function resolveInitialCounty() {
        if (config.initialCounty) {
            return config.initialCounty;
        }

        return getCountyFromUrl();
    }

    function shouldAutoLoadPubs() {
        if (config.loadOnStart) {
            return true;
        }

        if (isLoadAllFromUrl()) {
            return true;
        }

        return !!getCountyFromUrl();
    }

    function parsePage(responseText) {
        var raw = (responseText || '').trim();
        if (!raw) {
            return { pubs: [], next: null };
        }
        var data = JSON.parse(raw);
        if (Array.isArray(data)) {
            return { pubs: data, next: null };
        }
        return {
            pubs: (data && data.results) ? data.results : [],
            next: (data && data.next) ? data.next : null
        };
    }

    function addPubsToMap(pubs, county, thisLoad) {
        if (thisLoad !== loadGeneration) {
            return;
        }

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
        var marker;

        for (i = 0; i < pubs.length; i++) {
            pub = pubs[i];
            lat = parseFloat(pub.latitude);
            lng = parseFloat(pub.longitude);

            if (isNaN(lat) || isNaN(lng)) {
                continue;
            }

            color = pub.markerColor || 'lightgray';
            marker = L.marker([lat, lng], {
                icon: markerIcon(color, pub.markerIcon),
                title: pub.name || 'Pub'
            });

            if (pub.popupHtml) {
                marker.bindPopup(
                    '<div class="guindex-map-popup">' + pub.popupHtml + '</div>',
                    { maxWidth: 280 }
                );
            }

            markers.push(marker);
        }

        if (thisLoad !== loadGeneration) {
            return;
        }

        if (markers.length) {
            cluster.addLayers(markers);
            activeClusterLayer = cluster;
            map.addLayer(activeClusterLayer);

            window.setTimeout(function () {
                if (thisLoad !== loadGeneration) {
                    return;
                }

                try {
                    if (county) {
                        applyCountyViewport(county);
                    } else {
                        map.fitBounds(activeClusterLayer.getBounds().pad(0.05));
                    }
                } catch (e) {
                    applyCountyViewport(county);
                }

                refreshMapSize();
                hideStatus();
            }, 0);
        } else {
            applyCountyViewport(county);
            refreshMapSize();
            setStatus(county ? ('No pubs found in ' + county + '.') : 'No pubs with valid coordinates to display.');
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

    function fetchMapPubPage(url, accumulated, thisLoad, county, onDone, onFail) {
        if (thisLoad !== loadGeneration) {
            return;
        }

        setStatus(
            'Loading pubs' +
            (county ? ' in ' + county : '') +
            ' (' + accumulated.length + ' loaded)...'
        );

        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.setRequestHeader('Accept', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.onreadystatechange = function () {
            if (request.readyState !== 4) {
                return;
            }

            if (thisLoad !== loadGeneration) {
                return;
            }

            if (request.status < 200 || request.status >= 300) {
                onFail('Failed to load map data (HTTP ' + request.status + ').');
                return;
            }

            var page;
            try {
                page = parsePage(request.responseText);
            } catch (e) {
                console.error('Guindex map parse error:', e, 'url:', url);
                onFail(
                    'Map data response was incomplete or invalid. ' +
                    'The server may be truncating large responses.'
                );
                return;
            }

            accumulated = accumulated.concat(page.pubs);

            if (page.next) {
                fetchMapPubPage(
                    buildApiUrl(county, page.next),
                    accumulated,
                    thisLoad,
                    county,
                    onDone,
                    onFail
                );
                return;
            }

            onDone(accumulated);
        };

        request.onerror = function () {
            if (thisLoad !== loadGeneration) {
                return;
            }
            onFail('Network error while loading map data.');
        };

        request.send(null);
    }

    function loadPubsForCounty(county) {
        var apiUrl = config.apiUrl;

        if (!apiUrl) {
            setStatus('Map API URL is not configured.');
            return;
        }

        loadGeneration += 1;
        var thisLoad = loadGeneration;
        selectedCounty = effectiveCounty(county);

        clearMarkers();
        applyCountyViewport(selectedCounty);

        var statusPrefix = selectedCounty ? ('Loading ' + selectedCounty + ' pubs...') : 'Loading all pubs...';
        setStatus(statusPrefix);

        fetchMapPubPage(
            buildApiUrl(selectedCounty),
            [],
            thisLoad,
            selectedCounty,
            function (pubs) {
                if (thisLoad !== loadGeneration) {
                    return;
                }

                if (!pubs.length) {
                    applyCountyViewport(selectedCounty);
                    refreshMapSize();
                    setStatus(
                        selectedCounty ?
                            ('No pubs found in ' + selectedCounty + '.') :
                            'No pub data returned from server.'
                    );
                    return;
                }

                window.setTimeout(function () {
                    addPubsToMap(pubs, selectedCounty, thisLoad);
                }, 0);
            },
            function (message) {
                if (thisLoad !== loadGeneration) {
                    return;
                }
                setStatus(message);
            }
        );
    }

    function startMap() {
        statusEl = document.getElementById('map_status');

        initMap();

        if (shouldAutoLoadPubs()) {
            loadPubsForCounty(isLoadAllFromUrl() ? '' : effectiveCounty(''));
        } else {
            setStatus('Select a county to view pubs on the map.');
        }

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
