(function () {

    GUINDEX_URL = location.protocol + '//' + location.hostname + ':' + location.port;

    // Request user contribution info from api

    var request = new XMLHttpRequest();
    request.open('GET', GUINDEX_URL + '/api/contributors/', true); 

    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = processRequest;

    function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            contributors = JSON.parse(request.responseText);    

            if (contributors.length)
                displayContributorStats(contributors);
        }
    }

    function displayContributorStats(contributors)
    {
        best_contributions_table = document.getElementById('best_contributions_table');

        // Display most visited
        most_visited = contributors.slice();

        most_visited.sort(function(a, b) {
            return b['pubsVisited'] - a['pubsVisited'];
        });

        most_pubs_visited_text = most_visited[0]['username'] +
                                 ' (' + most_visited[0]['pubsVisited'] + ')';

        document.getElementById('most_pubs_visited_value').innerHTML = most_pubs_visited_text;

        // Display most original prices
        most_original_prices = contributors.slice();

        most_original_prices.sort(function(a, b) {
            return b['originalPrices'] - a['originalPrices'];
        });

        most_original_prices_text = most_original_prices[0]['username'] +
                                   ' (' + most_original_prices[0]['originalPrices'] + ')';

        document.getElementById('most_original_prices_value').innerHTML = most_original_prices_text;

        // Display most curent verifications
        most_current_verifications = contributors.slice();

        most_current_verifications.sort(function(a, b) {
            return b['currentVerifications'] - a['currentVerifications'];
        });

        most_current_verifications_text = most_current_verifications[0]['username'] +
                                          ' (' + most_current_verifications[0]['currentVerifications'] + ')';

        document.getElementById('most_current_verifications_value').innerHTML = most_current_verifications_text;
        
        // Set personal contribution stats
        personal_stats = null;
        for (var i = 0; i < contributors.length; i++)
        {
            if (contributors[i]['username'] == g_username)
                personal_stats = contributors[i];
        }

        document.getElementById('personal_pubs_visited_value').innerHTML          = personal_stats['pubsVisited'];
        document.getElementById('personal_current_verifications_value').innerHTML = personal_stats['currentVerifications'];
        document.getElementById('personal_original_prices_value').innerHTML       = personal_stats['originalPrices'];
    }

})();
