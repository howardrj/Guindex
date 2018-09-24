var g_userSettings = null;
var g_userSettingsTable = null;
var g_retrievingUserSettings = false;

// Can only be called if user is logged in
function populateUserSettingsTable ()
{
    function getUserSettings (callback)
    {
        if (g_retrievingUserSettings)
           return;
        
        g_userSettings = null;

        // Function to get detailed info about this user using REST API
        var request = new XMLHttpRequest();

        request.open('GET', G_API_BASE + 'contributors/' + g_userId + '/', true);

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

        request.send(null);

        g_retrievingUserSettings = true;

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                g_userSettings = JSON.parse(request.responseText);
                g_retrievingUserSettings = false;

                if (callback)
                    callback();
            }
        }
    }

    if (g_userSettings == null)
    {
        getUserSettings(populateUserSettingsTable);
        return;
    }

    var table_data = [];

    var prefix = '<label class="switch">';
    var suffix = '<div id="email_alerts_toggler_div" class="slider round"> </div></label>';

    // Email alerts setting
    var email_alerts_list = ['Email Alerts', 
                             "Receive email alerts when new prices and pubs are added to the Guindex.",
                             prefix + '<input type="checkbox" id="email_alerts_toggler" class="toggler hoverable">' + suffix
                            ];

    table_data.push(email_alerts_list);

    // Telgram alerts setting
    var telegram_description = "Receive Telegram alerts when new prices and pubs are added to the Guindex.";

    if (!g_userSettings['telegramActivated'])
    {
        telegram_description += " To activate your Telegram account, please add the GuindexBot as a contact using" +
                                " the Telegram app and send: /activate " + g_userSettings['telegramActivationKey'] + '.';
    }

    suffix = '<div id="telegram_alerts_toggler_div" class="slider round"> </div></label>';

    var telegram_alerts_list = ['Telegram Alerts',
                                telegram_description,
                                prefix + '<input type="checkbox" id="telegram_alerts_toggler" class="toggler hoverable">' + suffix
                                ];

    table_data.push(telegram_alerts_list);

    // Check if table is being drawn from scratch or refreshed
    if (!g_userSettingsTable)
    {
        // Clear log in warning
        var settings_page = document.getElementById('settings_page');

        settings_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        settings_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        g_userSettingsTable = $('#GuindexUserSettingsTable').DataTable({
                                  responsive: true,
                                  "paging": false,
                                  "ordering": false,
                                  "searching": false,
                                  data: table_data,
                                  columns: [
                                      { title: "Setting" },
                                      { title: "Description" },
                                      { title: "Toggle" },
                                  ]
                              });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_userSettingsTable.clear().draw();
        g_userSettingsTable.rows.add(table_data);
        g_userSettingsTable.columns.adjust().draw();
    }

    // Need this since setting checked in HTML does not leave toggler in correct state
    if (g_userSettings['usingEmailAlerts'])
        document.getElementById('email_alerts_toggler').checked = true;

    if (g_userSettings['usingTelegramAlerts'])
        document.getElementById('telegram_alerts_toggler').checked = true;
}

$(document).on('click', '.toggler', function () {

    var toggler = this;

    // Post settings change to Guindex
    var request = new XMLHttpRequest();

    var data = {};
    var field;
    
    if (this.id == "email_alerts_toggler")
    {
        var field = 'usingEmailAlerts';
    }
    else if (this.id == "telegram_alerts_toggler")
    {
        var field = 'usingTelegramAlerts';
    } 
    else
    {
        // Can't get field
        toggler.checked = !toggler.checked;
        return;
    }

    data[field] = toggler.checked;

    request.open('PATCH', G_API_BASE + 'contributors/' + g_userId +'/', true); 
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    request.send(JSON.stringify(data));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4)
        {
            var response = JSON.parse(request.responseText);

            if (request.status == 200)
            {
                // Success
            }
            else
            {
                // Error: Revert toggler to original state
                displayMessage('Error', response['usingTelegramAlerts'])
                toggler.checked = !toggler.checked;
            }
        }   
    }
});
