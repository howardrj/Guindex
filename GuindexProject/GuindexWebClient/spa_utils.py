# -*- coding: utf-8 -*-
"""Shared context for Guindex shell-like templates."""
from django.conf import settings

from Guindex.GuindexParameters import GuindexParameters


def web_client_template_context(request, extra=None):
    ctx = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id': settings.FACEBOOK_APP_ID,
        'guindex_counties': GuindexParameters.SUPPORTED_COUNTIES,
        'debug': settings.DEBUG,
        'async_template_loading': True,
    }
    if extra:
        ctx.update(extra)
    return ctx
