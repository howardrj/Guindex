from django.urls import include, re_path

from UserProfile import views
from dj_rest_auth.views import LoginView, LogoutView


urlpatterns = [
    re_path(r'^api/rest-auth/login/$', LoginView.as_view(), name='rest_login'),
    re_path(r'^api/rest-auth/logout/$', LogoutView.as_view(), name='rest_logout'),
    re_path(r'^api/rest-auth/facebook/$', views.FacebookLogin.as_view(), name = 'fb_login'),
    re_path(r'^api/rest-auth/facebook/connect/$', views.FacebookConnect.as_view(), name = 'fb_connect'),
    # Public email/password sign-up (abuse mitigation: consider rate limits / CAPTCHA later)
    re_path(r'^api/rest-auth/registration/', include('dj_rest_auth.registration.urls')),
]
