# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger(__name__)


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user)

    context_dict = {
        'google_maps_api_key' : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'     : settings.FACEBOOK_APP_ID,
    }
    
    return render(request, 'guindex_web_client.html', context_dict)
