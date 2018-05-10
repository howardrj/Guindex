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

	
	


	

