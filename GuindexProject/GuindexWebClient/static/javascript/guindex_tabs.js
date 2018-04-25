(function () {

    var page_content_links = document.getElementsByClassName('page_content_link'); 
    var page_content_divs  = document.getElementsByClassName('page_content')

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

            // If displaying the map, trigger resize
        });
    }
})();
