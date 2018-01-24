(function () {

    var approve_buttons = document.getElementsByClassName('approve_contribution_button');

    for (var i = 0; i < approve_buttons.length; i++)
    {
        approve_buttons[i].addEventListener('click', function (evt) { approveContribution (evt) });
    }

    var approveContribution = function (evt) {

        var contribution_id     = evt.target.getAttribute('data-contribution_id');
        var contribution_type   = evt.target.getAttribute('data-contribution_type');
        var contribution_method = evt.target.getAttribute('data-method');
        var contribution_reason = ""

        if (contribution_method == 'reject')
        {
            // Try get contribution reason
            contribution_reason = evt.target.parentNode.children[0].value;

            // Hide dropdown
            evt.target.parentNode.classList.remove("show");
        }

        // Hide approve and reject buttons and display loader
        document.getElementById('approve_' + contribution_type + '_' + contribution_id).style.display = 'none';
        document.getElementById('reject_'  + contribution_type + '_' + contribution_id + '_button').style.display = 'none';
        document.getElementById(contribution_type + '_' + contribution_id + '_loader').style.display  = 'block';

        var request = new XMLHttpRequest();
        request.open('POST', '/approve_contribution/', true); 

        request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        request.send(JSON.stringify({'contributionId'    : contribution_id,
                                     'contributionType'  : contribution_type,
                                     'contributionReason': contribution_reason,
                                     'contributionMethod': contribution_method}));

        request.onreadystatechange = processRequest;

        function processRequest()
        {
            if (request.readyState == 4 && request.status == 200)
            {
                cleanUpTable(contribution_id, contribution_type, contribution_method);
            }
        };

        var cleanUpTable = function (contributionId, contributionType, contributionMethod) {

            var table   = document.getElementById(contributionType + '_table');

            var clicked_button_id = contributionMethod + '_' + contributionType + '_' + contributionId;
            var clicked_button    = table.querySelector('#' + clicked_button_id)

            if (contributionMethod == "approve")
            {
                clicked_button.parentNode.innerHTML = "APPROVED";
            }
            else if (contributionMethod == "reject")
            {
                clicked_button.parentNode.innerHTML = "REJECTED";
            }
            else
            {
                console.log("Received invalid contribution method");
            }
        };
    };
})();
