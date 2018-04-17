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

from Guindex import urls as GuindexUrls

from GuindexWebClient import urls as GuindexWebClientUrls

from TopLevel import urls as TopLevelUrls

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view


urlpatterns = []

# Append django admin url
urlpatterns.append(url(r'^admin/', admin.site.urls))

# Append UserProfile views
urlpatterns.extend(UserProfileUrls.urlpatterns)

# Append Guindex views
urlpatterns.extend(GuindexUrls.urlpatterns)

# Append GuindexWebClient views
urlpatterns.extend(GuindexWebClientUrls.urlpatterns)

# Append TopLevel views
urlpatterns.extend(TopLevelUrls.urlpatterns)

# Append HTTP API schema url
schema_view = get_schema_view(title='Guindex HTTP API')
urlpatterns.append(url(r'^api/schema/$', schema_view))

# Append HTTP API docs url
# urlpatterns.append(url(r'^api/docs/', include_docs_urls(title='Guindex HTTP API')))

# TODO
# Append 404 view last
