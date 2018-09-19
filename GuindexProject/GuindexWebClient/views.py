# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseNotFound

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user)

    context_dict = {
        'google_maps_api_key' : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'     : settings.FACEBOOK_APP_ID,
        'guindex_counties'    : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'               : settings.DEBUG,
    }
    
    return render(request, 'guindex_web_client.html', context_dict)

def guindexWebClientWithTemplate(request, template):

    logger.info("Received Guindex web client request from user %s for template %s", request.user, template)

    if template[-1] == '/':
        template = template[:-1]

    try:
        rendered_template = render(request, template + '.html', {})
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

    if template == 'guindex_map':
        return rendered_template

    context_dict = {
        'google_maps_api_key' : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'     : settings.FACEBOOK_APP_ID,
        'guindex_counties'    : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'               : settings.DEBUG,
    }
    
    return render(request, 'guindex_web_client.html', context_dict)
