from django.conf.urls import url

from Guindex import views
from django.views.decorators.cache import cache_page
from Guindex.GuindexParameters import GuindexParameters


urlpatterns = [
    url(r'^api/pubs/$', cache_page(GuindexParameters.CACHE_TIMEOUT)(views.PubList.as_view())),
    url(r'^api/pubs/(?P<pk>[0-9]+)/$', views.PubDetail.as_view()),
    url(r'^api/pubs_pending_create/$', views.PubPendingCreateList.as_view()),
    url(r'^api/pubs_pending_create/(?P<pk>[0-9]+)/$', views.PubPendingCreateDetail.as_view()),
    url(r'^api/pubs_pending_patch/$', views.PubPendingPatchList.as_view()),
    url(r'^api/pubs_pending_patch/(?P<pk>[0-9]+)/$', views.PubPendingPatchDetail.as_view()),
    url(r'^api/guinness/$', views.GuinnessList.as_view()),
    url(r'^api/guinness/(?P<pk>[0-9]+)/$', views.GuinnessDetail.as_view()),
    url(r'^api/guinness_pending_create/$', views.GuinnessPendingCreateList.as_view()),
    url(r'^api/guinness_pending_create/(?P<pk>[0-9]+)/$', views.GuinnessPendingCreateDetail.as_view()),
    url(r'^api/statistics/$', views.StatisticsList.as_view()),
    url(r'^api/contributors/$', views.ContributorList.as_view()),
    url(r'^api/contributors/(?P<pk>[0-9]+)/$', views.ContributorDetail.as_view()),
    url(r'^api/contact/$', views.Contact.as_view()),
]
