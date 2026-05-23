import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer, PasswordResetSerializer


class TokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    isStaff = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'user', 'username', 'email', 'isStaff')

    def get_isStaff(self, obj):
        return 'True' if obj.user.is_staff else 'False'


class GuindexLoginSerializer(LoginSerializer):
    """
    django-rest-auth LoginSerializer uses emailaddress_set.get() when verification
    is mandatory; legacy users (pre-allauth email rows) raise DoesNotExist -> HTTP 500.
  """

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            return super(GuindexLoginSerializer, self).validate(attrs)
        except EmailAddress.DoesNotExist:
            user = self.authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    _('Unable to log in with provided credentials.')
                )
            if not user.email:
                raise serializers.ValidationError(_('E-mail is not verified.'))

            EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=True,
                primary=True,
            )
            attrs['user'] = user
            return attrs


class GuindexRegisterSerializer(RegisterSerializer):
    """
    Reject signup when any user already holds this email (verified or not).
    """

    def validate_username(self, value):
        value = (value or '').strip()
        email = ''
        if hasattr(self, 'initial_data') and self.initial_data:
            email = (self.initial_data.get('email') or '').strip()
        if email and ('@' in value or not value):
            value = re.sub(r'[^\w.@+-]', '_', email.split('@')[0])[:150] or 'user'
        return get_adapter().clean_username(value)

    def validate(self, data):
        email = (data.get('email') or '').strip()
        username = (data.get('username') or '').strip()
        if email and not username:
            data = dict(data)
            data['username'] = re.sub(
                r'[^\w.@+-]', '_', email.split('@')[0]
            )[:150] or 'user'
        return super(GuindexRegisterSerializer, self).validate(data)

    def get_cleaned_data(self):
        data = super(GuindexRegisterSerializer, self).get_cleaned_data()
        email = (data.get('email') or '').strip()
        if email and not (data.get('username') or '').strip():
            data['username'] = re.sub(
                r'[^\w.@+-]', '_', email.split('@')[0]
            )[:150] or 'user'
        return data

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
    """django-rest-auth 0.9.x: password_reset_form_class must be a class attribute."""

    def __init__(self, *args, **kwargs):
        from UserProfile.forms import GuindexPasswordResetForm
        self.password_reset_form_class = GuindexPasswordResetForm
        super(GuindexPasswordResetSerializer, self).__init__(*args, **kwargs)
