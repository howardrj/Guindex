(function () {

    // Open new Gunness form when new Guinness button is clicked
    var new_guinness_buttons = document.getElementsByClassName('new_guinness_button');

    for (var i = 0; i < new_guinness_buttons.length; i++)
    {
        new_guinness_buttons[i].addEventListener('click', function () { openNewGuinnessForm(event) });
    }

    var openNewGuinnessForm = function (evt)
    {
        var new_guinness_form = document.getElementById('new_guinness_modal');

        // Set pub id in form 
        var pub_id_field = new_guinness_form.querySelector('#id_pub');

        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(new_guinness_form.id);
    }

})();
