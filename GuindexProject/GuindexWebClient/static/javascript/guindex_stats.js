var g_stats = null;
var g_guindexStatsTable = null;
var g_retrievingStats = false;
var g_statsTableRendered = false;

function populateGuindexStatsTable ()
{
    // Hack to avoid fetching stats each time tab is opened
    if (g_statsTableRendered)
        return;

    function getStats (callback)
    {
        if (g_retrievingStats)
            return;

        g_stats = null;

        // Function to get detailed info about this user using REST API
        var request = new XMLHttpRequest();

        request.open('GET', G_API_BASE + 'statistics/1/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(null);

        g_retrievingStats = true;

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                g_stats = JSON.parse(request.responseText);
                g_retrievingStats = false;

                if (callback)
                    callback();
            }
        }
    }

    if (g_stats == null)
    {
        getStats(populateGuindexStatsTable);
        return;
    }

    var table_data = [];

    var last_calculated               = new Date(g_stats['lastCalculated']).toString().split(' ');
    var last_calculated_pretty_format = last_calculated[0] + ' ' + last_calculated[2] + ' ' + last_calculated[1] + ' ' + last_calculated[3] + ' ' + last_calculated[4];

    table_data.push(["Number of Pubs in Database",          g_stats['pubsInDb']]);
    table_data.push(["Percentage Visited",                  g_stats['percentageVisited'] + '%']);
    table_data.push(["Average Price",                       "\u20AC" + g_stats['averagePrice']]);
    table_data.push(["Standard Deviation",                  "\u20AC" + g_stats['standardDeviation']]);
    table_data.push(["Number of Closed Pubs",               g_stats['closedPubs']]);
    table_data.push(["Number of Pubs not Serving Guinness", g_stats['notServingGuinness']]);
    table_data.push(["Last Calculated",                     last_calculated_pretty_format]);
    table_data.push(["Number of Users",                     g_stats['numUsers']]);

    // Check if table is being drawn from scratch or refreshed
    if (!g_guindexStatsTable)
    {
        data_columns = [
            {title: "Statistic", "orderable": false},
            {title: "Value",     "orderable": false},
        ]

        g_guindexStatsTable = $('#GuindexStatisticsTable').DataTable({
                                  responsive: true,
                                  data: table_data,
                                  columns: data_columns,
                                  "paging": false,
                                  "ordering": false,
                                  "searching": false,
                              });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_guindexStatsTable.clear().draw();
        g_guindexStatsTable.rows.add(table_data);
        g_guindexStatsTable.columns.adjust().draw();
    }

    g_statsTableRendered = true;
}

