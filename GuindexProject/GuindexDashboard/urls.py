from django.conf.urls import url, include

from dashing.utils import router

from GuindexDashboard import views


urlpatterns = [
    url(r'^dashboard/', include(router.urls)),
]
