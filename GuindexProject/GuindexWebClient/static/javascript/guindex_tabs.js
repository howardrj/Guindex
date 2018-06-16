(function () {

    var g_firstPage = true;

    var page_content_links = document.getElementsByClassName('page_content_link'); 
    var page_content_divs  = document.getElementsByClassName('page_content');

    for (var i = 0; i < page_content_links.length; i++)
    {
        page_content_links[i].addEventListener('click', function (evt) {

            // Hide all page content
            for (var i = 0; i < page_content_divs.length; i++)
            {
                page_content_divs[i].style.display = 'none';    
            }

            // Get anchor node (evt.target may be child node)
            var anchor_node = evt.target;

            while (!anchor_node.classList.contains('page_content_link'))
            {
                anchor_node = anchor_node.parentNode;
            }

            var page_content_id = anchor_node.getAttribute('data-content_page_id');

            // Display corresponding page content
            document.getElementById(page_content_id).style.display = 'block';

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
        });
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

    // Callback invoked each timr we step through history
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
        document.getElementById(page_content_id).style.display = 'block';
    };

})();
