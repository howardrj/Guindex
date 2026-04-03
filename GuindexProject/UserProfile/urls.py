from django.urls import include, path, re_path

from UserProfile import views

PASSWORD_RESET = (
    r"^api/rest-auth/password/reset/confirm/"
    r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
    r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$"
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
