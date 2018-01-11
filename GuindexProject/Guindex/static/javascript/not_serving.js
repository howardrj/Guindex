(function () {

    var not_serving_buttons = document.getElementsByClassName('not_serving_guinness_button');

    for (var i = 0 ; i < not_serving_buttons.length; i++)
    {
        not_serving_buttons[i].addEventListener('click', function (evt) { openNotServingGuinnessForm(evt) });
    }

    var openNotServingGuinnessForm = function (evt)
    {
        var not_serving_form = document.getElementById('not_serving_modal');

        // Set pub name in form
        var pub_name_field = not_serving_form.querySelector('#pub_name');
        pub_name_field.innerHTML = evt.target.getAttribute('data-pub_name');

        // Set pub id in form 
        var pub_id_field = not_serving_form.querySelector('#pub_id');
        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(not_serving_form.id);
    }
})();
