# -*- coding: utf-8 -*-
"""
Password reset for django-rest-auth 0.9.x (no rest_auth.forms module).
Uses allauth's ResetPasswordForm pattern with Guindex confirm URLs.
"""
import hashlib
import logging

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import filter_users_by_email, user_pk_to_url_str, user_username
from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def guindex_password_reset_url(request, user, temp_key):
    """Link to the standalone reset page (not django-admin style URLs)."""
    site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    uid = user_pk_to_url_str(user)
    return '{0}://{1}/password/reset/confirm/{2}/{3}/'.format(
        protocol,
        site.domain,
        uid,
        temp_key,
    )


class GuindexPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_('E-mail'), required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)
        self.users = self._filter_users_for_reset(email)
        # Do not reveal whether the address exists (same as Django's default form).
        return self.cleaned_data['email']

    @staticmethod
    def _filter_users_for_reset(email):
        try:
            return filter_users_by_email(email, is_active=True)
        except TypeError:
            return filter_users_by_email(email)

    @staticmethod
    def _cache_keys(email):
        digest = hashlib.sha256(email.strip().lower().encode('utf-8')).hexdigest()
        return (
            'guindex:pwreset:cd:{0}'.format(digest),
            'guindex:pwreset:mx:{0}'.format(digest),
        )

    @staticmethod
    def _single_user_for_reset(users):
        if not users:
            return []
        try:
            user_list = list(users)
        except TypeError:
            user_list = users
        if len(user_list) == 1:
            return user_list
        return [sorted(user_list, key=lambda u: u.pk)[0]]

    def save(self, request, **kwargs):
        email = self.cleaned_data['email']
        cd_key, mx_key = self._cache_keys(email)
        if cache.get(cd_key):
            return email
        if not cache.add(mx_key, 1, 30):
            return email
        try:
            return self._save_send_emails(request, **kwargs)
        finally:
            cache.delete(mx_key)

    def _save_send_emails(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator', default_token_generator)

        users = self._single_user_for_reset(self.users)
        if not users:
            return self.cleaned_data['email']

        for user in users:
            temp_key = token_generator.make_token(user)
            url = guindex_password_reset_url(request, user, temp_key)
            uid = user_pk_to_url_str(user)

            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
                'token': temp_key,
                'uid': uid,
            }
            auth_method = getattr(allauth_account_settings, 'AUTHENTICATION_METHOD', None)
            if auth_method and auth_method != 'email':
                context['username'] = user_username(user)

            get_adapter(request).send_mail(
                'account/email/password_reset_key',
                email,
                context,
            )

        cd_key, _ = self._cache_keys(email)
        cache.set(cd_key, 1, 120)
        return self.cleaned_data['email']
