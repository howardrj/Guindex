(function () {

    var verify_guinness_buttons = document.getElementsByClassName('verify_guinness_button');

    for (var i = 0 ; i < verify_guinness_buttons.length; i++)
    {
        verify_guinness_buttons[i].addEventListener('click', function (evt) { openVerifyGuinnessForm(evt) });
    }

    var openVerifyGuinnessForm = function (evt)
    {
        var verify_guinness_form = document.getElementById('verify_guinness_modal');

        // Set pub price in form
        var pub_price_field = verify_guinness_form.querySelector('#guinness_price');
        pub_price_field.innerHTML = evt.target.getAttribute('data-pub_price');

        // Set pub name in form
        var pub_name_field = verify_guinness_form.querySelector('#pub_name');
        pub_name_field.innerHTML = evt.target.getAttribute('data-pub_name');

        // Set pub id in form 
        var pub_id_field = verify_guinness_form.querySelector('#pub_id');
        pub_id_field.value = evt.target.getAttribute('data-pub_id'); 

        // Display from modal
        showModal(verify_guinness_form.id);
    }
})();
