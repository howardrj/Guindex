(function () {

    console.log("Here");

    if (typeof window.guindexLoadMapIframeForCounty !== 'function') {
        window.guindexLoadMapIframeForCounty = function (value) {
            var iframe = document.getElementById('guindex_map_iframe');
            var placeholder = document.getElementById('map_iframe_placeholder');
            var base = (typeof G_URL_BASE !== 'undefined') ? G_URL_BASE : (location.protocol + '//' + location.host);

            if (!iframe) {
                console.error('Guindex map: #guindex_map_iframe not found');
                return;
            }

            if (!value) {
                iframe.removeAttribute('src');
                iframe.style.display = 'none';
                if (placeholder) {
                    placeholder.style.display = 'block';
                }
                return;
            }

            var mapUrl = base + '/live_guindex_map/';
            mapUrl += (value === '__all__') ? '?load=all' : ('?county=' + encodeURIComponent(value));

            if (placeholder) {
                placeholder.style.display = 'none';
            }

            iframe.style.display = 'block';
            iframe.src = mapUrl;
        };
    }

    var page_content_divs = document.getElementsByClassName('page_content');
    var g_firstPage = true;

    $(document).on('click', '.page_content_link', function () {

        // Hide all page content
        for (var i = 0; i < page_content_divs.length; i++)
        {
            page_content_divs[i].style.display = 'none';    
        }

        // Get anchor node (evt.target may be child node)
        var anchor_node = this;

        while (!anchor_node.classList.contains('page_content_link'))
        {
            anchor_node = anchor_node.parentNode;
        }

        var page_content_id = anchor_node.getAttribute('data-content_page_id');

        var page_content = document.getElementById(page_content_id);

        // Update URL
        if (g_firstPage)
        {
            // Overwrite history if first page
            g_firstPage = false;

            history.replaceState(page_content_id,
                                 'Guindex', 
                                 location.protocol + '//' + location.hostname + ':' + location.port + '/' + page_content_id.slice(0, -5) + '/'); // Remove _page suffix
        }
        else
        {
            history.pushState(page_content_id,
                              'Guindex', 
                              location.protocol + '//' + location.hostname + ':' + location.port + '/' + page_content_id.slice(0, -5) + '/'); // Remove _page suffix
        }
    
        // Send analytics page view
        if (!g_debug)
            ga('send', 'pageview', page_content_id);
        
        if (page_content.hasAttribute('data-content_loaded') && page_content.getAttribute('data-content_loaded') == '1')
        {
            page_content.style.display = 'block';
            if (typeof window.guindexInitTabContent === 'function') {
                window.guindexInitTabContent(page_content);
            }
            page_content.dispatchEvent(new Event('tab_display', { bubbles: true }));
            return;
        }

        // TODO Start loader
        page_content.style.display = 'block'; 
        
        var request = new XMLHttpRequest();

        request.open('GET', G_URL_BASE + '/async_load/' + page_content_id.slice(0, -5), true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                injectAsyncPageContent(page_content, request.responseText);
                onTabLoad(page_content);
            }
        }
    });

    function injectAsyncPageContent(page_content, responseText)
    {
        var doc = new DOMParser().parseFromString(responseText, 'text/html');
        var loaded = doc.getElementById(page_content.id);

        page_content.innerHTML = '';

        if (loaded) {
            page_content.innerHTML = loaded.innerHTML;
        } else if (doc.body) {
            page_content.innerHTML = doc.body.innerHTML;
        } else {
            page_content.innerHTML = responseText;
        }
    }

    function guindexOnMapTabReady() {
        if (typeof window.guindexBindMapCountySelect === 'function') {
            window.guindexBindMapCountySelect();
        }

        if (typeof window.guindexMapOnTabLoaded === 'function') {
            window.guindexMapOnTabLoaded();
        }

        if (typeof window.guindexNotifyMapIframeResize === 'function') {
            var iframe = document.getElementById('guindex_map_iframe');
            if (iframe && iframe.getAttribute('src')) {
                window.setTimeout(window.guindexNotifyMapIframeResize, 100);
                window.setTimeout(window.guindexNotifyMapIframeResize, 500);
            }
        }
    }

    /**
     * Async tab HTML is injected with innerHTML, so inline <script> tags there
     * never run. Initialise each tab from the parent page after content loads.
     */
    function guindexInitTabContent(tabContent) {
        if (!tabContent || !tabContent.id) {
            return;
        }

        if (tabContent.getAttribute('data-content_loaded') !== '1') {
            return;
        }

        switch (tabContent.id) {
            case 'map_page':
                guindexOnMapTabReady();
                break;
            case 'contributions_page':
                if (typeof populateUserContributionsTable === 'function') {
                    populateUserContributionsTable();
                }
                break;
            case 'settings_page':
                if (typeof populateUserSettingsTable === 'function') {
                    populateUserSettingsTable();
                }
                break;
            case 'data_table_page':
                if (typeof populateGuindexDataTable === 'function') {
                    populateGuindexDataTable();
                }
                if (typeof g_loggedIn !== 'undefined' && g_loggedIn &&
                    typeof g_guindexDataTable !== 'undefined' && g_guindexDataTable &&
                    typeof g_guindexDataTable.onLogin === 'function') {
                    g_guindexDataTable.onLogin();
                }
                break;
            case 'statistics_page':
                if (typeof populateGuindexStatsTable === 'function') {
                    populateGuindexStatsTable();
                }
                break;
            case 'pending_contributions_page':
                if (typeof populatePendingContributionsTables === 'function') {
                    populatePendingContributionsTables();
                }
                break;
            default:
                break;
        }
    }

    window.guindexInitTabContent = guindexInitTabContent;

    function onTabLoad(tabContent)
    {
        tabContent.setAttribute('data-content_loaded', '1');
        guindexInitTabContent(tabContent);
        tabContent.dispatchEvent(new Event('tab_display', { bubbles: true }));
    }

    document.addEventListener('tab_display', function (evt) {
        if (evt.target && evt.target.classList &&
            evt.target.classList.contains('page_content')) {
            guindexInitTabContent(evt.target);
        }
    }, true);

    document.addEventListener('on_login', function (evt) {
        if (evt.target && evt.target.classList &&
            evt.target.classList.contains('page_content')) {
            guindexInitTabContent(evt.target);
        }
    }, true);

    function onUrlChange()
    {
        // Get URL path 
        var path = window.location.pathname;

        // Chop off leading slash
        path = path.slice(1);

        // Chop off trailing slash (if it exists)
        if (path[path.length - 1] == "/")
        {
            path = path.slice(0, -1);
        } 

        // Try find corresponding page
        var tab_to_open = document.getElementById(path + '_page');

        if (tab_to_open != null)
        {
            document.querySelectorAll('[data-content_page_id="' + path + '_page' + '"]')[0].click();
        }
        else // Open overview page if we can't find corresponding tab
        {
            document.querySelectorAll('[data-content_page_id="overview_page"]')[0].click();
        }
    }

    // Call it once at startup
    onUrlChange();

    // Callback invoked each time we step through history
    window.onpopstate = function(evt) {

        var page_content_id = evt.state; // First parameter to history.pushState

        // Just display correct page here
        // Don't need to pushState or do any analytics stuff

        // Hide all page content
        for (var i = 0; i < page_content_divs.length; i++)
        {
            page_content_divs[i].style.display = 'none';    
        }

        // Display corresponding page content
        var page_content = document.getElementById(page_content_id);
        page_content.style.display = 'block';

        if (page_content) {
            guindexInitTabContent(page_content);
        }
    };

})();
