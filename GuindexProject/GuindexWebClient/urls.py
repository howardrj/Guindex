from django.conf.urls import include, url
from django.views.decorators.cache import cache_page

from Guindex.GuindexParameters import GuindexParameters
from GuindexWebClient import views

urlpatterns = [
    url(r'^$', cache_page(GuindexParameters.CACHE_TIMEOUT)(views.guindexWebClient)),
    url(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
    url(r'^.', cache_page(GuindexParameters.CACHE_TIMEOUT)(views.guindexWebClient)),
]

# Note the second is just a dummy url to detect email collisions 
