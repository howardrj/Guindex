from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView, SocialConnectView

from UserProfile.serializers import GuindexSocialLoginSerializer


class GuindexSocialLoginView(SocialLoginView):
    serializer_class = GuindexSocialLoginSerializer


class GuindexSocialConnectView(SocialConnectView):
    pass


class FacebookLogin(GuindexSocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(GuindexSocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(GuindexSocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class GoogleConnect(GuindexSocialConnectView):
    adapter_class = GoogleOAuth2Adapter
