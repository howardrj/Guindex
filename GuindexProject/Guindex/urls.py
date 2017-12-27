from django.conf.urls import url

from Guindex import views


urlpatterns = [
    url(r'^guindex/$', views.guindex),
    url(r'^guindex_alerts/$', views.guindexAlertSettings)
]
