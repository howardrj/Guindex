var getPendingContributionsInfo = function ()
{
    getPendingPriceCreates();
    getPendingPubCreates();
    getPendingPubPatches();

    // Clear log in warning
    // Note we have mutliple tables so it's a bit easier to do it here instead of just 
    // before drawing the table.
    var pending_contributions_page = document.getElementById('pending_contributions_page');

    pending_contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
    pending_contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';
}

var getPendingPriceCreates = function ()
{
    // Function to get pending price submissions using REST API
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'guinness/pending/create/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            populatePendingPriceCreateTable(JSON.parse(request.responseText));
        }
    }
}

var getPendingPubCreates = function ()
{
    // Function to get pending new pub submissions using REST API
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'pubs/pending/create/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            populatePendingPubCreateTable(JSON.parse(request.responseText));
        }
    }
}

var getPendingPubPatches = function ()
{
    // Function to get pending pub updates using REST API
    var request = new XMLHttpRequest();

    request.open('GET', G_API_BASE + 'pubs/pending/patch/', true);

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            populatePendingPubPatchTable(JSON.parse(request.responseText));
        }
    }
}

var populatePendingPriceCreateTable = function (prices)
{
    // Check relevant objects are loaded
    if (!g_pubsList.length || (g_isStaffMember && !g_contributorsList.length))
    {
        setTimeout(populatePendingPriceCreateTable, 500, prices);
        return;
    }        

    var pending_price_create_table_data = [];

    for (var i = 0; i < prices.length; i++)
    {
        var price_data = [];

        // Pub name
        var pub_id = parseInt(prices[i]['pub']);
        var pub    = $.grep(g_pubsList, function(obj) { return obj['id'] === pub_id;})[0];

        var pub_name_link = '<a target="_blank" href="' + pub['mapLink'] + '">' + pub['name'] + '</a>';

        price_data.push(pub_name_link);
    
        // County
        var pub_county = pub['county'];
        price_data.push(pub_county);
    
        // Price
        price_data.push(prices[i]['price']);

        // Contribution time
        // This is ugly but it works
        // Allows datetime column to be sortable and still presentable
        // Change at your peril

        var date = new Date(prices[i]['creationDate']);
        var date_as_list = date.toString().split(' ');

        var date_pretty_format   = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];
        var date_sortable_format = date[3] + ("0" + (date.getMonth() + 1)).slice(-2) + ("0" + date.getDate()).slice(-2);

        price_data.push('<span style="display:none">' + date_sortable_format + '</span>' + date_pretty_format);
        
        if (g_isStaffMember)
        {
            // Contributor
            var contributor_id = parseInt(prices[i]['creator']);
            var contributor    = $.grep(g_contributorsList, function(obj) { return obj['id'] === contributor_id;})[0];

            price_data.push(contributor['username']);

            // Approve/Reject button
            var approve_button = '<i data-obj_id="' + prices[i]['id'] + '"data-table_type="pending_price_create" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
            var reject_button  = '<i data-obj_id="' + prices[i]['id'] + '"data-table_type="pending_price_create" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
            var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

            price_data.push(approve_button + '<span class="slash"> / </span>' + reject_button + loader);
        }

        pending_price_create_table_data.push(price_data);
    }

    // Check if table is being drawn from scratch or refreshed
    if (!g_pendingPriceCreateTable)
    {
        var data_columns = [{ title: "Pub" },
                            { title: "County" },
                            { title: "Price (€)" },
                            { title: "Submission Date" }];

        if (g_isStaffMember)
        {
            data_columns.push({ title: "Submitted By" });
            data_columns.push({ title: "Approve / Reject", "className": "text-center", "orderable": false });
        }

        g_pendingPriceCreateTable = $('#GuindexPendingGuinnessCreateTable').DataTable({
                                        responsive: true,
                                        data: pending_price_create_table_data,
                                        columns: data_columns,
                                   });
    }
    else
    {
        // Redraw table
        g_pendingPriceCreateTable.clear().draw();
        g_pendingPriceCreateTable.rows.add(pending_price_create_table_data);
        g_pendingPriceCreateTable.columns.adjust().draw();
    }
}

