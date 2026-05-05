# -*- coding: utf-8 -*-
import json
import logging

from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseRedirect

from Guindex.GuindexParameters import GuindexParameters
from GuindexWebClient.map_view_function import create_guindex_map
from GuindexWebClient.spa_utils import web_client_template_context

logger = logging.getLogger(__name__)


def faq(request):

    logger.info("Redirecting to FAQ")

    return HttpResponseRedirect('/info_faq/')


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user)

    return render(request, 'guindex_web_client.html', web_client_template_context(request))


def password_reset_confirm_page(request, uid, token):
    logger.info("Password reset confirm page for uid prefix=%s", (uid or "")[:8])
    ctx = web_client_template_context(request)
    ctx["uid_json"] = json.dumps(uid)
    ctx["token_json"] = json.dumps(token)
    return render(request, 'password_reset_confirm_standalone.html', ctx)


def guindexWebClientWithTemplate(request, template):

    logger.info("Received Guindex web client request from user %s for template %s", request.user, template)

    if template[-1] == '/':
        template = template[:-1]

    try:
        rendered_template = render(request, template + '.html', {})
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

    if template == 'guindex_map' or template == "new_guindex_map":
        return rendered_template

    return render(request, 'guindex_web_client.html', web_client_template_context(request))


def asyncLoadTemplate(request, template):

    logger.info("Received async load template for template %s request from user %s", template, request.user)

    context_dict = web_client_template_context(
        request,
        extra={'async_template_loading': False},
    )

#    if template == "map":
 #       folium_map = create_guindex_map()

  #      context_dict['map'] = folium_map._repr_html_()

    try:
        return render(request, template + '.html', context_dict)
    except:
        return HttpResponseNotFound('<h1> Page not found </h1>')

