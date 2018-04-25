# -*- coding: utf-8 -*-
import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def guindexWebClient(request):

    logger.info("Received Guindex web client request from user %s", request.user) 

    context_dict = {}
    
    return render(request, 'index.html', context_dict)

def index(request):

    return render(request, 'index_new_new.html')

def analysis(request):

    return render(request, 'analysis.html')

def geo(request):    
    return render(request, 'geo.html')

def social(request):    
    return render(request, 'social.html')

def pubdist(request):    
    return render(request, 'pubdist.html')

def travdrnk(request):    
    return render(request, 'travdrnk.html')

def info(request):    
    return render(request, 'info.html')

def links(request):    
    return render(request, 'links.html')

def guindexMapFull(request):
    return render(request, 'guindex_map_full.html')

def tos(request):    
    return render(request, 'tos.html')

def privacy(request):    
    return render(request, 'privacy.html')
