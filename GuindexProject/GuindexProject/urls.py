from django.conf.urls import url
from django.contrib import admin

from Guindex import urls as GuindexUrls

from GuindexWebClient import urls as GuindexWebClientUrls

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view


urlpatterns = []

# Append django admin url
urlpatterns.append(url(r'^admin/', admin.site.urls))

# Append Guindex views
urlpatterns.extend(GuindexUrls.urlpatterns)

# Append HTTP API schema url
schema_view = get_schema_view(title='Guindex HTTP API')
urlpatterns.append(url(r'^api/schema/$', schema_view))

# Append HTTP API docs url
urlpatterns.append(url(r'^api/docs/', include_docs_urls(title='Guindex HTTP API')))

# Append GuindexWebClient views
urlpatterns.extend(GuindexWebClientUrls.urlpatterns)

# TODO
# Append 404 view last
