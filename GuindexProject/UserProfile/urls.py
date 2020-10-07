from django.conf.urls import include, url
from django.conf import settings

from UserProfile import views
from rest_auth.views import LoginView


urlpatterns = [
    url(r'^api/rest-auth/', include('rest_auth.urls')),
    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls'))
]
