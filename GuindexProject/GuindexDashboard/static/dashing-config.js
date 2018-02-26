//var API_URL_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';
var API_URL_BASE = 'https://guindex.ie/api/'
var dashboard_set = new DashboardSet();


// Statistics Dashboard
dashboard_set.addDashboard('Statistics');

stats_dashboard = dashboard_set.getDashboard('Statistics');

stats_dashboard.addWidget('PubsNumbers_widget', 'Number', {

	color : '#515BB2',
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

	color : '#FF6D3A',
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

/*
stats_dashboard.addWidget('Users_widget', 'Number', {

	color : '#FF6D3A',
    getData: function () {
	
	this.interval = 10000;

        // Retrieve statistics through API
        var requestCons = new XMLHttpRequest();
        
	requestCons.open('GET', API_URL_BASE + 'contributors/', true); 
        requestCons.setRequestHeader('Content-Type', 'application/json');
        requestCons.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        requestCons.send(null);

        var scope = this.scope
        

        // Update widget in processRequest callback

        requestCons.onreadystatechange = function processRequest()
        {
            if (requestCons.readyState == 4 && requestCons.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(requestCons.responseText);
		console.log(statistics);
		//closedPubs = statistics[0].closedPubs.toString() ;
		//notServingGuinness = statistics[0].notServingGuinness.toString() ;

	    var data = {
			title: 'Users Signed Up',
            		moreInfo: 'Not serving Guinness',
            		//updatedAt: 'Last updated at 14:10',
           		detail: '20',
           		value: '30'
		};
		//console.log(data);
	    
		}

		$.extend(scope,data);
	}
	
    }
});
*/

stats_dashboard.addWidget('CheapestPints', 'List', {

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
            //var last_calculated = new Date(statistics['lastCalculated']);
            //var last_calculated_time = last_calculated.toLocaleTimeString();
            //var last_calculated_date = last_calculated.toLocaleDateString();


            //var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

		var statistics_data = [];

		//console.log(statistics.pubsWithPrices[0]);
		
            Object.keys(statistics).forEach(function (key, index) {

                if (key == 'pubsWithPrices')
                {
                    // Copy pubs with prices list into two lists that will be sorted

                    var cheapest_first = statistics.pubsWithPrices.slice();


                    cheapest_first.sort(function(a, b) {
                        return parseFloat(a.price) - parseFloat(b.price); 
                    });

			//statistics_data.push({label: key, value: statistics[key]});
			for(i=0; i<16;i++) {

                   		statistics_data.push({label: cheapest_first[i].name , value: "\u20AC" + cheapest_first[i].price.toString()});

			};
                    
                }
  
		
            });

		var dataset = {
			title: 'Cheapest Pints',
                	//updatedAt: 'Last calculated: ' + last_calculated_string,
                	data: statistics_data
		}; 

            // Set widget data
            $.extend(scope, dataset);
        }
    }
});

stats_dashboard.addWidget('DearestPints', 'List', {

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
            //var last_calculated = new Date(statistics['lastCalculated']);
            //var last_calculated_time = last_calculated.toLocaleTimeString();
            //var last_calculated_date = last_calculated.toLocaleDateString();


            //var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

		var statistics_data = [];

		//console.log(statistics.pubsWithPrices[0]);
		
            Object.keys(statistics).forEach(function (key, index) {

                if (key == 'pubsWithPrices')
                {
                    // Copy pubs with prices list into two lists that will be sorted
			//console.log(statistics.pubsWithPrices);

                    var dearest_first  = statistics.pubsWithPrices.slice();

                    dearest_first.sort(function(a, b) {
                        return parseFloat(b.price) - parseFloat(a.price); 
                    });

			//statistics_data.push({label: key, value: statistics[key]});
			for(i=0; i<16;i++) {

                   		statistics_data.push({label: dearest_first[i].name, value: "\u20AC" + dearest_first[i].price.toString()});

			};
                    
                }
  
		
            });

		var dataset = {
			title: 'Dearest Pints',
                	//updatedAt: 'Last calculated: ' + last_calculated_string,
                	data: statistics_data
		}; 

            // Set widget data
            $.extend(scope, dataset);
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
            //var last_calculated = new Date(statistics['lastCalculated']);
            //var last_calculated_time = last_calculated.toLocaleTimeString();
            //var last_calculated_date = last_calculated.toLocaleDateString();


            //var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

		var statistics_data = [];

		//console.log(statistics.pubsWithPrices[0]);
		
            Object.keys(statistics).forEach(function (key, index) {

                if (key == 'pubsWithPrices')
                {
                    // Copy pubs with prices list into two lists that will be sorted
			//console.log(statistics.pubsWithPrices);
                    var cheapest_first = statistics.pubsWithPrices.slice();
                    var dearest_first  = statistics.pubsWithPrices.slice();

                    cheapest_first.sort(function(a, b) {
                        return parseFloat(a.price) - parseFloat(b.price); 
                    });

                    dearest_first.sort(function(a, b) {
                        return parseFloat(b.price) - parseFloat(a.price); 
                    });

			//statistics_data.push({label: key, value: statistics[key]});

                    // TODO Add this to statistics_data
                    
                }
                else if (key != 'lastCalculated') // Don't include calculation time as part of statistics
                {
                    statistics_data.push({label: key, value: statistics[key]});
                }   
		
            });

		var dataset = {
			title: 'Guindex Statistics',
                	//updatedAt: 'Last calculated: ' + last_calculated_string,
                	data: statistics_data
		}; 

            // Set widget data
            $.extend(scope, dataset);
        }
    }
});

