# -*- coding: utf-8 -*-
"""
Password reset form override:
- keep compatibility with legacy allauth AUTHENTICATION_METHOD branch
- send at most one email per submitted address
"""
import hashlib

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str, user_username
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from rest_auth.forms import (
    AllAuthPasswordResetForm as RestAuthAllAuthPasswordResetForm,
    default_url_generator,
)


class GuindexPasswordResetForm(RestAuthAllAuthPasswordResetForm):
    _PW_RESET_COOLDOWN_S = 120
    _PW_RESET_MUTEX_S = 30

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = self._filter_users_for_reset(email)
        return self.cleaned_data["email"]

    @staticmethod
    def _filter_users_for_reset(email):
        """
        Support old/new allauth function signatures.
        """
        from allauth.account.utils import filter_users_by_email
        try:
            return filter_users_by_email(email, is_active=True, prefer_verified=True)
        except TypeError:
            try:
                return filter_users_by_email(email, is_active=True)
            except TypeError:
                return filter_users_by_email(email)

    @staticmethod
    def _cache_keys(email):
        digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
        return (
            "guindex:pwreset:cd:{0}".format(digest),
            "guindex:pwreset:mx:{0}".format(digest),
        )

    @staticmethod
    def _single_user_for_reset(users):
        if not users:
            return []
        if len(users) == 1:
            return list(users)
        # Deterministic fallback for legacy duplicate-email rows.
        return [sorted(users, key=lambda u: u.pk)[0]]

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        cd_key, mx_key = self._cache_keys(email)
        if cache.get(cd_key):
            return email
        if not cache.add(mx_key, 1, self._PW_RESET_MUTEX_S):
            return email
        try:
            return self._save_send_emails(request, **kwargs)
        finally:
            cache.delete(mx_key)

    def _save_send_emails(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in self._single_user_for_reset(self.users):
            temp_key = token_generator.make_token(user)
            url_generator = kwargs.get("url_generator", default_url_generator)
            url = url_generator(request, user, temp_key)
            uid = user_pk_to_url_str(user)

            context = {
                "current_site": current_site,
                "user": user,
                "password_reset_url": url,
                "request": request,
                "token": temp_key,
                "uid": uid,
            }
            # Keep legacy fallback for older allauth versions.
            if (
                getattr(allauth_account_settings, "LOGIN_METHODS", None)
                and allauth_account_settings.AuthenticationMethod.EMAIL
                not in allauth_account_settings.LOGIN_METHODS
            ):
                context["username"] = user_username(user)
            elif (
                hasattr(allauth_account_settings, "AUTHENTICATION_METHOD")
                and allauth_account_settings.AUTHENTICATION_METHOD
                != allauth_account_settings.AuthenticationMethod.EMAIL
            ):
                context["username"] = user_username(user)

            get_adapter(request).send_mail("account/email/password_reset_key", email, context)

        if self.users:
            cd_key, _ = self._cache_keys(email)
            cache.set(cd_key, 1, self._PW_RESET_COOLDOWN_S)
        return self.cleaned_data["email"]
