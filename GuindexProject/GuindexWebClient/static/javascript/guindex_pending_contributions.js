class GuindexPendingContributionsManager
{
    static singleton = null;

    constructor (user)
    {
        if (GuindexPendingContributionsManager.singleton)
            throw new Error("Cannot have more than one GuindexPendingContributionsManager instance");

        GuindexPendingContributionsManager.singleton = null;
        this.user = user;
        this.tables_rendered = false;

        this.pending_price_creates_table = new GuindexPendingPriceCreatesTable(this);
        this.pending_pub_creates_table = new GuindexPendingPubCreatesTable(this);
        this.pending_pub_patches_table = new GuindexPendingPubPatches(this);

        this._add_on_pending_contribution_decision_button_clicked_cb();
    }

    _add_on_pending_contribution_decision_button_clicked_cb ()
    {
        $(document).on('click',
                       '.pending_contribution_button',
                       this._on_pending_contribution_decision_button_clicked_cb);

    }

    _on_pending_contribution_decision_button_clicked_cb ()
    {
        let table_type = this.getAttribute('data-table_type');
        let obj_id     = this.getAttribute('data-obj_id');
        let method     = this.getAttribute('data-action');
        let buttons    = this.parentNode.getElementsByClassName('pending_contribution_button');

        let mgr = GuindexPendingContributionsManager.singleton;
        let user = mgr.user;

        if (method.indexOf("reject") != -1)
        {
            if (this.id.indexOf("final_reject_submit_button") == -1)
            {
                let reject_submit_button = document.getElementById('final_reject_submit_button');

                reject_submit_button.setAttribute('data-table_type', table_type);    
                reject_submit_button.setAttribute('data-obj_id', obj_id);    
                reject_submit_button.setAttribute('data-action', method);    
            
                // Open reject reason modal
                document.getElementById('reject_reason_link').click();
                return;
            }

            // Close reject reason modal
            document.getElementById('reject_reason_link').click();
        }

        let url = "";
        let post_data = {};

        if (table_type.indexOf("pending_price_create") != -1)
            url = user.api_base + 'pending_price_creates/' + obj_id + '/';
        else if (table_type.indexOf("pending_pub_create") != -1)
            url = user.api_base + 'pending_pub_creates/' + obj_id + '/';
        else if (table_type.indexOf("pending_pub_patch") != -1)
            url = user.api_base + 'pending_pub_patches/' + obj_id + '/';
        else
            return;

        if (method.indexOf("approve") != -1)
        {
            post_data['approved'] = (method == "approve");
        }
        else
        {
            let reject_reason = document.getElementById('reject_reason_text_area').value;

            post_data['approved'] = (method == "approve");
            post_data['reject_reason'] = reject_reason;
        }

        mgr._post_pending_contribution_decision (url,
                                                 method,
                                                 post_data,
                                                 buttons)
    }

    async _post_pending_contribution_decision (url,
                                               method,
                                               post_data,
                                               buttons) // tick and x buttons
    {

        guindex_toggle_loader(buttons[0]);
        guindex_toggle_loader(buttons[1]);

        buttons[0].parentNode.getElementsByClassName('slash')[0].style.display = 'none';

        let response = await fetch(url, 
                                   {
                                       method: 'PATCH',
                                       headers: {
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Token ' + this.user.access_token,
                                       },
                                       body: JSON.stringify(post_data),
                                   });

        
        if (response.status == 200)
        {
            if (method.indexOf("approve") != -1)
            {
                guindex_display_message("Info",
                                        "Successfully approved pending contribution.");

                buttons[0].parentNode.innerHTML = "Approved";
            }
            else
            {
                guindex_display_message("Info",
                                        "Successfully rejected pending contribution.");

                buttons[0].parentNode.innerHTML = "Rejected";
            }
        }
        else
        {
             guindex_display_message("Error",
                                     "Failed to " + method + " pending contribution.");

             guindex_toggle_loader(buttons[0]);
             guindex_toggle_loader(buttons[1]);

             buttons[0].parentNode.getElementsByClassName('slash')[0].style.display = 'inline';
        }
    }

    populate_tables ()
    {
        let pending_contributions_page = document.getElementById('pending_contributions_page');
        let mgr = GuindexPendingContributionsManager.singleton;
        let user = mgr.user;

        if (!user.is_staff)
            return;

        if (!user.logged_in())
            return;

        // Clear log in warning
        // Note we have mutliple tables so it's a bit easier to do it here instead of just 
        // before drawing the table.
        pending_contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        pending_contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        if (mgr.tables_rendered)
            return;

        mgr.pending_price_creates_table.populate();
        mgr.pending_pub_creates_table.populate();
        mgr.pending_pub_patches_table.populate();

        mgr.tables_rendered = true;
    }
}

class GuindexPendingPubPatchesTable
{
    static singleton = null;

