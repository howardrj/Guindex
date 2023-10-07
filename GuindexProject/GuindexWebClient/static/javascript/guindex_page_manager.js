class GuindexPageManager
{
    static singleton = null;

    constructor (url_base)
    {
        if (GuindexPageManager.singleton)
            throw new Error("Cannot have more than one GuindexPageManager instance");

        GuindexPageManager.singleton = this;
        this.url_base = url_base;
        this.displaying_first_page = true;

        this._add_on_tab_click_cbs();
        this._add_on_pop_state_cb();

        // Call it once at startup
        this._on_url_change();
    }

    _add_on_tab_click_cbs()
    {
        $(document).on('click',
                       '.page_content_link',
                       this._on_tab_click_cb);
    }

    _on_tab_click_cb ()
    {
        let page_content_divs = document.getElementsByClassName('page_content');
        let page_mgr = GuindexPageManager.singleton;

        // Hide all page content
        for (let i = 0; i < page_content_divs.length; i++)
            page_content_divs[i].style.display = 'none';    

        // Get anchor node (evt.target may be child node)
        let anchor_node = this;

        while (!anchor_node.classList.contains('page_content_link'))
            anchor_node = anchor_node.parentNode;

        let page_content_id = anchor_node.getAttribute('data-content_page_id');
        let page_content_div = document.getElementById(page_content_id);
        let page_name = page_content_id.slice(0, -5); // Remove _page suffix

        // Update URL
        if (page_mgr.displaying_first_page)
        {
            // Overwrite history if first page
            page_mgr.displaying_first_page = false;

            history.replaceState(page_content_id,
                                 'Guindex', 
                                 page_mgr.url_base + '/' + page_name + '/');
        }
        else
        {
            history.pushState(page_content_id,
                              'Guindex', 
                              page_mgr.url_base + '/' + page_name + '/');
        }
    
        // Send analytics page view
        if (!G_GUINDEX_DEBUG)
            ga('send', 'pageview', page_content_id);
        
        if (page_content_div.hasAttribute('data-content_loaded') &&
            page_content_div.getAttribute('data-content_loaded') == '1') // i.e page content is already loaded
        {
            page_content_div.style.display = 'block'; 
            page_content_div.dispatchEvent(new Event('tab_display'));
        }
        else
        {
            page_mgr._fetch_and_load_page_content(page_content_div,
                                                  page_content_id,
                                                  page_name);
        }
    }

    async _fetch_and_load_page_content (page_content_div,
                                        page_content_id,
                                        page_name)
    {
        // TODO Start loader
        page_content_div.style.display = 'block'; 

        let response = await fetch(this.url_base + '/async_load/' + page_name);

        if (!response.ok)
        {
            console.log("Failed to get content for page: " + page_name);
            return;
        }

        let page_content = await response.text()
        
        let html = new DOMParser().parseFromString(page_content, 'text/html').body.firstChild;

        // Update page content
        page_content_div.innerHTML = "";

        $('#' + page_content_id).append(html.innerHTML);

        this._on_page_load(page_content_div);
    }

    _on_page_load (page_content_div)
    {
        page_content_div.setAttribute('data-content_loaded', '1');
        page_content_div.dispatchEvent(new Event('tab_display'));
    }

    _add_on_pop_state_cb()
    {
        // Callback invoked each time we step through history
        window.onpopstate = this._on_pop_state_cb;
    }

    _on_pop_state_cb (evt)
    {
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
    }

    _on_url_change()
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

        // Simulate clicking of corresponding tab
        if (tab_to_open != null)
        {
            document.querySelectorAll('[data-content_page_id="' + path + '_page' + '"]')[0].click();
        }
        else // Open overview page if we can't find corresponding tab
        {
            document.querySelectorAll('[data-content_page_id="overview_page"]')[0].click();
        }
    }
}

(function () {

    g_guindex_page_manager = new GuindexPageManager(g_guindex_user.url_base);

})();
