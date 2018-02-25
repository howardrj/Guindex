//var API_URL_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';
var API_URL_BASE = 'https://guindex.ie/api/'
var dashboard_set = new DashboardSet();


// Statistics Dashboard
dashboard_set.addDashboard('Statistics');

stats_dashboard = dashboard_set.getDashboard('Statistics');

stats_dashboard.addWidget('PubsNumbers_widget', 'Number', {
    getData: function () {
	this.interval = 10000;

        // Retrieve statistics through API
        var request = new XMLHttpRequest();
        request.open('GET', API_URL_BASE + 'statistics/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);


        var scope = this.scope
        

        // Update widget in processRequest callback

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(request.responseText);
		pubsinDatabase = statistics[0].pubsInDb.toString() ;
		percentofPubs = statistics[0].percentageVisited.toString() + '%' ;
		
	    var data = {
			title: 'Number of Pubs in Database',
            		moreInfo: '% Visited',
            		//updatedAt: 'Last updated at 14:10',
           		detail: percentofPubs,
           		value: pubsinDatabase
		};
		
	    
		}

		$.extend(scope,data);
	}

	
	
    }
});

stats_dashboard.addWidget('PriceNumbers_widget', 'Number', {
    getData: function () {
	this.interval = 10000;

        // Retrieve statistics through API
        var request = new XMLHttpRequest();
        request.open('GET', API_URL_BASE + 'statistics/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);

        

        var scope = this.scope
        

        // Update widget in processRequest callback

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(request.responseText);
		averagePrice = "\u20AC" + statistics[0].averagePrice.toString() ;
		standardDeviation = statistics[0].standardDeviation.toString() ;
		
	    var data = {
			title: 'Average Price of a pint',
            		moreInfo: 'Standard Deviation',
            		//updatedAt: 'Last updated at 14:10',
           		detail: standardDeviation,
           		value: averagePrice
		};
		
	    
		}

		
		$.extend(scope,data);
	}

	
	
    }
});

stats_dashboard.addWidget('ClosedPub_widget', 'Number', {
    getData: function () {
	color: 'red';
	this.interval = 10000;

        // Retrieve statistics through API
        var request = new XMLHttpRequest();
        request.open('GET', API_URL_BASE + 'statistics/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);


        var scope = this.scope
        

        // Update widget in processRequest callback

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(request.responseText);
		closedPubs = statistics[0].closedPubs.toString() ;
		notServingGuinness = statistics[0].notServingGuinness.toString() ;

	    var data = {
			title: 'Closed Pubs',
            		moreInfo: 'Not serving Guinness',
            		//updatedAt: 'Last updated at 14:10',
           		detail: notServingGuinness,
           		value: closedPubs
		};
		//console.log(data);
	    
		}

		$.extend(scope,data);
	}

	
	
    }
});


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
            var statistics = JSON.parse(request.responseText)[0];    

            // Get last calculated time
            var last_calculated = new Date(statistics['lastCalculated']);
            var last_calculated_time = last_calculated.toLocaleTimeString();
            var last_calculated_date = last_calculated.toLocaleDateString();

            var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

            var statistics_data = [{label: 'Exit strategy', value: 24},
                   {label: 'Web 2.0', value: 12},
                   {label: 'Turn-key', value: 2},
                   {label: 'Enterprise', value: 12},
                   {label: 'Pivoting', value: 3},
                   {label: 'Leverage', value: 10},
                   {label: 'Streamlininess', value: 4},
                   {label: 'Paradigm shift', value: 6},
                   {label: 'Synergy', value: 7}]

		/*
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
		
            }); */

            // Set widget data
            $.extend(scope, {
                title: 'Guindex Statistics',
                updatedAt: 'Last calculated: ' + last_calculated_string,
                data: statistics_data,
            });
        }
    }
});

