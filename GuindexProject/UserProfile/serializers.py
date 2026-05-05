from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_email
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordResetSerializer


class TokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    isStaff = serializers.CharField(source='user.is_staff', read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user', 'username', 'email', 'isStaff')


class GuindexRegisterSerializer(RegisterSerializer):
    """
    Reject signup when any user already holds this email (verified or not).
    """

    def validate_email(self, value):
        email = get_adapter().clean_email(value)
        if email and filter_users_by_email(email, is_active=None):
            raise serializers.ValidationError(
                _('A user is already registered with this e-mail address.')
            )
        return email


class GuindexPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        if "allauth" in settings.INSTALLED_APPS:
            from UserProfile.forms import GuindexPasswordResetForm
            return GuindexPasswordResetForm
        from django.contrib.auth.forms import PasswordResetForm
        return PasswordResetForm
