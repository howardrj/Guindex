var g_guindexDataTable = null;

function populateGuindexDataTable()
{
    // No need to redraw table since it's already dynamic
    if (g_guindexDataTable)
        return;

    var data_columns = [
        {
            title: "Name",
            data: "name",
            render: function (data, type, row) {

                return '<a target="_blank" href="' + row['mapLink'] + '">' + data + '</a>';
            }
        },
        {
            title: "County",
            data: "county",
        },
        {
            title: "Price",
            data: "lastPrice",
            defaultContent: "N.A.",
        },
        {
            title: "Average Star Rating",
            data: "averageRating",
            render: function (data, type, row) {

                if (!data)
                    return "N.A.";

                var star_rating = Math.round(parseFloat(data));
                var html_string = "";

                for (var i = 0; i < 5; i++)
                {
                    if (i < star_rating)
                    {
                        html_string += '<i class="fa fa-star" aria-hidden="true" stle="color:black"></i>';
                    }
                    else
                    {
                        html_string += '<i class="fa fa-star" aria-hidden="true" style="color:lightgrey"></i>';
                    }
                } 
                return html_string;
            },
            defaultContent: "N.A."
        },
        {
            title: "Last Submitted Date",
            data: "lastSubmissionTime",
            render: function (data, type, row) {

                if (!data)
                    return "N.A.";

                var date_as_list = new Date(data).toString().split(' ');

                var date_pretty_format = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];

                return date_pretty_format;
            },
            defaultContent: "N.A.",
        },
        {
            title: "Submit Price (with Star Rating)",
            data: null,
            orderable: false,
            searchable: false,
            className: "text-center",
            visible: "false",
            render: function (data, type, row) {

                var input_field = '<input class="price_input" type="number" step="0.01" min="0" max="10"/> <br>';

                var stars = "";

                for (var i = 0; i < 5; i++)
                {
                    if (i < 3)
                    {
                        stars += '<i class="fa fa-star guindex_price_star" data-guindex_price_star_id="' + i + '" aria-hidden="true" style="color:black"></i>';
                    }
                    else
                    {
                        stars += '<i class="fa fa-star guindex_price_star" data-guindex_price_star_id="' + i + '" aria-hidden="true" style="color:lightgrey"></i>';
                    }
                }

                var submit_button = '<i class="fa fa-paper-plane submit_price_button" title="Submit Price (only available when logged in)" data-pub_id="' + row['id'] + '"></i>';
                var loader        = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

                return input_field + stars + submit_button + loader;
            },
        },
        {
            title: "Edit Pub",
            data: null,
            orderable: false,
            searchable: false,
            className: "text-center",
            visible: "false",
            render: function (data, type, row) {

                var edit_pub_button = '<i class="fa fa-edit edit_pub_button hoverable" title="Edit pub (only available when logged in)" data-pub_id="' + row['id'] + 
                                      '" data-name="'            +  row['name'] +
                                      '" data-latitude="'        +  row['latitude'] +
                                      '" data-longitude="'       +  row['longitude'] +
                                      '" data-county="'          +  row['county'] +
                                      '" data-closed="'          + (row['closed'] ? '1' : '0') +
                                      '" data-servingGuinness="' + (row['servingGuinness'] ? '1' : '0') +
                                      '"></i>';
                
                return edit_pub_button
            },
        },
        {
            title: "ID",
            data: "id",
            visible: false,
        },
        {
            title: "Latitude",
            data: "latitude",
            visible: false,
        },
        {
            title: "Longitude",
            data: "longitude",
            visible: false,
        },
        {
            title: "Map Link",
            data: "mapLink",
            visible: false,
        },
        {
            title: "Seving Guinness",
            data: "servingGuinness",
            visible: false,
        },
        {
            title: "Closed",
            data: "closed",
            visible: false,
        },
    ]

    g_guindexDataTable = $('#GuindexDataTable').DataTable({
                             "serverSide": true,
                             "ajax": "/api/pubs/?format=datatables",
                             "search": {
                                 "caseInsensitive": true,
                             },
                             "columns": data_columns,
                         });

    if (!g_guindexDataTable.onLogin)
    {
        g_guindexDataTable.onLogin = function () {
            g_guindexDataTable.column(5).visible(true);
            g_guindexDataTable.column(6).visible(true);
        }
    }

    if (g_loggedIn && g_guindexDataTable.onLogin)
    {
        g_guindexDataTable.onLogin();
    }
}

// Add event listeners

