var g_stats = null;
var g_guindexStatsTable = null;
var g_retrievingStats = false;
var g_statsTableRendered = false;
var g_myChart = null;
var g_myPriceChart = null;
var g_statsChartsInitialized = false;
var g_statsPubsLoadStarted = false;
var g_statsPubsList = [];

var g_statsCountyColors = [
	{county:"Dublin",colour1:"darkblue", colour2:"lightblue"},
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
	{county:"Monaghan",colour1:"white", colour2:"blue"},
	{county:"Antrim",colour1:"gold", colour2:"white"},
	{county:"Armagh",colour1:"orange", colour2:"white"},
	{county:"Derry",colour1:"red", colour2:"white"},
	{county:"Down",colour1:"red", colour2:"black"},
	{county:"Fermanagh",colour1:"green", colour2:"white"},
	{county:"Tyrone",colour1:"white", colour2:"red"}
];

var g_statsCountyColourFallback = {colour1: 'gray', colour2: 'lightgray'};

function guindexStatsCountyColours(county) {
    var j;
    for (j = 0; j < g_statsCountyColors.length; j++) {
        if (g_statsCountyColors[j].county === county) {
            return g_statsCountyColors[j];
        }
    }
    return g_statsCountyColourFallback;
}

function populateGuindexStatsTable ()
{
    if (!document.getElementById('GuindexStatisticsTable')) {
        return;
    }

    guindexEnsureStatsChartsAndData();

    if (g_statsTableRendered && $.fn.DataTable.isDataTable('#GuindexStatisticsTable')) {
        return;
    }

    if (g_statsTableRendered) {
        g_guindexStatsTable = null;
        g_statsTableRendered = false;
    }

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
        var data_columns = [
            {title: "Statistic", "orderable": false},
            {title: "Value",     "orderable": false}
        ];

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
function guindexEnsureStatsChartsAndData()
{
    if (g_statsChartsInitialized) {
        return;
    }

    var ctx = document.getElementById('myChart');
    var ctx2 = document.getElementById('myPriceChart');

    if (!ctx || !ctx2) {
        return;
    }

	function addData(chart, label, data) {
	    chart.data.labels.push(label);
	    chart.data.datasets.forEach(function (dataset) {
	        dataset.data.push(data);
	    });
	    chart.update();
	}

	function isEven(n) {
	   return n % 2 == 0;
	}

	g_myChart = new Chart(ctx, {
	    type: 'bar',
	    data: {
	        labels: ["Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading","Loading", "Loading"],
	        datasets: [{
	            'label': 'Pubs Not Visited',
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
	            'label': 'Pubs Visited',
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
					'label': function(tooltipItem,data) {
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

	g_myPriceChart = new Chart(ctx2, {
	    type: 'bar',
	    data: {
	        labels: ["Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading"
	        ,"Loading", "Loading", "Loading", "Loading", "Loading", "Loading","Loading", "Loading"],
	        datasets: [{
	            'label': 'Average Price of a Pint',
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
					'label': function(tooltipItem,data) {
						
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


    g_statsChartsInitialized = true;

    if (!g_statsPubsLoadStarted) {
        g_statsPubsLoadStarted = true;
        guindexStatsAppendPageToPubsList(1);
    }
}

function guindexStatsAppendPageToPubsList(pageNumber)
{
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'pubs/?page=' + pageNumber, true);

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
                g_statsPubsList.push(response['results'][i]);
            }

            //console.log(response['next']);
            
            if (response['next'])
            {
                guindexStatsAppendPageToPubsList(++pageNumber);
            }
            else
            {
                //console.log(pubs_list.length);
                //console.log(pubs_list[1]);
                var res = {};
                var CountryResult = [];
                var pi;
                var countyKey;

                for (pi = 0; pi < g_statsPubsList.length; pi++) {
                    countyKey = g_statsPubsList[pi].county;
                    if (!res[countyKey]) {
                        res[countyKey] = {
                            county: countyKey,
                            qty: 0,
                            visited: 0,
                            notvisited: 0,
                            totalPrices: 0,
                            averagePrice: 0
                        };
                        CountryResult.push(res[countyKey]);
                    }

                    res[countyKey].qty += 1;
                    if (g_statsPubsList[pi].lastPrice == null) {
                        res[countyKey].notvisited += 1;
                    } else {
                        res[countyKey].visited += 1;
                        res[countyKey].totalPrices += Number(g_statsPubsList[pi].lastPrice);
                        res[countyKey].averagePrice = Math.round(
                            (res[countyKey].totalPrices / res[countyKey].visited) * 100
                        ) / 100;
                    }
                }


                var sortedCountryResults = [];
                var sortedCountryPrice = [];
                var ci;
                var row;
                var colours;
                var visitedData = [];
                var notVisitedData = [];
                var visitedColours = [];
                var notVisitedColours = [];
                var countyLabels = [];
                var priceData = [];
                var priceColours = [];

                for (ci = 0; ci < CountryResult.length; ci++) {
                    row = CountryResult[ci];
                    sortedCountryResults.push([
                        row.county,
                        row.qty,
                        row.visited,
                        row.notvisited,
                        row.averagePrice
                    ]);
                    sortedCountryPrice.push([
                        row.county,
                        row.qty,
                        row.visited,
                        row.notvisited,
                        row.averagePrice
                    ]);
                }

                sortedCountryResults.sort(function (a, b) {
                    return b[1] - a[1];
                });

                sortedCountryPrice.sort(function (a, b) {
                    return b[4] - a[4];
                });

                for (ci = 0; ci < sortedCountryResults.length; ci++) {
                    row = sortedCountryResults[ci];
                    colours = guindexStatsCountyColours(row[0]);
                    countyLabels.push(row[0]);
                    notVisitedData.push(row[3]);
                    visitedData.push(row[2]);
                    notVisitedColours.push(colours.colour1);
                    visitedColours.push(colours.colour2);
                }

                g_myChart.data.labels = countyLabels;
                g_myChart.data.datasets[0].data = notVisitedData;
                g_myChart.data.datasets[1].data = visitedData;
                g_myChart.data.datasets[0].backgroundColor = notVisitedColours;
                g_myChart.data.datasets[1].backgroundColor = visitedColours;

                countyLabels = [];
                priceData = [];
                priceColours = [];

                for (ci = 0; ci < sortedCountryPrice.length; ci++) {
                    row = sortedCountryPrice[ci];
                    colours = guindexStatsCountyColours(row[0]);
                    countyLabels.push(row[0]);
                    priceData.push(row[4]);
                    priceColours.push(colours.colour1);
                }

                g_myPriceChart.data.labels = countyLabels;
                g_myPriceChart.data.datasets[0].data = priceData;
                g_myPriceChart.data.datasets[0].backgroundColor = priceColours;

				g_myChart.update();
				g_myPriceChart.update();
                
            }
        }   
    }
};
