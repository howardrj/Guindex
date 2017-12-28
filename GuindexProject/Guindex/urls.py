from django.conf.urls import url

from Guindex import views


urlpatterns = [
    url(r'^guindex/$', views.guindex),
    url(r'^guindex_alerts/$', views.guindexAlertSettings),
    url(r'^pubs/$', views.PubList.as_view()), # API view
    url(r'^pubs/(?P<pk>[0-9]+)/$', views.PubDetail.as_view()), # API view
    url(r'^guinness/$', views.GuinnessList.as_view()), # API view
    url(r'^guinness/(?P<pk>[0-9]+)/$', views.GuinnessDetail.as_view()), # API view
]
