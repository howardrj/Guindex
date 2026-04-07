from django.urls import include, path, re_path

from UserProfile import views

# Token must match allauth/django default_token_generator (e.g. "abc123-<32 hex>").
# The old {1,13}-{1,20} pattern was too short and broke reverse() during email send → HTTP 500.
PASSWORD_RESET = (
    r"^api/rest-auth/password/reset/confirm/"
    r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
    r"(?P<token>[^/]+)/$"
)

urlpatterns = [
    path("api/rest-auth/", include("dj_rest_auth.urls")),
    path("api/rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("account/", include("allauth.urls")),
    re_path(
        PASSWORD_RESET,
        views.GuindexPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