var populatePendingPubCreateTable = function (pubs)
{
    // Check relevant objects are loaded
    if (g_isStaffMember && !g_contributorsList.length)
    {
        setTimeout(populatePendingPubCreateTable, 500, prices);
        return;
    }        

    var pending_pub_create_table_data = [];

    for (var i = 0; i < pubs.length; i++)
    {
        var pub_data = [];

        // Pub name
        var pub_name_link = '<a target="_blank" href="' + pubs[i]['mapLink'] + '">' + pubs[i]['name'] + '</a>';

        pub_data.push(pub_name_link);

        // County
        var pub_county = pubs[i]['county'];
        pub_data.push(pub_county);

        // Contribution time
        // This is ugly but it works
        // Allows datetime column to be sortable and still presentable
        // Change at your peril

        var date = new Date(pubs[i]['creationDate']);
        var date_as_list = date.toString().split(' ');

        var date_pretty_format   = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];
        var date_sortable_format = date[3] + ("0" + (date.getMonth() + 1)).slice(-2) + ("0" + date.getDate()).slice(-2);

        pub_data.push('<span style="display:none">' + date_sortable_format + '</span>' + date_pretty_format);
        
        if (g_isStaffMember)
        {
            // Contributor
            var contributor_id = parseInt(pubs[i]['creator']);
            var contributor    = $.grep(g_contributorsList, function(obj) { return obj['id'] === contributor_id;})[0];

            pub_data.push(contributor['username']);

            // Approve/Reject button
            var approve_button = '<i data-obj_id="' + pubs[i]['id'] + '"data-table_type="pending_pub_create" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
            var reject_button  = '<i data-obj_id="' + pubs[i]['id'] + '"data-table_type="pending_pub_create" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
            var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

            pub_data.push(approve_button + '<span class="slash"> / </span>' + reject_button + loader);
        }

        pending_pub_create_table_data.push(pub_data);
    }

    if (!g_pendingPubCreateTable)
    {
        var data_columns =  [{ title: "Name" },
                             { title: "County" },
                             { title: "Submission Date" }];

        if (g_isStaffMember)
        {
            data_columns.push({ title: "Submitted By" });
            data_columns.push({ title: "Approve / Reject", "className": "text-center", "orderable": false });
        }

        g_pendingPubCreateTable = $('#GuindexPendingPubCreateTable').DataTable({
                                    responsive: true,
                                    data: pending_pub_create_table_data,
                                    columns: data_columns,
                                  });
    }
    else
    {
        // Redraw table
        g_pendingPubCreateTable.clear().draw();
        g_pendingPubCreateTable.rows.add(pending_pub_create_table_data);
        g_pendingPubCreateTable.columns.adjust().draw();
    }
}

