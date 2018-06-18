from django.conf.urls import include, url
from django.conf import settings

from UserProfile import views
from rest_auth.views import LoginView


urlpatterns = [
    url(r'^api/rest-auth/login/$', LoginView.as_view(), name='rest_login'),
    url(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name = 'fb_login'),
    url(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name = 'fb_connect'),
]

# Allow user registration in debug mode
if settings.DEBUG:
    urlpatterns.append(url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')))
