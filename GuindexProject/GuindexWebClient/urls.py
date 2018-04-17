from django.conf.urls import include, url

from GuindexWebClient import views

urlpatterns = [
	url(r'^home/$', views.guindexWebClient),
]
