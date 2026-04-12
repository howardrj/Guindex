from django.urls import include, re_path
from django.conf import settings

from UserProfile import views
from dj_rest_auth.views import LoginView


urlpatterns = [
    re_path(r'^api/rest-auth/login/$', LoginView.as_view(), name='rest_login'),
    re_path(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name = 'fb_login'),
    re_path(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name = 'fb_connect'),
]

# Allow user registration in debug mode
if settings.DEBUG:
    urlpatterns.append(re_path(r'^api/rest-auth/registration/', include('dj_rest_auth.registration.urls')))
