(function () {

    var config = window.GUINDEX_MAP_CONFIG || {};
    var MAP_PAGE_SIZE = 250;
    var map = null;
    var statusEl = document.getElementById('map_status');
    var countySelectEl = document.getElementById('map_county_select');
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

    function buildApiUrl(county) {
        var url = appendQueryParam(config.apiUrl, 'page_size', String(MAP_PAGE_SIZE));

        if (county) {
            url = appendQueryParam(url, 'county', county);
        }

        return url;
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
            label = pub.label || 'Pub';
            marker = L.marker([lat, lng], {
                icon: markerIcon(color),
                title: label
            });
            marker.bindPopup(label);
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
                fetchMapPubPage(page.next, accumulated, thisLoad, county, onDone, onFail);
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
        selectedCounty = county || '';

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

    function onCountyChange() {
        var county = countySelectEl ? countySelectEl.value : '';
        loadPubsForCounty(county);
    }

    function startMap() {
        initMap();

        if (countySelectEl) {
            countySelectEl.addEventListener('change', onCountyChange);
        }

        loadPubsForCounty('');

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
