from django.urls import re_path

from GuindexWebClient import views

urlpatterns = [
    re_path(r'^faq\/?$', views.faq),
    re_path(r'^async_load/(?P<template>.+)$', views.asyncLoadTemplate),
    re_path(r'^$', views.guindexWebClient),
    re_path(r'^(?P<template>.+)$', views.guindexWebClientWithTemplate),
    re_path(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
]

# Note the second is just a dummy url to detect email collisions
