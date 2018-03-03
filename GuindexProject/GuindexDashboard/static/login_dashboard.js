g_dashboardSet.addDashboard('Login');

login_dashboard = g_dashboardSet.getDashboard('Login');

login_dashboard.addWidget('FacebookLoginWidget', 'LoginWithFacebook', {

    getData: function () {
        $.extend(this.scope, {
        });
    }

});
