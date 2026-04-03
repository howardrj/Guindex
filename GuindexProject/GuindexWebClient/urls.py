from django.urls import path, re_path

from GuindexWebClient import views

urlpatterns = [
    re_path(r"^faq/?$", views.faq),
    re_path(r"^async_load/(?P<template>.+)$", views.asyncLoadTemplate),
    path("", views.guindexWebClient),
    path("social_sigup/", views.guindexWebClient, name="socialaccount_signup"),
    re_path(r"^(?P<template>.+)$", views.guindexWebClientWithTemplate),
]
