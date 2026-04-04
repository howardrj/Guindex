# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.views.decorators.clickjacking import xframe_options_sameorigin

from Guindex.GuindexParameters import GuindexParameters

from GuindexWebClient.forms import GuindexMapCountyForm
from GuindexWebClient.guindex_map_folium import create_guindex_map

logger = logging.getLogger(__name__)


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
        'debug'                 : settings.DEBUG,
        'async_template_loading': True,
        'google_auth_client_id' : settings.GOOGLE_AUTH_CLIENT_ID,
    }

    return render(request, 'guindex_web_client.html', context_dict)


@xframe_options_sameorigin
def guindex_map_page(request):
    """County selector and Folium map (served inside the map iframe)."""
    context = {}
    if request.method == "POST":
        form = GuindexMapCountyForm(request.POST)
        if form.is_valid():
            county = form.cleaned_data["county"]
            folium_map = create_guindex_map(county)
            context["map"] = folium_map._repr_html_()
    else:
        form = GuindexMapCountyForm()

    context["form"] = form
    response = render(request, "guindex_map.html", context)
    # OSM tile policy: tile requests must include Referer. Without an explicit
    # policy, embedded contexts can omit it (403). origin-when-cross-origin
    # sends the site origin on HTTPS→HTTPS cross-origin requests (e.g. to OSM).
    response["Referrer-Policy"] = "origin-when-cross-origin"
    return response


def guindexWebClientWithTemplate(request, template):

    logger.info("Received Guindex web client request from user %s for template %s", request.user, template)

    if template[-1] == '/':
        template = template[:-1]

    if template == "guindex_map":
        return guindex_map_page(request)

    try:
        rendered_template = render(request, template + ".html", {})
    except TemplateDoesNotExist:
        return HttpResponseNotFound("<h1> Page not found </h1>")

    context_dict = {
        'google_maps_api_key'   : settings.GOOGLE_MAPS_API_KEY,
        'google_analytics_key'  : settings.GOOGLE_ANALYTICS_KEY,
        'facebook_app_id'       : settings.FACEBOOK_APP_ID,
        'guindex_counties'      : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'                 : settings.DEBUG,
        'async_template_loading': True,
        'google_auth_client_id' : settings.GOOGLE_AUTH_CLIENT_ID,
    }

    return render(request, 'guindex_web_client.html', context_dict)


def asyncLoadTemplate(request, template):

    logger.info("Received async load template for template %s request from user %s", template, request.user)

    context_dict = {
        'google_maps_api_key'   : settings.GOOGLE_MAPS_API_KEY,
        'guindex_counties'      : GuindexParameters.SUPPORTED_COUNTIES,
        'debug'                 : settings.DEBUG,
        'async_template_loading': False,
    }

    try:
        return render(request, template + ".html", context_dict)
    except TemplateDoesNotExist:
        return HttpResponseNotFound("<h1> Page not found </h1>")
