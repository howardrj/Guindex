from django.conf.urls import include, url

from UserProfile import views
from rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)


urlpatterns = [
    url(r'^api/rest-auth/', include('rest_auth.urls')),
    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name = 'fb_login'),
    url(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name = 'fb_connect'),
    url(
        r'^api/socialaccounts/$',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    url(
        r'^socialaccounts/(?P<pk>\d+)/disconnect/$',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    )
]
