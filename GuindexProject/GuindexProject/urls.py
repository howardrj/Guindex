from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from Guindex import urls as GuindexUrls
from GuindexWebClient import urls as GuindexWebClientUrls
from UserProfile import urls as UserProfileUrls

urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns.extend(UserProfileUrls.urlpatterns)
urlpatterns.extend(GuindexUrls.urlpatterns)

urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

urlpatterns.extend(GuindexWebClientUrls.urlpatterns)
