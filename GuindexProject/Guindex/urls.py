from django.conf.urls import url

from Guindex import views


urlpatterns = [
    url(r'^guindex/$', views.guindex),
    url(r'^pending_contributions/$', views.pendingContributions),
    url(r'^approve_contribution/$', views.approveContribution),
    url(r'^are_pending_contributions/$', views.arePendingContributions),
    url(r'^guindex_alerts/$', views.guindexAlertSettings),
    url(r'^api/pubs/$', views.PubList.as_view()), # API view
    url(r'^api/pubs/(?P<pk>[0-9]+)/$', views.PubDetail.as_view()), # API view
    url(r'^api/guinness/$', views.GuinnessList.as_view()), # API view
    url(r'^api/guinness/(?P<pk>[0-9]+)/$', views.GuinnessDetail.as_view()), # API view
    url(r'^api/statistics/$', views.StatisticsList.as_view()), # API view
    url(r'^api/contributions/$', views.ContributionsList.as_view()),
    url(r'^api/contributions/(?P<pk>[0-9]+)$', views.ContributionsDetail.as_view()),
    url(r'^map/$', views.guindexMapFull),
]
