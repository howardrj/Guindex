var getDetailedContributorInfo = function ()
{
    // Function to get detailed info about this user using REST API
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'contributors/' + g_userId + '/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    request.send(JSON.stringify({'access_token': g_facebookAccessToken}));

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            g_detailedContributorInfo = JSON.parse(request.responseText);
            g_isStaffMember = g_detailedContributorInfo['is_staff'];
            populateUserSettingsTable();
        }
    }
}

var populateUserSettingsTable = function ()
{
    var user_settings_table_data = [];

    // Email alerts setting
    var email_alerts_list = ['Email Alerts', 
                             "Receive email alerts when new prices and pubs are added to the Guindex.",
                             g_detailedContributorInfo['usingEmailAlerts']
                             ? '<i id="email_alerts_toggler" class="fa fa-3x fa-toggle-on toggler on hoverable"></i>'
                             : '<i id="email_alerts_toggler" class="fa fa-3x fa-toggle-on fa-rotate-180 toggler hoverable"></i>'
                            ];

    user_settings_table_data.push(email_alerts_list);

    // Telgram alerts setting
    var telegram_description = "Receive Telegram alerts when new prices and pubs are added to the Guindex.";

    if (!g_detailedContributorInfo['telegramActivated'])
    {
        telegram_description += " To activate your Telegram account, please add the GuindexBot as a contact using" +
                                " the Telegram app and send: /activate " + g_detailedContributorInfo['telegramActivationKey'] + '.';
    }

    var telegram_alerts_list = ['Telegram Alerts',
                                telegram_description,
                                g_detailedContributorInfo['usingTelegramAlerts']
                                ? '<i id="telegram_alerts_toggler" class="fa fa-3x fa-toggle-on toggler on hoverable"></i>'
                                : '<i id="telegram_alerts_toggler" class="fa fa-3x fa-toggle-on fa-rotate-180 toggler hoverable"></i>'
                                ];

    user_settings_table_data.push(telegram_alerts_list);

    $('#GuindexUserSettingsTable').DataTable({
        responsive: true,
        "paging":   false,
        "ordering": false,
        "searching": false,
        data: user_settings_table_data,
        columns: [
            { title: "Setting" },
            { title: "Description" },
            { title: "Toggle" },
        ]
    });

    $('.toggler').on('click', function () {
        $(this).toggleClass('fa-rotate-180 on');

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
            $(this).toggleClass('fa-rotate-180 on');
            return;
        }

        data[field] = this.classList.contains('on');   

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
                    $('#' + toggler.id).toggleClass('fa-rotate-180 on');
                    displayMessage('Error', response['usingTelegramAlerts'])
                }
            }   
        }
    });
}
