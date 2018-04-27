var toggleLoader = function (buttonNode) {

    // Function that takes in button node
    // switches currrent didaply with corresponding loader

    var loader = buttonNode.parentNode.getElementsByClassName('guindex_web_client_loader')[0];

    if (buttonNode.style.display === "none")
    {
        buttonNode.style.display = "block";
        loader.style.display     = "none";
    }
    else
    {
        buttonNode.style.display = "none";
        loader.style.display     = "block";
    }
}

var displayMessage = function (severity, message) {
    
    // Function that opens generic message modal,
    // sets severity in modal header and message in modal body

    document.getElementById('message_severity').innerHTML = severity;
    document.getElementById('message_body').innerHTML = message;
    document.getElementById('message_link').click();
}
