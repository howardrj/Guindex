Dashing.widgets.LoginWithFacebook = function(dashboard) {
    var self = this;
    self.__init__ = Dashing.utils.widgetInit(dashboard, 'login_with_facebook');
    self.row = 1;
    self.col = 1;
    self.color = '#3B5998';
    self.scope = {};
    self.getWidget = function () {
        return this.__widget__;
    };
    self.getData = function () {};
    self.interval = 1000;
};

// Below code is borrowed from the Facbook javascript SDK
// SDK is loaded in login_with_facebook.html

// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
    console.log(response);

    if (response.status === 'unknown')
    {
        // The person is not logged into your app 
        document.getElementById('status').innerHTML = 'Please login to Facebook to continue.';
    }
    else if (response.status === 'not_authorized')
    {
        // The person is not logged into your app 
        document.getElementById('status').innerHTML = 'Please login to guindex.ie to continue.';
    }
    else if (response.status === 'connected')
    {
        // Logged into your app and Facebook.
        var access_token = response['authResponse']['accessToken'];
        var user_id      = response['authResponse']['userID'];

        // Retrieve user name through facebook API
        FB.api(
            '/' + user_id,
            'GET',
            {},
            function(response) {
                document.getElementById('status').innerHTML = 'Logged in as ' + response['name'] + '.';
                document.getElementById('login_with_facebook_button').style.display = 'none';
            }
        );

        // Use REST API to login to guindex.ie
        var request = new XMLHttpRequest();
        request.open('POST', API_URL_BASE + 'rest-auth/facebook/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'access_token': access_token}));

        // Pull in contributins widgets once user is authenticated
        // and display log out button
        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                // We have successfully logged in
                // Get token from response JSON object
                var response = JSON.parse(request.responseText);

                setupContributionsDashboard(response['key']); 
		    }
	    }
    } 
}

// This function is called when someone finishes with the Login Button
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

window.fbAsyncInit = function() {
    FB.init({
        appId      : '940061452839208',
        cookie     : true,  // enable cookies to allow the server to access 
                          // the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.8' // use graph api version 2.8
    });

    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });

};

var setupContributionsDashboard = function (guindexKey) {

    // Once we come in here, start populating the rest of the dashboard

    


}
