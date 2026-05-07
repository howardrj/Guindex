from django.urls import re_path
from django.views.generic import TemplateView

from UserProfile import views
from dj_rest_auth.registration.views import (
    RegisterView,
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetConfirmView, PasswordResetView

# Order: longer password/reset/confirm/... before bare .../confirm/ (API POST only)
urlpatterns = [
    re_path(r'^api/rest-auth/login/$', LoginView.as_view(), name='rest_login'),
    re_path(r'^api/rest-auth/logout/$', LogoutView.as_view(), name='rest_logout'),
    re_path(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name='fb_login'),
    re_path(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name='fb_connect'),
    re_path(r'^api/rest-auth/password/reset/$', PasswordResetView.as_view(), name='rest_password_reset'),
    re_path(
        r'^api/rest-auth/password/reset/confirm/$',
        PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm',
    ),
    re_path(
        r'^api/rest-auth/registration/$',
        RegisterView.as_view(),
        name='rest_register',
    ),
    re_path(
        r'^api/rest-auth/registration/verify-email/?$',
        VerifyEmailView.as_view(),
        name='rest_verify_email',
    ),
    re_path(
        r'^api/rest-auth/registration/resend-email/?$',
        ResendEmailVerificationView.as_view(),
        name='rest_resend_email',
    ),
    re_path(
        r'^api/rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        views.ConfirmEmailGuindexView.as_view(),
        name='account_confirm_email',
    ),
    re_path(
        r'^api/rest-auth/registration/account-email-verification-sent/?$',
        TemplateView.as_view(),
        name='account_email_verification_sent',
    ),
]
