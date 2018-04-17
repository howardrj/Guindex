# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user) 

    context_dict = {}
    
    return render(request, 'index.html', context_dict)
