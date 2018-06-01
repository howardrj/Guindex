var getDetailedContributorInfo = function ()
{
    g_detailedContributorInfo = {};

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
            populateUserContributionsTable();
        }
    }
}

var populateUserSettingsTable = function ()
{
    var user_settings_table_data = [];

    var prefix = '<label class="switch">';
    var suffix = '<div id="email_alerts_toggler_div" class="slider round"> </div></label>';

    // Email alerts setting
    var email_alerts_list = ['Email Alerts', 
                             "Receive email alerts when new prices and pubs are added to the Guindex.",
                             prefix + '<input type="checkbox" id="email_alerts_toggler" class="toggler hoverable">' + suffix
                            ];

    user_settings_table_data.push(email_alerts_list);

    // Telgram alerts setting
    var telegram_description = "Receive Telegram alerts when new prices and pubs are added to the Guindex.";

    if (!g_detailedContributorInfo['telegramActivated'])
    {
        telegram_description += " To activate your Telegram account, please add the GuindexBot as a contact using" +
                                " the Telegram app and send: /activate " + g_detailedContributorInfo['telegramActivationKey'] + '.';
    }

    suffix = '<div id="telegram_alerts_toggler_div" class="slider round"> </div></label>';

    var telegram_alerts_list = ['Telegram Alerts',
                                telegram_description,
                                prefix + '<input type="checkbox" id="telegram_alerts_toggler" class="toggler hoverable">' + suffix
                                ];

    user_settings_table_data.push(telegram_alerts_list);

    // Check if table is being drawn from scratch or refreshed
    if (!g_userSettingsTable)
    {
        // Clear log in warning
        var settings_page = document.getElementById('settings_page');

        settings_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        settings_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        g_userSettingsTable = $('#GuindexUserSettingsTable').DataTable({
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
    }
    else
    {
        // Redraw table
        g_userSettingsTable.clear().draw();
        g_userSettingsTable.rows.add(user_settings_table_data);
        g_userSettingsTable.columns.adjust().draw();
    }

    // Need this since setting checked in HTML does not leave toggler in correct state
    if (g_detailedContributorInfo['usingEmailAlerts'])
        document.getElementById('email_alerts_toggler').checked = true;

    if (g_detailedContributorInfo['usingTelegramAlerts'])
        document.getElementById('telegram_alerts_toggler').checked = true;
}

var populateUserContributionsTable = function ()
{
    var table_data = [];

    table_data.push(["Pubs Visited",          g_detailedContributorInfo['pubsVisited']]);
    table_data.push(["Current Verifications", g_detailedContributorInfo['currentVerifications']]);
    table_data.push(["Original Prices",       g_detailedContributorInfo['originalPrices']]);

    // Check if table is being drawn from scratch or refreshed
    if (!g_userContributionsTable)
    {
        // Clear log in warning
        var contributions_page = document.getElementById('contributions_page');

        contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        data_columns = [
            {title: "Statistic", "orderable": false},
            {title: "Value",     "orderable": false},
        ]

        g_userContributionsTable = $('#GuindexContributionsTable').DataTable({
                                    responsive: true,
                                    data: table_data,
                                    columns: data_columns,
                                    paging: false,
                                   });
    }
    else
    {
        // Redraw table
        // TODO Stay on same page table
        g_userContributionsTable.clear().draw();
        g_userContributionsTable.rows.add(table_data);
        g_userContributionsTable.columns.adjust().draw();
    }
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
