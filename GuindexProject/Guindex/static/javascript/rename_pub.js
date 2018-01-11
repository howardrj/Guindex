(function () {

    var rename_pub_buttons = document.getElementsByClassName('rename_pub_button');

    for (var i = 0 ; i < rename_pub_buttons.length; i++)
    {
        rename_pub_buttons[i].addEventListener('click', function (evt) { openRenamePubForm(evt) });
    }

    var openRenamePubForm = function (evt)
    {
        var rename_pub_form = document.getElementById('rename_pub_modal');

        // Set pub id in form 
        var pub_id_field = rename_pub_form.querySelector('#id_pub');

        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(rename_pub_form.id);
    }
})();
