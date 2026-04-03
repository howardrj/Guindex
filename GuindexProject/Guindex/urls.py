from django.urls import include, path, re_path
from rest_framework_nested import routers

from Guindex import views

router = routers.SimpleRouter()

router.register(r"^api/pubs", views.PubViewSet)
router.register(r"^api/pending_price_creates", views.GuinnessPendingCreateViewSet)
router.register(r"^api/pending_pub_creates", views.PubPendingCreateViewSet)
router.register(r"^api/pending_pub_patches", views.PubPendingPatchViewSet)
router.register(r"^api/statistics", views.StatisticsViewSet)
router.register(r"^api/contributors", views.ContributorViewSet)

pubs_router = routers.NestedSimpleRouter(router, r"^api/pubs", lookup="pub")
pubs_router.register(
    r"prices",
    views.GuinnessViewSet,
    basename="pub-prices",
)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^", include(pubs_router.urls)),
    path("api/contact/", views.Contact.as_view()),
]
