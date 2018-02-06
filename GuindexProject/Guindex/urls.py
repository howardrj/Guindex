from django.conf.urls import url

from Guindex import views


urlpatterns = [
    url(r'^guindex/$', views.guindex),
    url(r'^pending_contributions/$', views.pendingContributions),
    url(r'^api/pubs/$', views.PubList.as_view()), # API view
    url(r'^api/pubs/(?P<pk>[0-9]+)/$', views.PubDetail.as_view()), # API view
    url(r'^api/guinness/$', views.GuinnessList.as_view()), # API view
    url(r'^api/guinness/(?P<pk>[0-9]+)/$', views.GuinnessDetail.as_view()), # API view
    url(r'^api/statistics/$', views.StatisticsList.as_view()), # API view
    url(r'^api/contributors/$', views.ContributorList.as_view()),
    url(r'^api/contributors/(?P<pk>[0-9]+)/$', views.ContributorDetail.as_view()),
    # url(r'^api/pendingContributions/$', view.PendingContributionList.as_view()), # TODO Implement
    # url(r'^api/pendingContributions/$(?P<pk>[0-9]+)/', view.PendingContributionDetail.as_view()), # TODO Implement
]
