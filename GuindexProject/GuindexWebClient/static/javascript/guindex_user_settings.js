function guindex_init_user_settings_table ()
{
    let guindex_user_settings_table = new GuindexUserSettingsTable(g_guindex_user);
}

class GuindexUserSettingsTable
{
    static singleton = null;

    constructor (user)
    {
        if (GuindexUserSettingsTable.singleton)
            throw new Error("Cannot have more than one GuindexUserSettingsTable instance");

        GuindexUserSettingsTable.singleton = this;
        this.user = user;
        this.user_settings = null;
        this.user_settings_data_table = null;
        this.retrieving_user_settings = false;
        this.rendered = false;

        this._populate();
        this._add_on_setting_toggler_click_cb();
    }

    async _retrieve_user_settings_and_render_table ()
    {
        if (this.retrieving_user_settings)
            return;

        this.retrieving_user_settings = true;

        let response = await fetch(this.user.api_base + 'contributors/' + this.user.id + '/', 
                                   {
                                       headers: {
                                           'Authorization': 'Token ' + this.user.access_token,
                                       },
                                   });

        if (response.status == 200)
        {
            this.user_settings = await response.json();
            this._render_table();
        }
         
        this.retrieving_user_settings = false;
    }

    _render_table ()
    {
        var table_data = [];

        var prefix = '<label class="switch">';
        var suffix = '<div id="email_alerts_toggler_div" class="slider round"> </div></label>';

        // Email alerts setting
        var email_alerts_list = ['Email Alerts', 
                                 "Receive weekly email alerts about new prices and pubs added to the Guindex.",
                                 prefix + '<input type="checkbox" id="email_alerts_toggler" class="toggler hoverable">' + suffix
                                ];

        table_data.push(email_alerts_list);

        // Check if table is being drawn from scratch or refreshed
        if (!this.user_settings_data_table)
        {
            this.user_settings_data_table = $('#GuindexUserSettingsTable').DataTable({responsive: true,
                                                                                      "paging": false,
                                                                                      "ordering": false,
                                                                                      "searching": false,
                                                                                      data: table_data,
                                                                                      columns: [
                                                                                          { title: "Setting" },
                                                                                          { title: "Description" },
                                                                                          { title: "Toggle" },
                                                                                      ]});
        }
        else
        {
            // Redraw table
            // TODO Stay on same page table
            this.user_settings_data_table.clear().draw();
            this.user_settings_data_table.rows.add(table_data);
            this.user_settings_data_table.columns.adjust().draw();
        }

        // Need this since setting checked in HTML does not leave toggler in correct state
        if (this.user_settings['using_email_alerts'])
            document.getElementById('email_alerts_toggler').checked = true;

        if (!this.rendered)
            this.rendered = true;
    }

    _populate ()
    {
        var settings_page = document.getElementById('settings_page');

        if (!this.user.logged_in())
            return;

        // Clear log in warning if logged in
        settings_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        settings_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        if (this.rendered)
            return;

        if (!this.user_settings)
            this._retrieve_user_settings_and_render_table();
        else
            this._render_table()
    }

    _add_on_setting_toggler_click_cb ()
    {
        $(document).on('click', '.toggler', this._on_setting_toggler_click_cb);
    }

    _on_setting_toggler_click_cb ()
    {
        let toggler = this;
        let table = GuindexUserSettingsTable.singleton;
        let user = table.user;

        var data = {};
        var field;
        
        if (this.id !== "email_alerts_toggler")
        {
            field = 'using_email_alerts';
        }
        else
        {
            // Undo check since it's a field we are not aware of
            toggler.checked = !toggler.checked;
            return;
        }

        data[field] = toggler.checked;
         
        table._post_new_user_setting(data,
                                     toggler)
    }

    async _post_new_user_setting (data,
                                  toggler)
    {
        let response = await fetch(this.user.api_base + 'contributors/' + this.user.id + '/', 
                                   {
                                       method: 'PATCH',
                                       headers: {
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Token ' + this.user.access_token,
                                       },
                                       body: JSON.stringify(data),
                                   });


         if (response.status == 200)
         {
             // Success
         }
         else
         {
             // Error: Revert toggler to original state
             toggler.checked = !toggler.checked;
         }
    }
}

// Add settings page event listeners
(function ()
{
    document.getElementById('settings_page').addEventListener('tab_display',
                                                              guindex_init_user_settings_table);

    document.getElementById('settings_page').addEventListener('on_login',
                                                              guindex_init_user_settings_table); 
})();
