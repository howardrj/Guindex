# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect

from Guindex.GuindexParameters import GuindexParameters
from GuindexWebClient.map_folium import create_guindex_map

logger = logging.getLogger(__name__)


def _map_county_from_request(request):
    """GET county= must match SUPPORTED_COUNTIES; All / empty means no filter."""
    raw = (request.GET.get('county') or '').strip()
    if not raw or raw.lower() == 'all':
        return None
    if raw in GuindexParameters.SUPPORTED_COUNTIES:
        return raw
    logger.warning("Ignoring invalid map county parameter: %r", raw)
    return None


def faq(request):

    logger.info("Redirecting to FAQ")

    return HttpResponseRedirect('/info_faq/')


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user)

    context_dict = {
        'google_maps_api_key'   : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key'  : settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'       : settings.FACEBOOK_APP_ID,
        'guindex_counties'      : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'                 : True,
        'async_template_loading': True,
    }

    return render(request, 'guindex_web_client.html', context_dict)


def guindexWebClientWithTemplate(request, template):

    logger.info("Received Guindex web client request from user %s for template %s", request.user, template)

    if template[-1] == '/':
        template = template[:-1]

    # Folium map from live DB — portfolio pattern: map._repr_html_() | safe
    if template == 'new_guindex_map':
        try:
            guindex_map = create_guindex_map(county=_map_county_from_request(request))
            return render(
                request,
                'new_guindex_map.html',
                {'map': guindex_map._repr_html_()},
            )
        except Exception:
            logger.exception("Failed to build Folium map for new_guindex_map")
            return HttpResponseNotFound('<h1> Map unavailable </h1>')

    try:
        rendered_template = render(request, template + '.html', {})
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

    if template == 'guindex_map':
        return rendered_template

    context_dict = {
        'google_maps_api_key'   : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key'  : settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'       : settings.FACEBOOK_APP_ID,
        'guindex_counties'      : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'                 : True,
        'async_template_loading': True,
    }

    return render(request, 'guindex_web_client.html', context_dict)


def asyncLoadTemplate(request, template):

    logger.info("Received async load template for template %s request from user %s", template, request.user)

    context_dict = {
        'google_maps_api_key'   : settings.GOOGLE_MAPS_API_KEY,
        'guindex_counties'      : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'                 : True,
        'async_template_loading': False,
    }

#    if template == "map":
 #       folium_map = create_guindex_map()

  #      context_dict['map'] = folium_map._repr_html_()

    try:
        return render(request, template + '.html', context_dict)
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

