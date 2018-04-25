import logging
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework import generics
from rest_framework import permissions



