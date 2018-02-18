from django.conf.urls import url

from TopLevel import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^statistics/$', views.stats),
    url(r'^analysis/$', views.analysis),
    url(r'^analysis/geography/$', views.geo),
    url(r'^analysis/social/$', views.social),
    url(r'^analysis/pubdist/$', views.pubdist),
    url(r'^analysis/travdrnk/$', views.travdrnk),
    url(r'^info/$', views.info),
    url(r'^links/$', views.links),
    url(r'^test/$', views.test),
    url(r'^tos/$', views.tos),
    url(r'^privacy/$', views.privacy),
]
