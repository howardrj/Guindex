from django.conf.urls import include, url

from GuindexWebClient import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    url(r'^$', cache_page(60 * 30)(views.guindexWebClient)),
    url(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
    url(r'^.', cache_page(60*30)(views.guindexWebClient)),
]

# Note the second is just a dummy url to detect email collisions 
