(function () {

    console.log("Here");

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
            page_content.dispatchEvent(new Event('tab_display'));
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
                var html = new DOMParser().parseFromString(request.responseText, 'text/html').body.firstChild;

                // Update page content
                page_content.innerHTML = "";

                $('#' + page_content_id).append(html.innerHTML);

                onTabLoad(page_content);
            }
        }
    });

    function guindexNotifyMapIframeResize()
    {
        var iframe = document.getElementById('guindex_map_iframe');

        if (!iframe || !iframe.contentWindow)
        {
            return;
        }

        try {
            if (typeof iframe.contentWindow.guindexMapInvalidateSize === 'function')
            {
                iframe.contentWindow.guindexMapInvalidateSize();
            }
        } catch (e) {
            // Ignore if iframe is not ready yet.
        }
    }

    function guindexBindMapIframeResize()
    {
        var iframe = document.getElementById('guindex_map_iframe');

        if (!iframe || iframe.getAttribute('data-guindex-load-bound'))
        {
            return;
        }

        iframe.setAttribute('data-guindex-load-bound', '1');
        iframe.addEventListener('load', function () {
            guindexNotifyMapIframeResize();
            window.setTimeout(guindexNotifyMapIframeResize, 200);
            window.setTimeout(guindexNotifyMapIframeResize, 800);
        });
    }

    function guindexResetMapIframe()
    {
        var iframe = document.getElementById('guindex_map_iframe');
        var placeholder = document.getElementById('map_iframe_placeholder');

        if (iframe)
        {
            iframe.removeAttribute('src');
            iframe.style.display = 'none';
        }

        if (placeholder)
        {
            placeholder.style.display = 'block';
        }
    }

    function guindexLoadMapIframeForCounty(value)
    {
        var iframe = document.getElementById('guindex_map_iframe');
        var placeholder = document.getElementById('map_iframe_placeholder');

        if (!iframe)
        {
            return;
        }

        guindexBindMapIframeResize();

        if (!value)
        {
            guindexResetMapIframe();
            return;
        }

        var mapUrl = G_URL_BASE + '/live_guindex_map/';

        if (value === '__all__')
        {
            mapUrl += '?load=all';
        }
        else
        {
            mapUrl += '?county=' + encodeURIComponent(value);
        }

        if (placeholder)
        {
            placeholder.style.display = 'none';
        }

        iframe.style.display = 'block';
        iframe.src = mapUrl;
    }

    $(document).on('change', '#map_county_select', function () {
        guindexLoadMapIframeForCounty($(this).val());
    });

    function onTabLoad(tabContent)
    {
        tabContent.setAttribute('data-content_loaded', '1');

        if (tabContent.id === 'map_page')
        {
            guindexBindMapIframeResize();
        }

        tabContent.dispatchEvent(new Event('tab_display'));
    }

    document.addEventListener('tab_display', function (evt) {
        if (evt.target && evt.target.id === 'map_page')
        {
            guindexBindMapIframeResize();

            if (iframeHasSrc())
            {
                window.setTimeout(guindexNotifyMapIframeResize, 100);
                window.setTimeout(guindexNotifyMapIframeResize, 500);
            }
        }
    }, true);

    function iframeHasSrc()
    {
        var iframe = document.getElementById('guindex_map_iframe');
        return iframe && iframe.getAttribute('src');
    }

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

        if (page_content_id === 'map_page')
        {
            guindexBindMapIframeResize();

            if (iframeHasSrc())
            {
                window.setTimeout(guindexNotifyMapIframeResize, 100);
                window.setTimeout(guindexNotifyMapIframeResize, 500);
            }
        }
    };

})();
