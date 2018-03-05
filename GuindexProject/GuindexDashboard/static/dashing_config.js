var API_URL_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';

// Define global dashboard set
// New dashboards can be be created in separate files and appended to the set
var g_dashboardSet = new DashboardSet({
    rollingChoices: true,
});
