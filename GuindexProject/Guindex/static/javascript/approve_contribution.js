(function () {

    var approve_buttons = document.getElementsByClassName('approve_contribution_button');

    for (var i = 0; i < approve_buttons.length; i++)
    {
        approve_buttons[i].addEventListener('click', function (evt) { approveContribution (evt) });
    }

    var approveContribution = function (evt) {

        var contribution_id = evt.target.getAttribute('data-contribution_id');

        // Display loader
        evt.target.style.display = 'none';
        document.getElementById(evt.target.id + '_loader').style.display = 'block';

        var request = new XMLHttpRequest();
        request.open('POST', '/approve_contribution/', true); 

        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'contributionId': contribution_id}));

        request.onreadystatechange = processRequest;

        function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                cleanUpTable(contribution_id);
            }
        };

        var cleanUpTable = function (contributionId) {

            var table          = document.getElementById('pending_prices_table');
            var clicked_button = table.querySelector('#approve_contribution_button_' + contributionId)

            clicked_button.parentNode.innerHTML = "APPROVED";
        };
    };
})();
