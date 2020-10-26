from django.conf.urls import include, url
from django.conf import settings
from UserProfile import views


PASSWORD_RESET = (
    r'^api/rest-auth/password/reset/confirm/'
    r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
    r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
)

urlpatterns = [
    url(r'^api/rest-auth/', include('rest_auth.urls')),
    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls')) # Needed for account_email_verification_sent reverse
]

urlpatterns += [
    url(
        PASSWORD_RESET,
        views.GuindexPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
]
