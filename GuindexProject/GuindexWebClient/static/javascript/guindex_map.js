/**
 * Parent-page map tab: county dropdown and iframe loading.
 * Loaded on every page (debug and production) so it is not tied to guindex_tabs.min.js.
 */
(function () {

    function mapBaseUrl() {
        if (typeof G_URL_BASE !== 'undefined') {
            return G_URL_BASE;
        }
        return location.protocol + '//' + location.host;
    }

    function guindexNotifyMapIframeResize() {
        var iframe = document.getElementById('guindex_map_iframe');

        if (!iframe || !iframe.contentWindow) {
            return;
        }

        try {
            if (typeof iframe.contentWindow.guindexMapInvalidateSize === 'function') {
                iframe.contentWindow.guindexMapInvalidateSize();
            }
        } catch (e) {
            // Cross-origin or iframe not ready.
        }
    }

    function guindexBindMapIframeResize() {
        var iframe = document.getElementById('guindex_map_iframe');

        if (!iframe || iframe.getAttribute('data-guindex-load-bound')) {
            return;
        }

        iframe.setAttribute('data-guindex-load-bound', '1');
        iframe.addEventListener('load', function () {
            guindexNotifyMapIframeResize();
            window.setTimeout(guindexNotifyMapIframeResize, 200);
            window.setTimeout(guindexNotifyMapIframeResize, 800);
        });
    }

    function guindexResetMapIframe() {
        var iframe = document.getElementById('guindex_map_iframe');
        var placeholder = document.getElementById('map_iframe_placeholder');

        if (iframe) {
            iframe.removeAttribute('src');
            iframe.style.display = 'none';
        }

        if (placeholder) {
            placeholder.style.display = 'block';
        }
    }

    window.guindexLoadMapIframeForCounty = function (value) {
        var iframe = document.getElementById('guindex_map_iframe');
        var placeholder = document.getElementById('map_iframe_placeholder');

        if (!iframe) {
            console.error('Guindex map: #guindex_map_iframe not found (is the Map tab loaded?)');
            return;
        }

        guindexBindMapIframeResize();

        if (!value) {
            guindexResetMapIframe();
            return;
        }

        var mapUrl = mapBaseUrl() + '/live_guindex_map/';

        if (value === '__all__') {
            mapUrl += '?load=all';
        } else {
            mapUrl += '?county=' + encodeURIComponent(value);
        }

        if (placeholder) {
            placeholder.style.display = 'none';
        }

        iframe.style.display = 'block';
        iframe.src = mapUrl;
    };

    window.guindexOnMapCountyChange = function (selectEl) {
        var value = selectEl ? selectEl.value : '';
        window.guindexLoadMapIframeForCounty(value);
    };

    window.guindexNotifyMapIframeResize = guindexNotifyMapIframeResize;

    window.guindexMapOnTabLoaded = function () {
        guindexBindMapIframeResize();
    };

    if (typeof $ !== 'undefined') {
        $(document).on('change', '#map_county_select', function () {
            window.guindexLoadMapIframeForCounty($(this).val());
        });
    }

    document.addEventListener('change', function (evt) {
        if (evt.target && evt.target.id === 'map_county_select') {
            window.guindexLoadMapIframeForCounty(evt.target.value);
        }
    }, true);

})();
