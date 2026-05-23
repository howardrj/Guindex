import logging
import re

from django import forms as django_forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)

logger = logging.getLogger(__name__)


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

    def _username_from_email(self, email):
        base = re.sub(r'[^\w.@+-]', '_', email.split('@')[0])[:150] or 'user'
        User = get_user_model()
        candidate = base
        suffix = 0
        while User.objects.filter(username=candidate).exists():
            suffix += 1
            candidate = '{0}_{1}'.format(base[:140], suffix)
        return get_adapter().clean_username(candidate)

    def get_cleaned_data(self):
        data = super(GuindexRegisterSerializer, self).get_cleaned_data()
        email = (data.get('email') or '').strip()
        if email and not (data.get('username') or '').strip():
            data['username'] = self._username_from_email(email)
        return data

    def validate_password1(self, password):
        try:
            return get_adapter().clean_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        except django_forms.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_email(self, value):
        email = get_adapter().clean_email(value)
        if allauth_settings.UNIQUE_EMAIL and email and self._users_for_email(email):
            raise serializers.ValidationError(
                _('A user is already registered with this e-mail address.')
            )
        return email

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        try:
            adapter.save_user(request, user, self)
        except django_forms.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        except Exception as exc:
            logger.exception('adapter.save_user failed during registration')
            raise serializers.ValidationError(
                _('Registration failed. Please try again or contact support.')
            )

        self.custom_signup(request, user)
        self._setup_email_address(request, user)
        return user

    def _setup_email_address(self, request, user):
        if EmailAddress.objects.filter(user=user).exists():
            return
        try:
            setup_user_email(request, user, [])
        except Exception:
            logger.exception(
                'setup_user_email failed for user pk=%s; creating EmailAddress',
                user.pk,
            )
            if user.email:
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=False,
                    primary=True,
                )

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


class GuindexPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """
    rest-auth decodes uid as urlsafe base64; allauth reset links use base36
    (user_pk_to_url_str). Tokens are issued with allauth's default_token_generator.
    """

    def validate(self, attrs):
        from allauth.account.forms import default_token_generator as allauth_token
        try:
            from allauth.account.utils import url_str_to_user_pk
        except ImportError:
            from allauth.utils import url_str_to_user_pk
        from django.contrib.auth.forms import SetPasswordForm
        from django.contrib.auth.tokens import default_token_generator as django_token
        from django.utils.encoding import force_text
        from django.utils.http import urlsafe_base64_decode as uid_decoder

        UserModel = get_user_model()
        uid_raw = attrs.get('uid', '')

        try:
            pk = url_str_to_user_pk(uid_raw)
            self.user = UserModel._default_manager.get(pk=pk)
        except Exception:
            try:
                from allauth.compat import base36_to_int
                pk = base36_to_int(uid_raw)
                self.user = UserModel._default_manager.get(pk=pk)
            except Exception:
                try:
                    pk = force_text(uid_decoder(uid_raw))
                    self.user = UserModel._default_manager.get(pk=pk)
                except Exception:
                    raise serializers.ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)

        self.set_password_form = SetPasswordForm(
            user=self.user,
            data={
                'new_password1': attrs.get('new_password1'),
                'new_password2': attrs.get('new_password2'),
            },
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        token = attrs.get('token', '')
        if not allauth_token.check_token(self.user, token):
            if not django_token.check_token(self.user, token):
                raise serializers.ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        return self.set_password_form.save()