$(document).on('click', '.submit_price_button', function () {

    if (this.classList.contains('hoverable'))
    {
        var button = this;

        toggleLoader(button);

        var price  = parseFloat(this.parentNode.getElementsByTagName('input')[0].value);
        var pub_id = parseInt(this.getAttribute('data-pub_id'));

        // POST price to the guindex
        var request = new XMLHttpRequest();
        request.open('POST', G_API_BASE + 'pubs/' + pub_id + '/prices/', true); 

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

        // Get star rating
        var star_rating = 0; 

        var stars = this.parentNode.getElementsByClassName('guindex_price_star');

        for (var i = 0; i < stars.length; i++)
        {
            if (stars[i].style.color.indexOf("black") != -1)
            {
                star_rating++;
            }
        }

        request.send(JSON.stringify({
            'price': price,
            'starRating': star_rating,
        }));

        request.onreadystatechange = function processRequest()
        {
            if (request.readyState == 4)
            {
                var response = JSON.parse(request.responseText);

                if (request.status == 201) // => Created
                {
                    toggleLoader(button);

                    if (g_isStaffMember)
                    {
                        displayMessage("Info", "Thank you. Your submission was successful.");
                    }
                    else
                    {
                        displayMessage("Info", "Thank you. A member of staff will verify your submission shortly.");
                    }

                    // Reload table
                    if (g_guindexDataTable)
                        g_guindexDataTable.ajax.reload();
                }
                else
                {
                    var error_message = response['price'][0];
                    toggleLoader(button);
                    displayMessage("Error", error_message);
                }
            }   
        }
    }
});

$(document).on('input', '.price_input', function () {
            
    var submit_button = this.parentNode.getElementsByClassName('submit_price_button')[0];

    if (this.value && g_loggedIn && g_accessToken && g_isStaffMember != null)
    {
        submit_button.style.color = 'black';
        submit_button.classList.add('hoverable');
    }
    else
    {
        submit_button.style.color = 'gray';
        submit_button.classList.remove('hoverable');
    }
}); 

$(document).on('click', '.edit_pub_button', function () {

    if (!g_loggedIn || !g_accessToken)
    {
        displayMessage("Error", "You must be logged in to edit a pub.");
    }
    else
    {
        // Set form values
        var pub_id = parseInt(this.getAttribute('data-pub_id'));

        document.getElementById('edit_pub_name').value               = this.getAttribute('data-name');
        document.getElementById('edit_pub_latitude').value           = parseFloat(this.getAttribute('data-latitude'));
        document.getElementById('edit_pub_longitude').value          = parseFloat(this.getAttribute('data-longitude'));
        document.getElementById('edit_pub_county').value             = this.getAttribute('data-county');
        document.getElementById('edit_pub_closed').checked           = this.getAttribute('data-closed') == '1';
        document.getElementById('edit_pub_serving_guinness').checked = this.getAttribute('data-servingGuinness') == '1';

        document.getElementById('edit_pub_submit_button').setAttribute('data-pub_id', pub_id);

        // Open modal
        document.getElementById('edit_pub_link').click();
    }
});

$('#edit_pub_submit_button').on('click', function () {

    var button1 = this.parentNode.getElementsByTagName('button')[0];
    var button2 = this.parentNode.getElementsByTagName('button')[1];

    toggleLoader(button1);
    toggleLoader(button2);

    // Send form values in PATCH REST API request
    var id               = this.getAttribute('data-pub_id');
    var name             = document.getElementById('edit_pub_name').value;
    var latitude         = document.getElementById('edit_pub_latitude').value;
    var longitude        = document.getElementById('edit_pub_longitude').value;
    var county           = document.getElementById('edit_pub_county').value;
    var closed           = document.getElementById('edit_pub_closed').checked;
    var serving_guinness = document.getElementById('edit_pub_serving_guinness').checked;

    var request = new XMLHttpRequest();
    request.open('PATCH', G_API_BASE + 'pubs/' + id + '/', true); 

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

    var pub_patch_obj = {
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'county': county,
        'closed': closed,
        'servingGuinness': serving_guinness,
    };

    request.send(JSON.stringify(pub_patch_obj));

    request.onreadystatechange = processRequest;

    function processRequest()
    {
        if (request.readyState == 4) 
        {
            toggleLoader(button1);
            toggleLoader(button2);

            response = JSON.parse(request.responseText);    

            if (request.status == 200)
            {
                if (g_isStaffMember)
                {
                    displayMessage("Info", "Thank you. Your submission was successful.");
                }
                else
                {
                    displayMessage("Info", "Thank you. A member of staff will verify your submission shortly.");
                }
            
                // Reload table
                if (g_guindexDataTable)
                    g_guindexDataTable.ajax.reload();
            }
            else
            {
                // Display errors
                var error_message = '<p>Please fix the following error(s): </p>'

                var error_table = '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';

                error_table += '<tr> <th> Field </th> <th> Error </th> </tr>';

                Object.keys(response).forEach(function(key) {

                    error_table += '<tr>';

                    error_table += '<td>' + key + '</td>';

                    error_table += '<td>' + response[key] + '</td>';

                    error_table += '</tr>';
                });

                error_table += '</tbody></table>';

                displayMessage("Error", error_message + error_table);
            }
        }
    }
});

$(document).on('click', '.guindex_price_star', function () {

    var clicked_star_id = parseInt(this.getAttribute('data-guindex_price_star_id'));

    var stars = this.parentNode.getElementsByClassName('guindex_price_star');

    for (var i = 0; i < stars.length; i++)
    {
        var star_id = parseInt(stars[i].getAttribute('data-guindex_price_star_id')) 

        if (star_id <= clicked_star_id)
        {
            stars[i].style.color = "black";
        }
        else
        {
            stars[i].style.color = "lightgrey";
        }
    }
});
