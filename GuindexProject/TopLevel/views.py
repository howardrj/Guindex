import logging
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework import generics
from rest_framework import permissions


def index(request):    
    return render(request, 'index_new.html')

def stats(request):    
    return render(request, 'stats.html')

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