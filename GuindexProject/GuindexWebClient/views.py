# -*- coding: utf-8 -*-
import json
import logging
import os

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect, FileResponse

from Guindex.GuindexParameters import GuindexParameters


def _web_client_context(request, **extra):
    """Shared template context for the main web client and async tab loads."""
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id': settings.FACEBOOK_APP_ID,
        'guindex_counties': GuindexParameters.SUPPORTED_COUNTIES,
        # Keep True so templates load .js sources (same as before); production
        # still uses .min.js for the bundles listed in guindex_web_client.html.
        'debug': True,
        'async_template_loading': True,
    }
    context.update(extra)
    return context

logger = logging.getLogger(__name__)

NEW_GUINDEX_MAP_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates',
    'new_guindex_map.html',
)


def serve_live_guindex_map(request):
    """
    Live Leaflet map: loads pub markers from /api/map/pubs/ when opened with
    ?county=Name or ?load=all (set by parent page county dropdown via iframe src).
    """
    map_api_url = request.build_absolute_uri('/api/map/pubs/')

    county_param = (request.GET.get('county') or '').strip()
    load_all = request.GET.get('load') == 'all'
    initial_county = county_param if county_param in GuindexParameters.SUPPORTED_COUNTIES else ''
    load_on_start = load_all or bool(initial_county)

    county_viewports = {}
    for county in GuindexParameters.SUPPORTED_COUNTIES:
        county_viewports[county] = GuindexParameters.get_county_map_viewport(county)

    context = {
        'map_center_lat': GuindexParameters.DUBLIN_CENTER_LATITUDE,
        'map_center_lng': GuindexParameters.DUBLIN_CENTER_LONGITUDE,
        'map_zoom': GuindexParameters.MAP_ZOOM_LEVEL,
        'map_api_url': map_api_url,
        'county_viewports_json': json.dumps(county_viewports),
        'load_on_start_json': json.dumps(load_on_start),
        'initial_county_json': json.dumps(initial_county),
    }

    return render(request, 'live_guindex_map.html', context)


def serve_new_guindex_map(request):
    """
    Serve the pre-generated Folium map as a static file with Content-Length set.
    Avoids Django template rendering for the ~5MB HTML file, which can cause
    NS_ERROR_NET_PARTIAL_TRANSFER in browsers when the response is truncated.
    """
    if not os.path.isfile(NEW_GUINDEX_MAP_TEMPLATE):
        logger.error("Map template missing at %s", NEW_GUINDEX_MAP_TEMPLATE)
        return HttpResponseNotFound('<h1>Map not found</h1>')

    map_file = open(NEW_GUINDEX_MAP_TEMPLATE, 'rb')
    response = FileResponse(map_file, content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=300'
    return response


def faq(request):

    logger.info("Redirecting to FAQ")

    return HttpResponseRedirect('/info_faq/')


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user)

    return render(request, 'guindex_web_client.html', _web_client_context(request))


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

    if template == 'live_guindex_map':
        return serve_live_guindex_map(request)

    if template == 'new_guindex_map':
        return serve_new_guindex_map(request)

    return render(request, 'guindex_web_client.html', _web_client_context(request))


def asyncLoadTemplate(request, template):

    logger.info("Received async load template for template %s request from user %s", template, request.user)

    context_dict = _web_client_context(request, async_template_loading=False)

#    if template == "map":
 #       folium_map = create_guindex_map()

  #      context_dict['map'] = folium_map._repr_html_()

    try:
        return render(request, template + '.html', context_dict)
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

