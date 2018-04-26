(function () {

    var checkPubListForTable = function ()
    {
        if (g_pubsList.length)
        { 
            populateTable();
        }
        else
        {
            // Check later if pub data has been retrived
            setTimeout(checkPubListForTable, 500);
        }
    }

    // Check g_pubsList is populated
    if (g_pubsList.length)
    {
        populateTable();
    }
    else
    {
        checkPubListForTable();
    }

    var populateTable = function ()
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
                // Allows datetime column to be sortbale and still presentable
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
            pub_data.push(input_field + submit_button);

            table_data.push(pub_data.slice());
        } 

        $('#GuindexDataTable').DataTable({
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

        // Add event listeners for price input field
        var input_fields = document.getElementsByClassName('price_input');

        for (var i = 0; i < input_fields.length; i++)
        {
            input_fields[i].addEventListener('input', function (evt) {
                
                var submit_button = evt.target.parentNode.getElementsByClassName('submit_price_button')[0];

                if (evt.target.value && g_loggedIn && g_accessToken)
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
                            if (request.status == 201)
                            {
                                // 201 => Created
                                console.log("Success");

                                // TODO Open success modal and reload table
                                // Message should be different depending on if user is staff or not
                            }
                            else
                            {
                                console.log("Error");

                                // TODO Open Error Modal
                            }
                        }   
                    }
                }
            });
        }
    } 
})();
