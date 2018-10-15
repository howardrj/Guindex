var g_pendingContributionsTablesRendered = false;

function populatePendingContributionsTables ()
{
    if (g_isStaffMember == false)
        return;

    if (g_loggedIn)
    {
        // Clear log in warning
        // Note we have mutliple tables so it's a bit easier to do it here instead of just 
        // before drawing the table.
        var pending_contributions_page = document.getElementById('pending_contributions_page');

        pending_contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        pending_contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';
    }
    else
    {
        return;
    }

    if (g_pendingContributionsTablesRendered)
        return;

    populatePendingPriceCreatesTable();
    populatePendingPubCreatesTable();
    populatePendingPubPatchesTable();

    g_pendingContributionsTablesRendered = true;
}

var g_guindexPendingPriceCreatesTable = null;

function populatePendingPriceCreatesTable ()
{
    // No need to redraw table since it's already dynamic
    if (g_guindexPendingPriceCreatesTable)
        return;

    var data_columns = [
        {
            title: "ID",
            data: 'id',
        },
        {
            title: "Pub",
            data: "pubName",
            orderable: false,
            searchable: false,
        },
        {   
            title: "County",
            data: "pubCounty",
            orderable: false,
            searchable: false,
        },
        {
            title: "Price",
            data: "price",
        },
        {
            title: "Contributor",
            data: "creatorName",
            orderable: false,
            searchable: false,
        },
        {
            title: "Submission Time",
            data: "creationDate",
            render: function (data, type, row) {

                var date_as_list = new Date(data).toString().split(' ');

                var date_pretty_format = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];

                return date_pretty_format;
            },
        },  
        {
            title: "Approve / Reject",
            data: null,
            orderable: false,
            searchable: false,
            className: "text-center",
            render: function (data, type, row) {

                var approve_button = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_price_create" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
                var reject_button  = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_price_create" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
                var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

                return approve_button + '<span class="slash"> / </span>' + reject_button + loader;
            },
        },
    ]

    g_guindexPendingPriceCreatesTable = $('#GuindexPendingGuinnessCreateTable').DataTable({
                                            "serverSide": true,
                                            "ajax": {
                                                "url": "/api/pending_price_creates/?format=datatables",
                                                "beforeSend": function(xhr) {
                                                    xhr.setRequestHeader("Authorization", 'Token ' + g_accessToken);
                                                },
                                            },
                                            "searching": false,
                                            "columns": data_columns,
                                        });
}

var g_guindexPendingPubCreatesTable = null;

function populatePendingPubCreatesTable ()
{
    // No need to redraw table since it's already dynamic
    if (g_guindexPendingPubCreatesTable)
        return;

    var data_columns = [
        {
            title: "ID",
            data: 'id',
        },
        {
            title: "Name",
            data: "name",
        },
        {   
            title: "County",
            data: "county",
        },
        {
            title: "Closed?",
            data: "closed",
            render: function (data, type, row) {

                return data == true ? "Yes" : "No";
            },
        },
        {
            title: "Serving Guinness?",
            data: "servingGuinness",
            render: function (data, type, row) {

                return data == true ? "Yes" : "No";
            },
        },
        {
            title: "Contributor",
            data: "creatorName",
            orderable: false,
            searchable: false,
        },
        {
            title: "Submission Time",
            data: "creationDate",
            render: function (data, type, row) {

                var date_as_list = new Date(data).toString().split(' ');

                var date_pretty_format = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];

                return date_pretty_format;
            },
        },  
        {
            title: "Approve / Reject",
            data: null,
            orderable: false,
            searchable: false,
            className: "text-center",
            render: function (data, type, row) {

                var approve_button = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_pub_create" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
                var reject_button  = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_pub_create" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
                var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

                return approve_button + '<span class="slash"> / </span>' + reject_button + loader;
            },
        },
    ]

    g_guindexPendingPubCreatesTable = $('#GuindexPendingPubCreateTable').DataTable({
                                          "serverSide": true,
                                          "ajax": {
                                              "url": "/api/pending_pub_creates/?format=datatables",
                                              "beforeSend": function(xhr) {
                                                  xhr.setRequestHeader("Authorization", 'Token ' + g_accessToken);
                                              },
                                          },
                                          "searching": false,
                                          "columns": data_columns,
                                      });
}

var g_guindexPendingPubPatchesTable = null;

function populatePendingPubPatchesTable ()
{
    // No need to redraw table since it's already dynamic
    if (g_guindexPendingPubPatchesTable)
        return;

    var data_columns = [
        {
            title: "ID",
            data: 'id',
        },
        {
            title: "Original Pub Name",
            data: "pubNameOrig",
            orderable: false,
            searchable: false,
        },
        {   
            title: "Original County",
            data: "pubCountyOrig",
            orderable: false,
            searchable: false,
        },
        {
            title: "Contributor",
            data: "creatorName",
            orderable: false,
            searchable: false,
        },
        {
            title: "Submission Time",
            data: "creationDate",
            render: function (data, type, row) {

                var date_as_list = new Date(data).toString().split(' ');

                var date_pretty_format = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];

                return date_pretty_format;
            },
        },  
        {
            title: "Proposed Changes",
            data: "proposedPatches",
            orderable: false,
            searchable: false,
            render: function (data, type, row) {

                var changed_fields = '<table border="0"> <tbody>';
                for (var key in data)
                {
                    console.log(key);
                    console.log(data[key][0]);
                    console.log(data[key][1]);
                    changed_fields += '<tr>';
                    changed_fields += '<td> <b>' + key + ': </b></td>';
                    changed_fields += '<td>' + data[key][0] + '</td>';
                    changed_fields += '<td> <i class="fa fa-arrow-right"></i> </td>';
                    changed_fields += '<td>'+ data[key][1] + '</td>';
                    changed_fields += '</tr>';
                }

                changed_fields += '</tbody></table>';
                return changed_fields;
            },
        },
        {
            title: "Approve / Reject",
            data: null,
            orderable: false,
            searchable: false,
            className: "text-center",
            render: function (data, type, row) {

                var approve_button = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_pub_patch" data-action="approve" class="fa fa-check pending_contribution_button hoverable"></i>';
                var reject_button  = '<i data-obj_id="' + row['id'] + '"data-table_type="pending_pub_patch" data-action="reject"  class="fa fa-times pending_contribution_button hoverable"></i>';
                var loader         = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

                return approve_button + '<span class="slash"> / </span>' + reject_button + loader;
            },
        },
    ]

    g_guindexPendingPubPatchesTable = $('#GuindexPendingPubPatchTable').DataTable({
                                          "serverSide": true,
                                          "ajax": {
                                              "url": "/api/pending_pub_patches/?format=datatables",
                                              "beforeSend": function(xhr) {
                                                  xhr.setRequestHeader("Authorization", 'Token ' + g_accessToken);
                                              },
                                          },
                                          "searching": false,
                                          "columns": data_columns,
                                      });
}

// Add event listeners for pending contributions buttons
$(document).on('click', '.pending_contribution_button', function () {

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
        request.open('PATCH', G_API_BASE + 'pending_price_creates/' + obj_id + '/', true); 
    }
    else if (table_type.indexOf("pending_pub_create") != -1)
    {
        request.open('PATCH', G_API_BASE + 'pending_pub_creates/' + obj_id + '/', true); 
    }
    else if (table_type.indexOf("pending_pub_patch") != -1)
    {
        request.open('PATCH', G_API_BASE + 'pending_pub_patches/' + obj_id + '/', true); 
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
