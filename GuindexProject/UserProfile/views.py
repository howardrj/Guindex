import logging

from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView

logger = logging.getLogger(__name__)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class ConfirmEmailGuindexView(ConfirmEmailView):
    """Email confirmation with Guindex site chrome (standalone page, not the SPA shell)."""

    template_name = "email_confirm_standalone.html"

    def dispatch(self, request, *args, **kwargs):
        key = kwargs.get("key") or ""
        logger.info("Email confirm request key prefix=%s", key[:16])
        return super().dispatch(request, *args, **kwargs)
