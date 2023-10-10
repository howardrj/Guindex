class GuindexContactForm
{
    static singleton = null;

    constructor (user)
    {
        if (GuindexContactForm.singleton)
            throw new Error("Cannot have more than one GuindexContactForm instance");

        GuindexContactForm.singleton = this;
        this.user = user;

        this._add_on_contact_form_submit_cb();
    }

    _add_on_contact_form_submit_cb ()
    {
        $('#contact_form_submit_button').on('click', this._on_contact_form_submit_cb);
    }

    _on_contact_form_submit_cb ()
    {
        let form = GuindexContactForm.singleton;

        let name    = document.getElementById('contact_form_name').value;
        let email   = document.getElementById('contact_form_email').value;
        let subject = document.getElementById('contact_form_subject').value;
        let message = document.getElementById('contact_form_message').value;

        let contact_data = {
            'name'   : name,
            'email'  : email,
            'subject': subject,
            'message': message,
        }

        form._submit_form_data(contact_data,
                               this);
    }

    async _submit_form_data (contact_data,
                             button)
    {
        guindex_toggle_loader(button);

        let response = await fetch(this.user.api_base + 'contact/', 
                                   {
                                       method: 'POST',
                                       headers: {
                                           'Content-Type': 'application/json',
                                       },
                                       body: JSON.stringify(contact_data),
                                   });

        guindex_toggle_loader(button);

        let response_body = await response.json();

        if (response.status == 201)
            this._on_form_submit_success();
        else
            this._on_form_submit_failure(response_body);
    }

    _on_form_submit_success ()
    {
        guindex_display_message("Info",
                                "Thank you for your message. " +
                                "A member of the Guindex team will be in touch with you shortly.");

        // Clear form
        document.getElementById('contact_form_name').value    = "";
        document.getElementById('contact_form_email').value   = "";
        document.getElementById('contact_form_subject').value = "";
        document.getElementById('contact_form_message').value = "";
    }

    _on_form_submit_failure (response)
    {
        // Display errors
        var error_message = '<p>Please fix the following error(s): </p>'

        var error_table = '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';

        error_table += '<tr> <th> Field </th> <th> Error </th> </tr>';

        Object.keys(response).forEach(function(key) {

            error_table += '<tr>';

            error_table += '<td>' + key + '</td>';

            error_table += '<td>' + response[key] + '</td>';

            error_table += '</tr>';
        });

        error_table += '</tbody></table>';

        guindex_display_message("Error", error_message + error_table);
    }
}

(function ()
{
    let contact_form = new GuindexContactForm(g_guindex_user);
})();
