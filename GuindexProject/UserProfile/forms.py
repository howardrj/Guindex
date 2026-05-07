# -*- coding: utf-8 -*-
"""
dj-rest-auth ``AllAuthPasswordResetForm`` fork: avoid deprecated
``AUTHENTICATION_METHOD`` access (allauth warns; use ``LOGIN_METHODS`` only).
"""
import hashlib

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import filter_users_by_email, user_pk_to_url_str, user_username
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from dj_rest_auth.forms import (
    AllAuthPasswordResetForm as DjRestAllAuthPasswordResetForm,
    default_url_generator,
)


class GuindexPasswordResetForm(DjRestAllAuthPasswordResetForm):
    """Same behaviour as dj-rest-auth's form without the deprecated branch."""

    def clean_email(self):
        """
        Match allauth's ResetPasswordForm: prefer verified addresses when resolving
        users, so legacy duplicate rows map to one account when possible.
        """
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(
            email, is_active=True, prefer_verified=True
        )
        return self.cleaned_data["email"]

    @staticmethod
    def _single_user_for_reset(users):
        """At most one reset link per request (one outbound message to that inbox)."""
        if not users:
            return []
        if len(users) == 1:
            return list(users)
        return [min(users, key=lambda u: u.pk)]

    # Dedupe rapid duplicate POSTs (double handlers, double-clicks, or retries in flight).
    _PW_RESET_COOLDOWN_S = 120
    _PW_RESET_MUTEX_S = 30

    @staticmethod
    def _pw_reset_cache_keys(email: str) -> tuple[str, str]:
        h = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
        return (f"guindex:pwreset:cd:{h}", f"guindex:pwreset:mx:{h}")

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        cd_key, mx_key = self._pw_reset_cache_keys(email)
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
            login_methods = getattr(allauth_account_settings, "LOGIN_METHODS", None)
            if login_methods and (
                allauth_account_settings.AuthenticationMethod.EMAIL
                not in login_methods
            ):
                context["username"] = user_username(user)
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )
        if self.users:
            cd_key, _ = self._pw_reset_cache_keys(email)
            cache.set(cd_key, 1, self._PW_RESET_COOLDOWN_S)
        return self.cleaned_data["email"]
