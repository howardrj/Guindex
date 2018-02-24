var API_URL_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';
var API_URL_BASE = 'https://guindex.ie/api/'
var dashboard_set = new DashboardSet();

// Statistics Dashboard
dashboard_set.addDashboard('Statistics');

stats_dashboard = dashboard_set.getDashboard('Statistics');

stats_dashboard.addWidget('StatisticsWidget', 'List', {

    getData: function () {

        this.interval = 10000;

        // Retrieve statistics through API
        var request = new XMLHttpRequest();
        request.open('GET', API_URL_BASE + 'statistics/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);

        request.onreadystatechange = processRequest;

        var scope = this.scope

        // Update widget in processRequest callback

        function processRequest()
        {
            if (request.readyState != 4 || request.status != 200)
                return;

            // Get statistics JSON object
            var cstatistics = JSON.parse(request.responseText)[0];    

            // Get last calculated time
            var last_calculated = new Date(statistics['lastCalculated']);
            var last_calculated_time = last_calculated.toLocaleTimeString();
            var last_calculated_date = last_calculated.toLocaleDateString();

            var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

            var statistics_data = []

            Object.keys(statistics).forEach(function (key, index) {

                if (key == 'pubsWithPrices')
                {
                    // Copy pubs with prices list into two lists that will be sorted
                    var cheapest_first = statistics.pubsWihPrices.slice();
                    var dearest_first  = statistics.pubsWihPrices.slice();

                    cheapest_first.sort(function(a, b) {
                        return parseFloat(a.price) - parseFloat(b.price); 
                    });

                    dearest_first.sort(function(a, b) {
                        return parseFloat(b.price) - parseFloat(a.price); 
                    });

                    // TODO Add this to statistics_data
                    
                }
                else if (key != 'lastCalculated') // Don't include calculation time as part of statistics
                {
                    statistics_data.push({label: key, value: statistics[key]});
                }   
            });

            // Set widget data
            $.extend(scope, {
                title: 'Guindex Statistics',
                updatedAt: 'Last calculated: ' + last_calculated_string,
                data: statistics_data,
            });
        }
    }
});

