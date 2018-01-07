from django.conf.urls import url

from GuindexUser import views


urlpatterns = [
    url(r'^contributions/$', views.ContributionsList.as_view()),
    url(r'^contributions/(?P<pk>[0-9]+)$', views.ContributionsDetail.as_view()),
]
