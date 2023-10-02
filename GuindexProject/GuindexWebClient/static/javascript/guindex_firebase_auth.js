(function ()
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

    // Kick off authentication process once module is loaded
    g_guindex_user.check_firebase_auth_status();

})();
