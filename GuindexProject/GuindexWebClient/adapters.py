# -*- coding: utf-8 -*-
from allauth.account.adapter import DefaultAccountAdapter


class GuindexAccountAdapter(DefaultAccountAdapter):
    """Use the SPA home for login links instead of Django-only ``/accounts/login/``."""

    def get_login_url(self, request):
        return "/"
