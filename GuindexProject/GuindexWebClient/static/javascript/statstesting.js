var API_URL_BASE = 'https://guindex.ie/api/'

        // Retrieve statistics through API
        var request = new XMLHttpRequest();
        request.open('GET', API_URL_BASE + 'statistics/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);



        // Update widget in processRequest callback

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(request.responseText);
		pubsinDatabase = statistics[0].pubsInDb.toString() ;
		percentofPubs = statistics[0].percentageVisited.toString() + '%' ;
		
	    var datagenstats = {
			title: 'Number of Pubs in Database:',
            		moreInfo: '% Visited:',
           		detail: percentofPubs,
           		value: pubsinDatabase
		}
			
		  document.getElementById("test1").innerHTML = datagenstats.title;
		  document.getElementById("test2").innerHTML = datagenstats.value;
 		  document.getElementById("test3").innerHTML = datagenstats.moreInfo;
		  document.getElementById("test4").innerHTML = datagenstats.detail;
 		 
	    
		}

	
	}


        // Retrieve statistics through API
        var request2 = new XMLHttpRequest();
        request2.open('GET', API_URL_BASE + 'statistics/', true); 

        request2.setRequestHeader('Content-Type', 'application/json');
        request2.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request2.send(null);

        

   
        

        // Update widget in processRequest callback

        request2.onreadystatechange = function processRequest()
        {
            if (request2.readyState == 4 && request2.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(request2.responseText);
		averagePrice = "\u20AC" + statistics[0].averagePrice.toString() ;
		standardDeviation = "\u20AC" + statistics[0].standardDeviation.toString() ;
		
	    var dataother = {
			title: 'Average Price of a pint:',
            		moreInfo: 'Standard Deviation:',
           		detail: standardDeviation,
           		value: averagePrice
		};
		 document.getElementById("test5").innerHTML = dataother.title;
		  document.getElementById("test6").innerHTML = dataother.value;
 		  document.getElementById("test7").innerHTML = dataother.moreInfo;
		  document.getElementById("test8").innerHTML = dataother.detail;
	    
		}

		
	
	}

	
	var requestclose = new XMLHttpRequest();
        requestclose.open('GET', API_URL_BASE + 'statistics/', true); 

        requestclose.setRequestHeader('Content-Type', 'application/json');
        requestclose.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        requestclose.send(null);



        // Update widget in processRequest callback

        requestclose.onreadystatechange = function processRequest()
        {
            if (requestclose.readyState == 4 && requestclose.status == 200) {
                

            // Get statistics JSON object
            var statistics = JSON.parse(requestclose.responseText);
		closedPubs = statistics[0].closedPubs.toString() ;
		notServingGuinness = statistics[0].notServingGuinness.toString() ;

	    var dataclose = {
			title: 'Closed Pubs:',
            		moreInfo: 'Not serving Guinness:',
           		detail: notServingGuinness,
           		value: closedPubs
		};

		 document.getElementById("test9").innerHTML = dataclose.title;
		  document.getElementById("test10").innerHTML = dataclose.value;
 		  document.getElementById("test11").innerHTML = dataclose.moreInfo;
		  document.getElementById("test12").innerHTML = dataclose.detail;
	    
		}


	}

	
	var requestpubs = new XMLHttpRequest();
        requestpubs.open('GET', API_URL_BASE + 'statistics/', true); 

        requestpubs.setRequestHeader('Content-Type', 'application/json');
        requestpubs.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        requestpubs.send(null);

        requestpubs.onreadystatechange = processRequest;



        // Update widget in processRequest callback

        function processRequest()
        {
            if (requestpubs.readyState != 4 || requestpubs.status != 200)
                return;

            // Get statistics JSON object
            var statistics = JSON.parse(requestpubs.responseText)[0];    

		var statistics_data = [];

		
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
                	data: statistics_data
		};

		document.getElementById("testagain").innerHTML = dataset.data[0].label; 
		document.getElementById("testagain2").innerHTML = dataset.data[0].value;
		document.getElementById("testagain3").innerHTML = dataset.data[1].label; 
		document.getElementById("testagain4").innerHTML = dataset.data[1].value;
		document.getElementById("testagain5").innerHTML = dataset.data[2].label; 
		document.getElementById("testagain6").innerHTML = dataset.data[2].value;
		document.getElementById("testagain7").innerHTML = dataset.data[3].label; 
		document.getElementById("testagain8").innerHTML = dataset.data[3].value;
		document.getElementById("testagain9").innerHTML = dataset.data[4].label; 
		document.getElementById("testagain10").innerHTML = dataset.data[4].value;
		document.getElementById("testagain11").innerHTML = dataset.data[5].label; 
		document.getElementById("testagain12").innerHTML = dataset.data[5].value;
		document.getElementById("testagain13").innerHTML = dataset.data[6].label; 
		document.getElementById("testagain14").innerHTML = dataset.data[6].value;
		document.getElementById("testagain15").innerHTML = dataset.data[7].label; 
		document.getElementById("testagain16").innerHTML = dataset.data[7].value;
		document.getElementById("testagain17").innerHTML = dataset.data[8].label; 
		document.getElementById("testagain18").innerHTML = dataset.data[8].value;
		document.getElementById("testagain19").innerHTML = dataset.data[9].label; 
		document.getElementById("testagain20").innerHTML = dataset.data[9].value;

        }




	

