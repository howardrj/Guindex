from django.conf.urls import include, url

from Guindex.GuindexParameters import GuindexParameters
from GuindexWebClient import views

urlpatterns = [
    url(r'^async_load/(?P<template>.+)$', views.asyncLoadTemplate),
    url(r'^$', views.guindexWebClient),
    url(r'^(?P<template>.+)$', views.guindexWebClientWithTemplate),
    url(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
]

# Note the second is just a dummy url to detect email collisions 
