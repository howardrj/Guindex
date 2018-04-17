var G_API_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';

(function () {

    var g_pubData = [];

    // Fetch pub data
    var request = new XMLHttpRequest();
    request.open('GET', G_API_BASE + 'pubs/', true); 

    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.send(null);

    request.onreadystatechange = function processRequest()
    {
        if (request.readyState == 4 && request.status == 200)
        {
            // Parse pubs
            var pubs_list = JSON.parse(request.responseText);

            // Sort alphabetically
            pubs_list.sort(function(a, b) {
                return a['name'].localeCompare(b['name']);
            });

            // Add to pubs list
            for (var i = 0; i < pubs_list.length; i++)
            {
                pub_data = [];

                // Append pub name
                pub_data.push(pubs_list[i]['name']);

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
                    var date = new Date(pubs_list[i]['prices'].slice(-1)[0]['creationDate']).toString().split(' ');
                    pub_data.push(date[0] + ' ' + date[2] + ' ' + date[1] + ' ' + date[3]);
                }
                else
                {
                    pub_data.push('-');
                } 

                // Append submit price button
                pub_data.push("Will place button here");

                g_pubData.push(pub_data.slice());
            } 

            $('#GuindexDataTable').DataTable({
                responsive: true,
                data: g_pubData,
                columns: [
                    {title: "Name"},
                    {title: "Price (€)"},
                    {title: "Last Submitted By"},
                    {title: "Last Submitted Date"},
                    {title: "Submit Price"},
                ] 
            });
        }
    } 
})();
