"""GuindexProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from UserProfile import urls as UserProfileUrls
from UserProfile.views import error404

from Guindex import urls as GuindexUrls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

# Append UserProfile views
urlpatterns.extend(UserProfileUrls.urlpatterns)

# Append Guindex views
urlpatterns.extend(GuindexUrls.urlpatterns)

# Append 404 view last
urlpatterns.append(url(r'.*', error404))
