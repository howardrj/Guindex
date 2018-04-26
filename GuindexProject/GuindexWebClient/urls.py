from django.conf.urls import include, url

from GuindexWebClient import views

urlpatterns = [
	url(r'^$', views.guindexWebClient),
    url(r'^social_sigup/$', views.guindexWebClient, name = 'socialaccount_signup'),
]

# Note the second is just a dummy url to detect email collisions 
