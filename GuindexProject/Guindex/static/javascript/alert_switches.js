(function () {

    // Globals for resetting swicth in case of error
    g_resettingSwitch = false;
    g_clickedSwitch   = null;

    var alerts_switches = document.getElementsByClassName('alerts_checkbox');

    for (var i = 0; i < alerts_switches.length; i++)
    {
        alerts_switches[i].addEventListener('change', function(evt) { updateAlertsSettings(evt) });
    }

    var updateAlertsSettings = function(evt)
    {
        g_clickedSwitch = evt.target;

        if (g_resettingSwitch) // Restore switch to original state if error cccurs
        {
            g_resettingSwitch = false;
            return
        }    

        // Send asynchronous request to server to update setting
        var request = new XMLHttpRequest();
        request.open('POST', '/guindex_alerts/', true); 

        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        var using_email    = document.getElementById('email_checkbox').checked;
        var using_telegram = document.getElementById('telegram_checkbox').checked;

        request.send(JSON.stringify({'usingEmail': using_email, 'usingTelegram': using_telegram})); 

        request.onreadystatechange = processRequest;

        function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
            }   
            else
            {
                // We got an error. Reset switch
                g_resettingSwitch = true;
                g_clickedSwitch.click();
            }
        }
    }

})();
