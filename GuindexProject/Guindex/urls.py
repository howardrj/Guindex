from django.conf.urls import url, include
from rest_framework_nested import routers

from Guindex import views

router = routers.SimpleRouter()

router.register(r'^api/pubs', views.PubViewSet)
router.register(r'^api/pending_price_creates', views.GuinnessPendingCreateViewSet)
router.register(r'^api/pending_pub_creates', views.PubPendingCreateViewSet)
router.register(r'^api/pending_pub_patches', views.PubPendingPatchViewSet)
router.register(r'^api/statistics', views.StatisticsViewSet)
router.register(r'^api/contributors', views.ContributorViewSet)

pubs_router = routers.NestedSimpleRouter(router, r'^api/pubs', lookup = 'pub')
pubs_router.register(r'prices', views.GuinnessViewSet, base_name = 'pub-prices')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(pubs_router.urls)),
    url(r'^api/contact/$', views.Contact.as_view()),
]
