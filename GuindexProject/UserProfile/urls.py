from django.conf.urls import url
from django.views.generic import TemplateView

from UserProfile import views
from rest_auth.registration.views import RegisterView, VerifyEmailView
from rest_auth.views import LoginView, LogoutView, PasswordResetConfirmView, PasswordResetView


urlpatterns = [
    url(r'^api/rest-auth/login/$', LoginView.as_view(), name='rest_login'),
    url(r'^api/rest-auth/logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name='fb_login'),
    url(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name='fb_connect'),
    url(r'^api/rest-auth/password/reset/$', PasswordResetView.as_view(), name='rest_password_reset'),
    url(r'^api/rest-auth/password/reset/confirm/$', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
]

# Keep registration endpoint public in all environments.
urlpatterns.extend([
    url(r'^api/rest-auth/registration/$', RegisterView.as_view(), name='rest_register'),
    url(r'^api/rest-auth/registration/verify-email/?$', VerifyEmailView.as_view(), name='rest_verify_email'),
    url(
        r'^api/rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        views.ConfirmEmailGuindexView.as_view(),
        name='account_confirm_email',
    ),
    url(
        r'^api/rest-auth/registration/account-email-verification-sent/?$',
        TemplateView.as_view(),
        name='account_email_verification_sent',
    ),
])
