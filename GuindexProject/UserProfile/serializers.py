from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from allauth.account.adapter import get_adapter
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
        if email and self._users_for_email(email):
            raise serializers.ValidationError(
                _('A user is already registered with this e-mail address.')
            )
        return email

    def _users_for_email(self, email):
        """
        Compatible lookup across old/new allauth versions.
        """
        try:
            from allauth.account.utils import filter_users_by_email
            try:
                return filter_users_by_email(email, is_active=None)
            except TypeError:
                # Older signature without is_active.
                return filter_users_by_email(email)
        except Exception:
            User = get_user_model()
            try:
                return list(User.objects.filter(email__iexact=email))
            except Exception:
                return list(User.objects.filter(email=email))


class GuindexPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        if "allauth" in settings.INSTALLED_APPS:
            from UserProfile.forms import GuindexPasswordResetForm
            return GuindexPasswordResetForm
        from django.contrib.auth.forms import PasswordResetForm
        return PasswordResetForm
