var guindex_toggle_loader = function (button_node) {

    // Function that takes in button node
    // switches currrent didaply with corresponding loader

    var loader = button_node.parentNode.getElementsByClassName('guindex_web_client_loader')[0];

    if (button_node.style.display === "none")
    {
        button_node.style.display = "block";
        loader.style.display     = "none";
    }
    else
    {
        button_node.style.display = "none";
        loader.style.display     = "block";
    }
}

var guindex_display_message = function (severity, message) {
    
    // Function that opens generic message modal,
    // sets severity in modal header and message in modal body

    document.getElementById('message_severity').innerHTML = severity;
    document.getElementById('message_body').innerHTML = message;
    document.getElementById('message_link').click();
}
