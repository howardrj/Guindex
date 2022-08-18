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
    LOGGED_IN_TO_GUINDEX: 2
}

const GuindexUserAuthProviders = {
    UNKNOWN: 0,
    GOOGLE: 1
}

class GuindexUser
{
    static singleton = null;

    constructor ()
    {
        if (GuindexUser.singleton)
            throw new Error("Cannot have more than one GuindexUser instance");

        GuindexUser.singleton = this;
        this.state = GuindexUserStates.LOGGED_OUT;
        this.auth_provider = GuindexUserAuthProviders.UNKNOWN;

        firebase.auth().onAuthStateChanged(this._on_firebase_user_auth_state_changed);
    }

    _change_state (state_name)
    {
        if (state_name == this.state)
            return;

    }

    _on_firebase_user_auth_state_changed (user)
    {
        let guindex_user = GuindexUser.singleton;

        if (!user)
        {
            console.log("User has not been authenticated by any provider");
            guindex_user._change_state(GuindexUserStates.LOGGED_OUT);
            return;
        }

        console.log(guindex_user);
    }
}

(function () {

    guindex_login_init_firebase();

    let guindex_user = new GuindexUser();
})();
