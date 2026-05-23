from django.conf.urls import url

from GuindexWebClient import views

urlpatterns = [
    url(r'^faq\/?$', views.faq),
    url(r'^live_guindex_map/?$', views.serve_live_guindex_map),
    url(r'^new_guindex_map/?$', views.serve_new_guindex_map),
    url(r'^async_load/(?P<template>.+)$', views.asyncLoadTemplate),
    url(
        r'^password/reset/confirm/(?P<uid>[^/]+)/(?P<token>[^/]+)/$',
        views.password_reset_confirm_page,
        name='password_reset_confirm',
    ),
    url(r'^$', views.guindexWebClient),
    url(r'^(?P<template>.+)$', views.guindexWebClientWithTemplate),
    url(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
]

# Note the second is just a dummy url to detect email collisions
