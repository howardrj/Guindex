# -*- coding: utf-8 -*-
"""Shared template context for ``guindex_web_client.html`` (SPA shell)."""
from django.conf import settings

from Guindex.GuindexParameters import GuindexParameters


def web_client_template_context(request, extra=None):
    """
    Context for ``guindex_web_client.html`` and related shells.

    Replaces the former duplicated ``context_dict`` in ``views.guindexWebClient``
    and ``views.guindexWebClientWithTemplate`` (maps, analytics, Facebook, counties,
    debug, async loading flag). Pass ``extra`` to override, e.g.
    ``async_template_loading`` for ``asyncLoadTemplate``.
    """
    ctx = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "google_analytics_key": settings.GOOGLE_ANALYTICS_KEY,
        "facebook_app_id": settings.FACEBOOK_APP_ID,
        "guindex_counties": GuindexParameters.SUPPORTED_COUNTIES,
        "debug": True,
        "async_template_loading": True,
    }
    if extra:
        ctx.update(extra)
    return ctx
