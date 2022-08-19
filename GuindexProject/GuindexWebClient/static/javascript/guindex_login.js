import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.3/firebase-app.js";

function guindex_login_init_firebase ()
{
    const firebase_config = {
        apiKey: "AIzaSyDdzY9rNnZTpA_EenAfn9Vs7SRvAZtCh2g",
        authDomain: "guindex-fd679.firebaseapp.com",
        projectId: "guindex-fd679",
        storageBucket: "guindex-fd679.appspot.com",
        messagingSenderId: "895081803981",
        appId: "1:895081803981:web:d897aed7427b4c79c8f984",
        measurementId: "G-K9V19D9DWE"
    };

    const app = firebase.initializeApp(firebase_config);

    var ui_config = {
        signInSuccessUrl: window.location.href,
        signInOptions: [
            // Leave the lines as is for the providers you want to offer your users.
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        ],
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());

    ui.start('#firebaseui-auth-container', ui_config);
}

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
        this.is_staff_member = (data['results'][0]['isStaff'] == 'True')
        this.user_id = data['results'][0]['user']

        this._change_state(GuindexUserStates.LOGGED_INTO_GUINDEX)
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

(function () {

    guindex_login_init_firebase();

    let guindex_user = new GuindexUser();

    guindex_user.check_firebase_auth_status();

})();
