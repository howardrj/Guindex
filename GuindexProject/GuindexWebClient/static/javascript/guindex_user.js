var g_guindex_user = null;

const GuindexUserStates = {
    LOGGED_OUT: 0,
    AUTHENTICATED_BY_PROVIDER: 1,
    LOGGED_INTO_GUINDEX: 2
}

const GuindexUserAuthProviders = {
    UNKNOWN: 0,
    GOOGLE: 1
}

class GuindexUserState
{
    constructor (user)
    {
        this.user = user;
    }

    init ()
    {
        throw new Error("init method must be implemented"); 
    }

    deinit ()
    {
        throw new Error("deinit method must be implemented"); 
    }

    toString ()
    {
        throw new Error("toString method must be implemented"); 
    }
}

class GuindexUserStateLoggedOut extends GuindexUserState 
{
    constructor (user)
    {
        super(user);
        this.state_id = GuindexUserStates.LOGGED_OUT;
    }

    init ()
    {
    
    }

    deinit ()
    {

    }

    toString ()
    {
        return "LOGGED_OUT";
    }
}

class GuindexUserStateAuthenticatedByProvider extends GuindexUserState 
{
    constructor (user)
    {
        super(user);
        this.state_id = GuindexUserStates.AUTHENTICATED_BY_PROVIDER;
    }

    init ()
    {
        this.user.request_access_token();
    }

    deinit ()
    {
    }

    toString ()
    {
        return "AUTHENTICATED_BY_PROVIDER";
    }
}

class GuindexUserStateLoggedIntoGuindex extends GuindexUserState 
{
    constructor (user)
    {
        super(user);
        this.state_id = GuindexUserStates.LOGGED_INTO_GUINDEX;
    }

    init ()
    {
        // Show pending contributions tab 
        if (this.user.is_staff_member)
            document.getElementById('pending_contributions_li').style.display = 'list-item';

        var page_contents = document.getElementsByClassName('page_content');

        for (var i = 0; i < page_contents.length; i++)
        {
            page_contents[i].dispatchEvent(new Event('on_login'));
        }

        // Set login status link to display username (i.e. top right corner of GUI)
        var login_link = document.getElementById('login_link');
        login_link.innerHTML = this.user.username;

        // Toggle log in/out display messages
        document.getElementById('logged_out_modal_header').style.display = 'none';
        document.getElementById('logged_in_modal_header').style.display = 'block';

        document.getElementById('logged_out_modal_body').style.display = 'none';
        document.getElementById('logged_in_modal_body').style.display = 'block';
        document.getElementById('logged_in_modal_body_username').innerHTML = this.user.username;

        document.getElementById('logged_out_modal_footer').style.display = 'none';
        document.getElementById('logged_in_modal_footer').style.display = 'block';
    
        // Add logout button event listener
        $(document).on('click', '#logout_button', function () {

            toggleLoader(this);

            firebase.auth().signOut().then(function() {
                // Sign-out successful.
                location.reload();
            }).catch(function(error) {
                // An error happened
               toggleLoader(this);
           });    
        });
    }

    deinit ()
    {
    }

    toString ()
    {
        return "LOGGED_INTO_GUINDEX";
    }
}

class GuindexUser
{
    static singleton = null;

    constructor ()
    {
        if (GuindexUser.singleton)
            throw new Error("Cannot have more than one GuindexUser instance");

        GuindexUser.singleton = this;
        this.current_state = new GuindexUserStateLoggedOut(this);
        this.auth_provider = GuindexUserAuthProviders.UNKNOWN;
        this.firebase_id_token = null; // Sent to Guindex server to request API access token
        this.guindex_access_token = null; // Used in subsequent requests to Guindex API
        this.is_staff_member = false;
        this.user_id = 0;
        this.url_base = location.protocol + '//' + location.hostname + ':' + location.port;
        this.api_base = this.url_base + '/api/';
        this.login_method = 'google';
    }

    logged_in ()
    {
        return this.access_token != null;
    }

    async request_access_token ()
    {
        let response = await fetch(this.api_base + 'access_token/', 
                                   {
                                       headers: {
                                           'FIREBASE-TOKEN-ID': this.firebase_id_token,
                                       },
                                   });

        if (!response.ok)
        {
            console.log("Failed to get access token");
            return;
        }

        let data = await response.json();

        this.guindex_access_token = data['results'][0]['key'];
        this.is_staff_member = (data['results'][0]['isStaff'] == 'True');
        this.user_id = data['results'][0]['user'];
        this.username = data['results'][0]['username'];

        this._change_state(GuindexUserStates.LOGGED_INTO_GUINDEX);
    }

    check_firebase_auth_status ()
    {
        firebase.auth().onAuthStateChanged(this._on_firebase_user_auth_state_changed.bind(this));
    }

    _change_state (state_id)
    {
        let new_state = null;

        if (state_id.valueOf() === this.current_state.state_id.valueOf())
            return;

        switch (state_id)
        {
            case GuindexUserStates.LOGGED_OUT:
                new_state = new GuindexUserStateLoggedOut(this);
                break;
            case GuindexUserStates.AUTHENTICATED_BY_PROVIDER:
                new_state = new GuindexUserStateAuthenticatedByProvider(this);
                break;
            case GuindexUserStates.LOGGED_INTO_GUINDEX:
                new_state = new GuindexUserStateLoggedIntoGuindex(this);
                break;
            default:
                throw new Error("Cannot transition to state with ID %d", state_id);
        }

        console.log("Transitioning from state %s to state %s", this.current_state, new_state);

        this.current_state.deinit()
        this.current_state = new_state;
        this.current_state.init()
    }

    _on_firebase_user_auth_state_changed (user)
    {
        if (!user)
        {
            console.log("User has not been authenticated by any provider");
            this._change_state(GuindexUserStates.LOGGED_OUT);
            return;
        }

        this._on_user_authenticated_by_provider(user)
    }

    async _on_user_authenticated_by_provider (user)
    {
        this.firebase_id_token = await firebase.auth().currentUser.getIdToken(user);

        this._change_state(GuindexUserStates.AUTHENTICATED_BY_PROVIDER)
    }

    toString ()
    {
        return this.user_id + this.current_state;
    }
}

(function ()
{
    g_guindex_user = new GuindexUser();

})();
