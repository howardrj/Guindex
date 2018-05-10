var API_URL_BASE = 'https://guindex.ie/api/'


	 var requestpubsd = new XMLHttpRequest();
        requestpubsd.open('GET', API_URL_BASE + 'statistics/', true); 

        requestpubsd.setRequestHeader('Content-Type', 'application/json');
        requestpubsd.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        requestpubsd.send(null);

        requestpubsd.onreadystatechange = processRequest;


        function processRequest()
        {
            if (requestpubsd.readyState != 4 || requestpubsd.status != 200)
                return;

            // Get statistics JSON object
            var statisticsd = JSON.parse(requestpubsd.responseText)[0];    

            // Get last calculated time
            //var last_calculated = new Date(statistics['lastCalculated']);
            //var last_calculated_time = last_calculated.toLocaleTimeString();
            //var last_calculated_date = last_calculated.toLocaleDateString();


            //var last_calculated_string = last_calculated_date + ' - ' + last_calculated_time;

		var statistics_datad = [];

		//console.log(statistics.pubsWithPrices[0]);
		
            Object.keys(statisticsd).forEach(function (key, index) {

                if (key == 'pubsWithPrices')
                {
                    // Copy pubs with prices list into two lists that will be sorted
			//console.log(statistics.pubsWithPrices);

                    var dearest_first  = statisticsd.pubsWithPrices.slice();

                    dearest_first.sort(function(a, b) {
                        return parseFloat(b.price) - parseFloat(a.price); 
                    });

			//statistics_data.push({label: key, value: statistics[key]});
			for(i=0; i<16;i++) {

                   		statistics_datad.push({label: dearest_first[i].name, value: "\u20AC" + dearest_first[i].price.toString()});

			};
                    
                }
  
		
            });

		var datasetd = {
			title: 'Dearest Pints',
                	datad: statistics_datad
		}; 
		
		document.getElementById("testagaind").innerHTML = datasetd.datad[0].label; 
		document.getElementById("testagaind2").innerHTML = datasetd.datad[0].value;
		document.getElementById("testagaind3").innerHTML = datasetd.datad[1].label; 
		document.getElementById("testagaind4").innerHTML = datasetd.datad[1].value;
		document.getElementById("testagaind5").innerHTML = datasetd.datad[2].label; 
		document.getElementById("testagaind6").innerHTML = datasetd.datad[2].value;
		document.getElementById("testagaind7").innerHTML = datasetd.datad[3].label; 
		document.getElementById("testagaind8").innerHTML = datasetd.datad[3].value;
		document.getElementById("testagaind9").innerHTML = datasetd.datad[4].label; 
		document.getElementById("testagaind10").innerHTML = datasetd.datad[4].value;
		document.getElementById("testagaind11").innerHTML = datasetd.datad[5].label; 
		document.getElementById("testagaind12").innerHTML = datasetd.datad[5].value;
		document.getElementById("testagaind13").innerHTML = datasetd.datad[6].label; 
		document.getElementById("testagaind14").innerHTML = datasetd.datad[6].value;
		document.getElementById("testagaind15").innerHTML = datasetd.datad[7].label; 
		document.getElementById("testagaind16").innerHTML = datasetd.datad[7].value;
		document.getElementById("testagaind17").innerHTML = datasetd.datad[8].label; 
		document.getElementById("testagaind18").innerHTML = datasetd.datad[8].value;
		document.getElementById("testagaind19").innerHTML = datasetd.datad[9].label; 
		document.getElementById("testagaind20").innerHTML = datasetd.datad[9].value;
      
        }
