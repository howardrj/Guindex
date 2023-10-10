class GuindexUserContributionsTable
{
    constructor (user)
    {
        if (GuindexUserContributionsTable.singleton)
            throw new Error("Cannot have more than one GuindexUserContributionsTable instance");

        GuindexUserContributionsTable.singleton = this;
        this.user = user;
        this.user_contributions = null;
        this.user_contributions_data_table = null;
        this.retrieving_user_contributions = false;
        this.rendered = false;
    }

    get_contribution_badges ()
    {
        let count = this.user_contributions['original_prices'];

        var image_tag = '<img src="'
        if (count < 0.5)
            image_tag += this.user.url_base + "/static/images/Trophy0.jpeg";
        else if (count < 4.5)
            image_tag += this.user.url_base + "/static/images/Trophy1.jpeg";
        else if (count < 9.5)
            image_tag += this.user.url_base + "/static/images/Trophy5.jpeg";
        else if (count < 24.5)
            image_tag += this.user.url_base + "/static/images/Trophy10.jpeg";
        else if (count < 49.5)
            image_tag += this.user.url_base + "/static/images/Trophy25.jpeg";
        else if (count < 99.5)
            image_tag += this.user.url_base + "/static/images/Trophy50.jpeg";
        else
	        image_tag += this.user.url_base + "/static/images/Trophy100.jpeg";

        image_tag +='" width=35%>';
        return image_tag;
    }

    async _retrieve_user_contributions_and_render_table ()
    {
        if (this.retrieving_user_contributions)
            return;

        this.retrieving_user_contributions = true;

        let response = await fetch(this.user.api_base + 'contributors/' + this.user.id + '/', 
                                   {
                                       headers: {
                                           'Authorization': 'Token ' + this.user.access_token,
                                       },
                                   });

        if (response.status == 200)
        {
            this.user_contributions = await response.json();
            this._render_table();
        }
         
        this.retrieving_user_contributions = false;
    }

    _render_table ()
    {
        var table_data = [];

        table_data.push(["Pubs Visited", this.user_contributions['pubs_visited']]);
        table_data.push(["Current Verifications", this.user_contributions['current_verifications']]);
        table_data.push(["Original Prices", this.user_contributions['original_prices']]);
        table_data.push(["Badges", this.get_contribution_badges()]);

        // Check if table is being drawn from scratch or refreshed
        if (!this.user_contributions_data_table)
        {
            data_columns = [
                {title: "Statistic", "orderable": false},
                {title: "Value",     "orderable": false},
            ]

            this.user_contributions_data_table = $('#GuindexContributionsTable').DataTable({responsive: true,
                                                                                            data: table_data,
                                                                                            columns: data_columns,
                                                                                            "paging": false,
                                                                                            "ordering": false,
                                                                                            "searching": false});
        }
        else
        {
            // Redraw table
            // TODO Stay on same page table
            this.user_contributions_data_table.clear().draw();
            this.user_contributions_data_table.rows.add(table_data);
            this.user_contributions_data_table.columns.adjust().draw();
        }

        if (!this.rendered)
            this.rendered = true;
    }

    populate ()
    {
        var contributions_page = document.getElementById('contributions_page');

        if (!this.user.logged_in())
            return;

        // Clear log in warning if logged in
        contributions_page.getElementsByClassName('on_logged_in')[0].style.display  = 'block';
        contributions_page.getElementsByClassName('on_logged_out')[0].style.display = 'none';

        if (this.rendered)
            return;

        if (!this.user_contributions)
            this._retrieve_user_contributions_and_render_table();
        else
            this._render_table()
    }
}

(function ()
{
    let table = new GuindexUserContributionsTable(g_guindex_user);

    document.getElementById('contributions_page').addEventListener('tab_display',
                                                                   table.populate);

    document.getElementById('contributions_page').addEventListener('on_login',
                                                                   table.populate);
})();
