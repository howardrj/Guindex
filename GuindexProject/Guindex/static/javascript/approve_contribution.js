(function () {

    var approve_buttons = document.getElementsByClassName('approve_contribution_button');

    for (var i = 0; i < approve_buttons.length; i++)
    {
        approve_buttons[i].addEventListener('click', function (evt) { approveContribution (evt) });
    }

    var approveContribution = function (evt) {

        var contribution_id   = evt.target.getAttribute('data-contribution_id');
        var contribution_type = evt.target.getAttribute('data-contribution_type');

        // Display loader
        evt.target.style.display = 'none';
        document.getElementById(evt.target.id + '_loader').style.display = 'block';

        var request = new XMLHttpRequest();
        request.open('POST', '/approve_contribution/', true); 

        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'contributionId'  : contribution_id,
                                     'contributionType': contribution_type}));

        request.onreadystatechange = processRequest;

        function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                cleanUpTable(contribution_id, contribution_type);
            }
        };

        var cleanUpTable = function (contributionId, contributionType) {

            var table          = document.getElementById(contributionType + '_table');
            var clicked_button = table.querySelector('#' + contributionType + '_' + contributionId)

            clicked_button.parentNode.innerHTML = "APPROVED";
        };
    };
})();