var populatePendingPubPatchTable = function (pubs)
{
    // Check relevant objects are loaded
    if (!g_pubsList.length || (g_isStaffMember && !g_contributorsList.length))
    {
        setTimeout(populatePendingPubPatchTable, 500, pubs);
        return;
    }        

    var pending_pub_patch_table_data = [];

    for (var i = 0; i < pubs.length; i++)
    {
        var pub_data = [];
        var cloned_pub = $.grep(g_pubsList, function(obj) { return obj['id'] === pubs[i]['clonedFrom'];})[0];

        // Pub name
        var pub_name_link = '<a target="_blank" href="' + cloned_pub['mapLink'] + '">' + cloned_pub['name'] + '</a>';

        pub_data.push(pub_name_link);

        // County
        var pub_county = cloned_pub['county'];
        pub_data.push(pub_county);

        // Changed fields
        var changed_fields = '<table border="0"> <tbody>';

        if (cloned_pub['name'] != pubs[i]['name'])
        {
            changed_fields += '<tr>';

            changed_fields += '<td> Name: </td>';
            changed_fields += '<td>' + cloned_pub['name'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['name'] + '</td>';

            changed_fields += '</tr>';
        }

        if (cloned_pub['county'] != pubs[i]['county'])
        {
            changed_fields += '<tr>';

            changed_fields += '<td> County: </td>';
            changed_fields += '<td>' + cloned_pub['county'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['county'] + '</td>';

            changed_fields += '</tr>';
        }

        if (cloned_pub['latitude'] != pubs[i]['latitude'])
        {
            changed_fields += '<tr>';

            changed_fields += '<td> Latitude: </td>';
            changed_fields += '<td>' + cloned_pub['latitude'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['latitude'] + '</td>';

            changed_fields += '</tr>';
        }

        if (cloned_pub['longitude'] != pubs[i]['longitude'])
        {
            changed_fields += '<tr>';

            changed_fields += '<td> Longitude: </td>';
            changed_fields += '<td>' + cloned_pub['longitude'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['longitude'] + '</td>';

            changed_fields += '</tr>';
        }

        if (cloned_pub['closed'] != pubs[i]['closed'])
        {
            changed_fields += '<tr>';
            changed_fields += '<td> Closed: </td>';
            changed_fields += '<td>' + cloned_pub['closed'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['closed'] + '</td>';
            changed_fields += '</tr>';
        }

        if (cloned_pub['servingGuinness'] != pubs[i]['servingGuinness'])
        {
            changed_fields += '<tr>';
            changed_fields += '<td> Serving Guinness: </td>';
            changed_fields += '<td>' + cloned_pub['servingGuinness'] + '</td>';
            changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
            changed_fields += '<td>'+ pubs[i]['servingGuinness'] + '</td>';
            changed_fields += '</tr>';
        }
        
        changed_fields += "</tbody></table>";

        pub_data.push(changed_fields);

        // Contribution time
        // This is ugly but it works
        // Allows datetime column to be sortable and still presentable
        // Change at your peril

        var date = new Date(pubs[i]['creationDate']);
        var date_as_list = date.toString().split(' ');

        var date_pretty_format   = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];
        var date_sortable_format = date[3] + ("0" + (date.getMonth() + 1)).slice(-2) + ("0" + date.getDate()).slice(-2);

        pub_data.push('<span style="display:none">' + date_sortable_format + '</span>' + date_pretty_format);
        
        if (g_isStaffMember)
        {
            // Contributor
            var contributor_id = parseInt(pubs[i]['creator']);
            var contributor    = $.grep(g_contributorsList, function(obj) { return obj['id'] === contributor_id;})[0];

            pub_data.push(contributor['username']);

            // Approve/Reject button
            var approve_button = '<i data-obj_id="' + pubs[i]['id'] + '"data-table_type="pending_pub_patch" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
            var reject_button  = '<i data-obj_id="' + pubs[i]['id'] + '"data-table_type="pending_pub_patch" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
            var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

            pub_data.push(approve_button + '<span class="slash"> / </span>' + reject_button + loader);
        }

        pending_pub_patch_table_data.push(pub_data);
    }

    if (!g_pendingPubPatchTable)
    {
        var data_columns = [{ title: "Name" },
                            { title: "County" },
                            { title: "Changed Fields", "className": "text-center", "orderable": false },
                            { title: "Submission Date" }];

        if (g_isStaffMember)
        {
            data_columns.push({ title: "Submitted By" });
            data_columns.push({ title: "Approve / Reject", "className": "text-center", "orderable": false });
        }

        g_pendingPubPatchTable = $('#GuindexPendingPubPatchTable').DataTable({
                                    responsive: true,
                                    data: pending_pub_patch_table_data,
                                    columns: data_columns,
                                 });
    }
    else
    {
        // Redraw table
        g_pendingPubPatchTable.clear().draw();
        g_pendingPubPatchTable.rows.add(pending_pub_patch_table_data);
        g_pendingPubPatchTable.columns.adjust().draw();
    }
}

// Add event listeners for pending contributions buttons
$(document).on('click', '.pending_contribution_button', function () {

    if (!g_loggedIn || !g_accessToken)
    {
        displayMessage("Error", "You must be logged in.");
        return;
    }

    var table_type = this.getAttribute('data-table_type');
    var obj_id     = this.getAttribute('data-obj_id');
    var method     = this.getAttribute('data-action');
    var buttons    = this.parentNode.getElementsByClassName('pending_contribution_button');

    if (method.indexOf("reject") != -1)
    {
        if (this.id.indexOf("final_reject_submit_button") != -1)
        {
            // Get correct button to replace with loader
            var table_type_buttons = document.querySelectorAll('[data-table_type="' + table_type + '"]');

            // Overwrite buttons
            for (var i = 0; i < table_type_buttons.length; i++)
            {
                if (table_type_buttons[i].getAttribute('data-obj_id') == obj_id)
                {
                    buttons = table_type_buttons[i].parentNode.getElementsByClassName('pending_contribution_button');
                    break;
                }
            }

            // Close reject reason modal
            document.getElementById('reject_reason_link').click();
        }
        else
        {
            var reject_submit_button = document.getElementById('final_reject_submit_button');

            reject_submit_button.setAttribute('data-table_type', table_type);    
            reject_submit_button.setAttribute('data-obj_id', obj_id);    
            reject_submit_button.setAttribute('data-action', method);    
        
            // Open reject reason modal
            document.getElementById('reject_reason_link').click();
            return;
        }
    }

    var request = new XMLHttpRequest();

    if (table_type.indexOf("pending_price_create") != -1)
    {
        request.open('PATCH', G_API_BASE + 'guinness/pending/create/' + obj_id + '/', true); 
    }
    else if (table_type.indexOf("pending_pub_create") != -1)
    {
        request.open('PATCH', G_API_BASE + 'pubs/pending/create/' + obj_id + '/', true); 
    }
    else if (table_type.indexOf("pending_pub_patch") != -1)
    {
        request.open('PATCH', G_API_BASE + 'pubs/pending/patch/' + obj_id + '/', true); 
    }
    else
    {
        return;
    }

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    if (method.indexOf("approve") != -1)
    {
        request.send(JSON.stringify({'approved': method == "approve"}));
    }
    else
    {
        var reject_reason = document.getElementById('reject_reason_text_area').value;

        request.send(JSON.stringify({'approved': method == "approve", 'rejectReason': reject_reason}));
    }

    toggleLoader(buttons[0]);
    toggleLoader(buttons[1]);
    buttons[0].parentNode.getElementsByClassName('slash')[0].style.display = 'none';

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            if (method.indexOf("approve") != -1)
            {
                displayMessage("Info", "Successfully approved pending contribution.");
                buttons[0].parentNode.innerHTML = "Approved";
            }
            else
            {
                displayMessage("Info", "Successfully rejected pending contribution.");
                buttons[0].parentNode.innerHTML = "Rejected";
            }

            // Reload tables
            getPubInfo();
            initMap();
            getStats();
            getContributorInfo();
            getDetailedContributorInfo();
            getPendingContributionsInfo();
        }
        else
        {
            displayMessage("Error", "Failed to " + method + " pending contribution.");
            toggleLoader(buttons[0]);
            toggleLoader(buttons[1]);
            buttons[0].parentNode.getElementsByClassName('slash')[0].style.display = 'inline';
        }
    }
});
