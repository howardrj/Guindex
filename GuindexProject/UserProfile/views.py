import logging

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_auth.app_settings import TokenSerializer, create_token
from rest_auth.models import TokenModel
from rest_framework import status
from rest_framework.response import Response
from rest_auth.registration.views import RegisterView, SocialLoginView, SocialConnectView

logger = logging.getLogger(__name__)


def _email_verification_is_mandatory():
    verification = getattr(allauth_settings, 'EMAIL_VERIFICATION', None)
    if verification == 'mandatory':
        return True
    try:
        return verification == allauth_settings.EmailVerificationMethod.MANDATORY
    except AttributeError:
        return False


class GuindexRegisterView(RegisterView):
    """
    Registration view safe on django-rest-auth 0.9.x + older allauth:
    avoids EmailVerificationMethod / auth_token edge cases that return HTTP 500.
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        return Response(
            self.get_response_data(user),
            status=status.HTTP_201_CREATED,
        )

    def get_response_data(self, user):
        if _email_verification_is_mandatory():
            return {'detail': _('Verification e-mail sent.')}

        if getattr(settings, 'REST_USE_JWT', False):
            return super(GuindexRegisterView, self).get_response_data(user)

        token = create_token(TokenModel, user, None)
        try:
            return TokenSerializer(token).data
        except Exception:
            logger.exception('TokenSerializer failed after registration')
            return {
                'key': token.key,
                'user': user.pk,
                'username': user.username,
                'email': user.email,
                'isStaff': 'True' if user.is_staff else 'False',
            }

    def perform_create(self, serializer):
        django_request = getattr(self.request, '_request', self.request)
        user = serializer.save(django_request)
        if getattr(settings, 'REST_USE_JWT', False):
            from rest_auth.utils import jwt_encode
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)

        try:
            complete_signup(
                self.request._request,
                user,
                allauth_settings.EMAIL_VERIFICATION,
                None,
            )
        except Exception:
            logger.exception(
                'complete_signup failed for user pk=%s (account may still exist)',
                user.pk,
            )

        return user


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class ConfirmEmailGuindexView(ConfirmEmailView):
    template_name = "email_confirm_standalone.html"

    def dispatch(self, request, *args, **kwargs):
        key = kwargs.get("key") or ""
        logger.info("Email confirm request key prefix=%s", key[:16])
        return super(ConfirmEmailGuindexView, self).dispatch(request, *args, **kwargs)
