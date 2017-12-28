(function () {

    var close_pub_buttons = document.getElementsByClassName('close_pub_button');

    for (var i = 0 ; i < close_pub_buttons.length; i++)
    {
        close_pub_buttons[i].addEventListener('click', function () { openClosePubForm(event) });
    }

    var openClosePubForm = function (evt)
    {
        var close_pub_form = document.getElementById('close_pub_modal');

        // Set pub name in form
        var pub_name_field = close_pub_form.querySelector('#pub_name');
        pub_name_field.innerHTML = evt.target.getAttribute('data-pub_name');

        // Set pub id in form 
        var pub_id_field = close_pub_form.querySelector('#pub_id');
        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(close_pub_form.id);
    }
})();
