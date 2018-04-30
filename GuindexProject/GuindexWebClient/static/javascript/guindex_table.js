var populateGuindexTable = function ()
{
    var table_data = [];
    
    // Copy global list
    var pubs_list = g_pubsList.slice();

    // Sort alphabetically
    pubs_list.sort(function(a, b) {
        return a['name'].localeCompare(b['name']);
    });

    // Add to pubs list
    for (var i = 0; i < pubs_list.length; i++)
    {
        pub_data = [];

        // Append pub name
        var pub_name_link = '<a target="_blank" href="' + pubs_list[i]['mapLink'] + '">' + pubs_list[i]['name'] + '</a>';
        pub_data.push(pub_name_link);

        // Append price
        if (pubs_list[i]['prices'].length)
        {
            pub_data.push(pubs_list[i]['prices'].slice(-1)[0]['price']);
        }
        else
        {
            pub_data.push('-');
        } 

        // Append last submitted by
        if (pubs_list[i]['prices'].length)
        {
            pub_data.push(pubs_list[i]['prices'].slice(-1)[0]['creatorName']);
        }
        else
        {
            pub_data.push('-');
        } 

        // Append last submitted date
        if (pubs_list[i]['prices'].length)
        {
            // This is ugly but it works
            // Allows datetime column to be sortable and still presentable
            // Change at your peril

            var date = new Date(pubs_list[i]['prices'].slice(-1)[0]['creationDate']);
            var date_as_list = date.toString().split(' ');

            var date_pretty_format   = date_as_list[0] + ' ' + date_as_list[2] + ' ' + date_as_list[1] + ' ' + date_as_list[3];
            var date_sortable_format = date[3] + ("0" + (date.getMonth() + 1)).slice(-2) + ("0" + date.getDate()).slice(-2);

            pub_data.push('<span style="display:none">' + date_sortable_format + '</span>' + date_pretty_format);
        }
        else
        {
            pub_data.push('-');
        } 

        // Append submit price button
        var input_field   = '<input class="price_input" type="number" step="0.01" min="0" max="10"/>';
        var submit_button = '<i class="fa fa-paper-plane submit_price_button" title="Submit Price (only available when logged in)" data-pub_id="' + pubs_list[i]['id'] + '"></i>';
        var loader        = '<i class="fa fa-spinner fa-spin guindex_web_client_loader"></i>';

        pub_data.push(input_field + submit_button + loader);

        table_data.push(pub_data.slice());
    } 

    // Check if table is being drawn from scratch or refreshed
    if (!g_guindexDataTable)
    {
        g_guindexDataTable = $('#GuindexDataTable').DataTable({
                                responsive: true,
                                data: table_data,
                                columns: [
                                    {title: "Name"},
                                    {title: "Price (€)"},
                                    {title: "Last Submitted By"},
                                    {title: "Last Submitted Date"},
                                    {title: "Submit Price", "className": "text-center", "orderable": false},
                                ] 
                            });
    }
    else
    {
        // Redraw table
        datatable.clear().draw();
        datatable.rows.add(NewlyCreatedData); // Add new data
        datatable.columns.adjust().draw(); // Redraw the DataTable
      
    }

    // Add event listeners for price input field
    var input_fields = document.getElementsByClassName('price_input');

    for (var i = 0; i < input_fields.length; i++)
    {
        input_fields[i].addEventListener('input', function (evt) {
            
            var submit_button = evt.target.parentNode.getElementsByClassName('submit_price_button')[0];

            if (evt.target.value && g_loggedIn && g_accessToken && g_isStaffMember != null)
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
    }

    // Add event listeners for price submit buttons
    var submit_price_buttons = document.getElementsByClassName('submit_price_button'); 

    for (var i = 0; i < submit_price_buttons.length; i++)
    {
        submit_price_buttons[i].addEventListener('click', function (evt) {
        
            if (evt.target.classList.contains('hoverable'))
            {
                var button = evt.target;

                toggleLoader(button);

                var price  = parseFloat(evt.target.parentNode.getElementsByTagName('input')[0].value);
                var pub_id = parseInt(evt.target.getAttribute('data-pub_id'));

                // POST price to the guindex
                var request = new XMLHttpRequest();
                request.open('POST', G_API_BASE + 'guinness/', true); 

                request.setRequestHeader('Content-Type', 'application/json');
                request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

                request.send(JSON.stringify({'pub': pub_id, 'price': price}));

                request.onreadystatechange = function processRequest()
                {
                    if (request.readyState == 4)
                    {
                        var response = JSON.parse(request.responseText);

                        console.log(response);

                        if (request.status == 201) // => Created
                        {
                            toggleLoader(button);

                            if (g_isStaffMember)
                            {
                                displayMessage("Info", "Thank you. Your submission was successful.");
                            }
                            else
                            {
                                displayMessage("Info", "Thank you. A member of staff will verify your submision shortly.");
                            }
                                
                            // Reload relevant tables
                            populateGuindexTableUsingRestApi();
                            initMap();
                            getContributorInfo();
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
    }
} 
