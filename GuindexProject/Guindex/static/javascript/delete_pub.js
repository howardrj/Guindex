(function () {

    var delete_pub_buttons = document.getElementsByClassName('delete_pub_button');

    for (var i = 0 ; i < delete_pub_buttons.length; i++)
    {
        delete_pub_buttons[i].addEventListener('click', function (evt) { openDeletePubForm(evt) });
    }

    var openDeletePubForm = function (evt)
    {
        var delete_pub_form = document.getElementById('delete_pub_modal');

        // Set pub name in form
        var pub_name_field = delete_pub_form.querySelector('#pub_name');
        pub_name_field.innerHTML = evt.target.getAttribute('data-pub_name');

        // Set pub id in form 
        var pub_id_field = delete_pub_form.querySelector('#pub_id');
        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(delete_pub_form.id);
    }
})();