    constructor (mgr)
    {
        if (GuindexPendingPubPatchesTable.singleton)
            throw new Error("Cannot have more than one GuindexPendingPubPatchesTable instance");

        this.mgr = mgr;
        this.user = mgr.user;
        this.rendered = false;
        this.data_table = null;
    }

    populate ()
    {
        // No need to redraw table since it's already dynamic
        if (this.data_table)
            return;

        var data_columns = [
            {
                title: "ID",
                data: 'id',
            },
            {
                title: "Original Pub Name",
                data: "pub_name_orig",
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return '<a target="_blank" href="' + row['mapLink'] + '">' + data + '</a>';
                }
            },
            {
                title: "Map Link",
                data: "map_link",
                visible: false,
            },
            {   
                title: "Original County",
                data: "pub_county_orig",
                orderable: false,
                searchable: false,
            },
            {
                title: "Contributor",
                data: "creator_name",
                orderable: false,
                searchable: false,
            },
            {
                title: "Submission Time",
                data: "creation_date",
                render: function (data, type, row) {

                    var date_as_list = new Date(data).toString().split(' ');

                    var date_pretty_format = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];

                    return date_pretty_format;
                },
            },  
            {
                title: "Proposed Changes",
                data: "proposed_patches",
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

        this.data_table = $('#GuindexPendingPubPatchTable').DataTable({
                              "serverSide": true,
                              "ajax": {
                                  "url": "/api/pending_pub_patches/?format=datatables",
                                  "beforeSend": function(xhr) {
                                      xhr.setRequestHeader("Authorization", 'Token ' + this.user.access_token);
                                  },
                              },
                              "searching": false,
                              "columns": data_columns,
                          });
    }
}

class GuindexPendingPubCreatesTable
{
    static singleton = null;

    constructor (mgr)
    {
        if (GuindexPendingPubCreatesTable.singleton)
            throw new Error("Cannot have more than one GuindexPendingPubCreatesTable instance");

        this.mgr = mgr;
        this.user = mgr.user;
        this.rendered = false;
        this.data_table = null;
    }

    populate ()
    {
        // No need to redraw table since it's already dynamic
        if (this.data_table)
            return;

        var data_columns = [
            {
                title: "ID",
                data: 'id',
            },
            {
                title: "Name",
                data: "name",
                render: function (data, type, row) {
                    return '<a target="_blank" href="' + row['mapLink'] + '">' + data + '</a>';
                }
            },
            {
                title: "Map Link",
                data: "map_link",
                visible: false,
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
                data: "serving_guinness",
                render: function (data, type, row) {

                    return data == true ? "Yes" : "No";
                },
            },
            {
                title: "Contributor",
                data: "creator_name",
                orderable: false,
                searchable: false,
            },
            {
                title: "Submission Time",
                data: "creation_date",
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

        this.data_table = $('#GuindexPendingPubCreateTable').DataTable({
                              "serverSide": true,
                              "ajax": {
                                  "url": "/api/pending_pub_creates/?format=datatables",
                                  "beforeSend": function(xhr) {
                                      xhr.setRequestHeader("Authorization", 'Token ' + this.user.access_token);},
                                  },
                              "searching": false,
                              "columns": data_columns
                          });
    }
}

class GuindexPendingPriceCreatesTable
{
    static singleton = null;

    constructor (mgr)
    {
        if (GuindexPendingPriceCreatesTable.singleton)
            throw new Error("Cannot have more than one GuindexPendingPriceCreatesTable instance");

        this.mgr = mgr;
        this.user = mgr.user;
        this.rendered = false;
        this.data_table = null;
    }

    populate ()
    {
        // No need to redraw table since it's already dynamic
        if (this.data_table)
            return;

        var data_columns = [
            {
                title: "ID",
                data: 'id',
            },
            {
                title: "Pub",
                data: "pub_name",
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return '<a target="_blank" href="' + row['pub_map_link'] + '">' + data + '</a>';
                }
            },
            {
                title: "Map Link",
                data: "pub_map_link",
                visible: false,
            },
            {   
                title: "County",
                data: "pub_county",
                orderable: false,
                searchable: false,
            },
            {
                title: "Price",
                data: "price",
            },
            {
                title: "Contributor",
                data: "creator_name",
                orderable: false,
                searchable: false,
            },
            {
                title: "Submission Time",
                data: "creation_date",
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

        this.data_table = $('#GuindexPendingGuinnessCreateTable').DataTable({
                              "serverSide": true,
                              "ajax": {
                                         "url": "/api/pending_price_creates/?format=datatables",
                                         "beforeSend": function(xhr) {
                                             xhr.setRequestHeader("Authorization", 'Token ' + this.user.access_token);},
                                      },
                              "searching": false,
                              "columns": data_columns
                          });
    }
}


(function ()
{
    let mgr = new GuindexPendingContributionsManager(g_guindex_user);

    document.getElementById('pending_contributions_page').addEventListener('tab_display',
                                                                           mgr.populate_tables);

    document.getElementById('pending_contributions_page').addEventListener('on_login',
                                                                           mgr.populate_tables); 

})();