/******************/
/* Dynamic Charts */
/******************/
$(function () {
	
	var CountyColors = [{county:"Dublin",colour1:"darkblue", colour2:"lightblue"},
	{county:"Cork",colour1:"red", colour2:"white"},
	{county:"Galway",colour1:"maroon", colour2:"white"},
	{county:"Kerry",colour1:"green", colour2:"yellow"},
	{county:"Limerick",colour1:"green", colour2:"white"},
	{county:"Kildare",colour1:"white", colour2:"black"},
	{county:"Mayo",colour1:"green", colour2:"red"},
	{county:"Tipperary",colour1:"blue", colour2:"yellow"},
	{county:"Donegal",colour1:"yellow", colour2:"green"},
	{county:"Wexford",colour1:"purple", colour2:"yellow"},
	{county:"Clare",colour1:"yellow", colour2:"blue"},
	{county:"Meath",colour1:"green", colour2:"yellow"},
	{county:"Westmeath",colour1:"maroon", colour2:"white"},
	{county:"Waterford",colour1:"white", colour2:"blue"},
	{county:"Sligo",colour1:"black", colour2:"white"},
	{county:"Kilkenny",colour1:"black", colour2:"yellow"},
	{county:"Louth",colour1:"red", colour2:"white"},
	{county:"Offaly",colour1:"green", colour2:"gold"},
	{county:"Wicklow",colour1:"blue", colour2:"yellow"},
	{county:"Laois",colour1:"blue", colour2:"white"},
	{county:"Roscommon",colour1:"yellow", colour2:"darkblue"},
	{county:"Leitrim",colour1:"yellow", colour2:"green"},
	{county:"Cavan",colour1:"darkblue", colour2:"white"},
	{county:"Carlow",colour1:"red", colour2:"yellow"},
	{county:"Longford",colour1:"blue", colour2:"white"},
	{county:"Monaghan",colour1:"white", colour2:"blue"}];

	function addData(chart, label, data) {
	    chart.data.labels.push(label);
	    chart.data.datasets.forEach((dataset) => {
	        dataset.data.push(data);
	    });
	    chart.update();
	}

	function isEven(n) {
	   return n % 2 == 0;
	}

	var ctx = document.getElementById("myChart");
	var myChart = new Chart(ctx, {
	    type: 'bar',
	    data: {
	        labels: ["Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading","Loading", "Loading"],
	        datasets: [{
	            label: 'Pubs Not Visited',
	            data: [0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0, 0 ],
	            backgroundColor: [
	               // 'blue',
	                'darkblue',
	                'red',
	                'maroon',
	                'green',
	                'green',
	                'white',
	                'red',
	                'blue',
	                'yellow',
	                'purple',
	                'yellow',
	                'green',
	                'maroon',
	                'white',
	                'black',
	                'blue',
	                'red',
	                'blue',
	                'blue',
	                'blue',
	                'yellow',
	                'yellow',
	                'blue',
	                'blue',
	                'blue',
	                'white'

	            ],
	            labels: [0, 0, 0, 0, 0, 0
	        		,0, 0, 0, 0, 0, 0
	        		,0,0,0,0,0,0
	        		,0,0,0,0,0,0,0,0],
	            borderColor: 'black',
	            borderWidth: 1
	        },
	        {
	            label: 'Pubs Visited',
	            data: [0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0, 0 ],
	            backgroundColor: [
	               // 'blue',
	                'lightblue',
	                'white',
	                'white',
	                'yellow',
	                'white',
	                'black',
	                'green',
	                'yellow',
	                'green',
	                'purple',
	                'blue',
	                'red',
	                'yellow',
	                'green',
	                'purple',
	                'blue',
	                'red',
	                'yellow',
	                'green',
	                'purple',
	                'blue',
	                'red',
	                'yellow',
	                'green',
	                'purple',
	                'blue'

	            ],
	            borderColor: 'black',
	            borderWidth: 1
	        }]
	    },
	    options: {
	    	legend:{
	    		display: false
	    	},
	        scales: {
	            yAxes: [{

	            	stacked: true,
	                ticks: {
	                    beginAtZero:true,
	                    fontColor: 'black'
	                }
	            }],
				xAxes: [{
					gridLines: {
    					color: "rgba(0, 0, 0, 0)",
					},
					stacked: true,
					scaleLabel:{
	            		display: true,
	            		labelString: '# of Pubs'
	            	},
    				ticks: {
    					autoSkip: false,
        				fontColor: 'black'
    				},
				}]
	        },
	        tooltips: {
				callbacks: {
					label: function(tooltipItem,data) {
						var oppositeIndex = tooltipItem.datasetIndex;
						if(oppositeIndex == 0){
							oppositeIndex = 1;
						}else{
							oppositeIndex = 0;
						}
						//console.log(tooltipItem);
						var TotalToolTip = tooltipItem.yLabel + data.datasets[oppositeIndex].data[tooltipItem.index];
						var PercentTooltip = Math.round((tooltipItem.yLabel / TotalToolTip)*1000)/10; 
    				//return Number(tooltipItem.xLabel) + " " + data.datasets[tooltipItem.datasetIndex].label + " " + Number(data.datasets[0].data[tooltipItem.datasetIndex]) + " " + Number(data.datasets[1].data[tooltipItem.datasetIndex]) ;
    				return Number(tooltipItem.yLabel) + "  " + data.datasets[tooltipItem.datasetIndex].label + "  " + Number(PercentTooltip) +"%" ;
    				//+ "% Average Price: €" + Number(data.datasets[0].labels[tooltipItem.index]);
					}
				}
			}
	    }
	});

	var ctx2 = document.getElementById("myPriceChart");
	var myPriceChart = new Chart(ctx2, {
	    type: 'bar',
	    data: {
	        labels: ["Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading","Loading", "Loading"],
	        datasets: [{
	            label: 'Average Price of a Pint',
	            data: [0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0
	            ,0, 0, 0, 0, 0, 0, 0 ],
	            backgroundColor: [
	               // 'blue',
	                'darkblue',
	                'red',
	                'maroon',
	                'green',
	                'green',
	                'white',
	                'red',
	                'blue',
	                'yellow',
	                'purple',
	                'yellow',
	                'green',
	                'maroon',
	                'white',
	                'black',
	                'blue',
	                'red',
	                'blue',
	                'blue',
	                'blue',
	                'yellow',
	                'yellow',
	                'blue',
	                'blue',
	                'blue',
	                'white'

	            ],
	            labels: [0, 0, 0, 0, 0, 0
	        		,0, 0, 0, 0, 0, 0
	        		,0,0,0,0,0,0
	        		,0,0,0,0,0,0,0,0],
	            borderColor: 'black',
	            borderWidth: 1
	        }]
	    },
	    options: {

	    	legend:{
	    		display: false
	    	},
	        scales: {
	            yAxes: [{

	            	//stacked: true,
	                ticks: {
	                	min:3,
	                	//max:6,
	                    beginAtZero:false,
	                    fontColor: 'black'
	                }
	            }],
				xAxes: [{
	            	gridLines: {
    					color: "rgba(0, 0, 0, 0)",
					},
					scaleLabel:{
	            		display: true,
	            		labelString: ' Average Price of Pint'
	            	},
    				ticks: {
    					autoSkip: false,
        				fontColor: 'black'
    				},
				}]
	        },
	        tooltips: {
				callbacks: {
					label: function(tooltipItem,data) {
						
						//console.log(tooltipItem);
						//var TotalToolTip = tooltipItem.xLabel + data.datasets[oppositeIndex].data[tooltipItem.index];
						//var PercentTooltip = Math.round((tooltipItem.xLabel / TotalToolTip)*1000)/10; 
    				//return Number(tooltipItem.xLabel) + " " + data.datasets[tooltipItem.datasetIndex].label + " " + Number(data.datasets[0].data[tooltipItem.datasetIndex]) + " " + Number(data.datasets[1].data[tooltipItem.datasetIndex]) ;
    				return "Average Price: €" + Number(data.datasets[0].data[tooltipItem.index]);
					}
				}
			}
	    }
	});


	var pubs_endpoint = "https://guindex.ie/api/pubs/"
var pubs_list = [];

appendPageToPubsList(1);

function appendPageToPubsList(pageNumber)
{
    var request = new XMLHttpRequest();

    request.open('GET', pubs_endpoint + '?page=' + pageNumber, true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            var response = JSON.parse(request.responseText);

            for (var i = 0; i < response['results'].length; i++)
            {
                pubs_list.push(response['results'][i]);
            }

            //console.log(response['next']);
            
            if (response['next'])
            {
                appendPageToPubsList(++pageNumber);
            }
            else
            {
                //console.log(pubs_list.length);
                //console.log(pubs_list[1]);
                var res;
                var CountryResult = [];

                var CountryResult = pubs_list.reduce(function(res, value) {
                  if (!res[value.county]) {
                    res[value.county] = { county: value.county, qty: 0 , visited: 0 , notvisited: 0 , totalPrices:0 , averagePrice: 0 };
                    CountryResult.push(res[value.county])
                  }

                  res[value.county].qty += 1;
                  if(value.lastPrice == null){
                  	res[value.county].notvisited += 1;
                  }else{
                  	res[value.county].visited += 1;
                  	res[value.county].totalPrices += Number(value.lastPrice);
                  	res[value.county].averagePrice = Math.round((res[value.county].totalPrices/res[value.county].visited)*100)/100;
                  }
                  return res;
                }, {});


                //console.log(CountryResult);

                var sortedCountryResults = [];
				Object.keys(CountryResult).forEach(function(key) {
				    sortedCountryResults.push([key, CountryResult[key].qty,CountryResult[key].visited,CountryResult[key].notvisited,CountryResult[key].averagePrice]);
				});

				sortedCountryResults.sort(function(a, b) {
				    return b[1] - a[1];
				});

				var sortedCountryPrice = [];
				Object.keys(CountryResult).forEach(function(key) {
				    sortedCountryPrice.push([key, CountryResult[key].qty,CountryResult[key].visited,CountryResult[key].notvisited,CountryResult[key].averagePrice]);
				});

				sortedCountryPrice.sort(function(a, b) {
				    return b[4] - a[4];
				});

				var m = 0 ;
                Object.keys(sortedCountryResults).forEach(function(key) {
					//console.log(key, sortedCountryResults[key],sortedCountryResults[key].qty,sortedCountryResults[key].visited,sortedCountryResults[key].notvisited,sortedCountryResults[key].averagePrice);

				    myChart.data.datasets[0].data[m] = sortedCountryResults[key][3];
				    myChart.data.datasets[1].data[m] = sortedCountryResults[key][2];

				    myChart.data.datasets[0].labels[m] = sortedCountryResults[key][4];

					myChart.data.labels[m] = sortedCountryResults[key][0];

					for(var j = 0; j < CountyColors.length; j++){
						if(sortedCountryResults[key][0] == CountyColors[j].county){
							myChart.data.datasets[0].backgroundColor[m] = CountyColors[j].colour1;
							myChart.data.datasets[1].backgroundColor[m] = CountyColors[j].colour2;
						}
					}

					m = m+1;

				});

                var m = 0 ;
                Object.keys(sortedCountryPrice).forEach(function(key) {
					//console.log(key, sortedCountryPrice[key],sortedCountryPrice[key].qty,sortedCountryPrice[key].visited,sortedCountryPrice[key].notvisited,sortedCountryPrice[key].averagePrice);

				    myPriceChart.data.datasets[0].data[m] = sortedCountryPrice[key][4];
					myPriceChart.data.labels[m] = sortedCountryPrice[key][0];

					for(var j = 0; j < CountyColors.length; j++){
						if(sortedCountryPrice[key][0] == CountyColors[j].county){

							myPriceChart.data.datasets[0].backgroundColor[m] = CountyColors[j].colour1;
							//myChart.data.datasets[1].backgroundColor[m] = CountyColors[j].colour2;
						}
					}

					m = m+1;

				});

				myChart.update();
				myPriceChart.update();
                
            }
        }   
    }
};

});
