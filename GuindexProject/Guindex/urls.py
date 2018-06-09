from django.conf.urls import url

from Guindex import views
from django.views.decorators.cache import cache_page


urlpatterns = [
    url(r'^api/pubs/$', cache_page(60 * 30)(views.PubList.as_view())),
    url(r'^api/pubs/(?P<pk>[0-9]+)/$', views.PubDetail.as_view()),
    url(r'^api/pubs/pending/create/$', views.PubPendingCreateList.as_view()),
    url(r'^api/pubs/pending/create/(?P<pk>[0-9]+)/$', views.PubPendingCreateDetail.as_view()),
    url(r'^api/pubs/pending/patch/$', views.PubPendingPatchList.as_view()),
    url(r'^api/pubs/pending/patch/(?P<pk>[0-9]+)/$', views.PubPendingPatchDetail.as_view()),
    url(r'^api/guinness/$', views.GuinnessList.as_view()),
    url(r'^api/guinness/(?P<pk>[0-9]+)/$', views.GuinnessDetail.as_view()),
    url(r'^api/guinness/pending/create/$', views.GuinnessPendingCreateList.as_view()),
    url(r'^api/guinness/pending/create/(?P<pk>[0-9]+)/$', views.GuinnessPendingCreateDetail.as_view()),
    url(r'^api/guinness/pending/patch/$', views.GuinnessPendingPatchList.as_view()),
    url(r'^api/guinness/pending/patch/(?P<pk>[0-9]+)/$', views.GuinnessPendingPatchDetail.as_view()),
    url(r'^api/statistics/$', views.StatisticsList.as_view()),
    url(r'^api/contributors/$', views.ContributorList.as_view()),
    url(r'^api/contributors/(?P<pk>[0-9]+)/$', views.ContributorDetail.as_view()),
    url(r'^api/contact/$', views.Contact.as_view()),
]
