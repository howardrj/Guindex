import logging

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.throttling import SimpleRateThrottle

from rest_framework_datatables.filters import DatatablesFilterBackend
from Guindex.filters import GuindexDatatablesFilterBackend

from Guindex.serializers import GuinnessSerializer
from Guindex.serializers import GuinnessPendingCreateSerializer
from Guindex.serializers import PubSerializer
from Guindex.serializers import MapPubSerializer
from Guindex.serializers import PubPendingCreateSerializer
from Guindex.serializers import PubPendingPatchSerializer
from Guindex.serializers import StatisticsSerializer
from Guindex.serializers import ContributorSerializer
from Guindex.serializers import ContactSerializer

from Guindex.models import Guinness, GuinnessPendingCreate
from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import StatisticsSingleton

logger = logging.getLogger(__name__)


#######################
# Permissions Classes #
#######################

class IsAdminOrReadOnly(permissions.IsAdminUser):
    """
        Custom permissions class that only allows admins
        to perform non-safe methods but any user can read
    """

    def has_permission(self, request, view):

        return request.method in ['GET'] or request.user.is_staff


class IsContributorOrAdminUser(permissions.IsAdminUser):
    """
        Custom permissions class that only allows a contributor
        (or admin user) to access its own user object
    """

    def has_permission(self, request, view):

        # Get primary key used in request (assumes trailing '/' in url)
        try:
            pk = int(request.path.split('/')[::-1][1])
        except:
            pk = -1

        return request.user.id == pk or request.user.is_staff


######################
# Guinness API Views #
######################

class GuinnessViewSet(viewsets.ModelViewSet):

    serializer_class   = GuinnessSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'post']

    def get_queryset(self):
        return Guinness.objects.filter(pub = self.kwargs['pub_pk'])


###################################
# GuinnessPendingCreate API Views #
###################################

class GuinnessPendingCreateViewSet(viewsets.ModelViewSet):

    serializer_class   = GuinnessPendingCreateSerializer
    queryset           = GuinnessPendingCreate.objects.all()
    permission_classes = (permissions.IsAdminUser, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS


#################
# Pub API Views #
#################

class PubViewSet(viewsets.ModelViewSet):

    serializer_class   = PubSerializer
    queryset           = Pub.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'post', 'patch']
    filter_backends    = (DjangoFilterBackend, SearchFilter, GuindexDatatablesFilterBackend,)
    filter_fields      = ('name', 'closed', 'servingGuinness', 'county', 'creator', )
    search_fields      = ('name',)


class MapPubPagination(PageNumberPagination):
    """
        Small pages so each JSON response stays under proxy/browser size limits.
        (A single ~5000-pub JSON payload was being truncated mid-transfer.)
    """
    page_size = 250
    page_size_query_param = 'page_size'
    max_page_size = 500


class MapPubList(generics.ListAPIView):
    """
        Approved pubs for the live Leaflet map, paginated for reliable delivery.
        Filter with ?county=Dublin (exact match on supported county names).
    """

    serializer_class = MapPubSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = MapPubPagination
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('county', )

    def get_queryset(self):
        # Server-side filter: ?county=Cork returns Cork pubs only (not client-side).
        qs = Pub.objects.all().only(
            'id', 'name', 'latitude', 'longitude', 'closed',
            'servingGuinness', 'lastPrice', 'county', 'lastSubmissionTime',
        ).order_by('name')

        county = (self.request.query_params.get('county') or '').strip()
        if county:
            qs = qs.filter(county=county)

        return qs


##############################
# PubPendingCreate API Views #
##############################

class PubPendingCreateViewSet(viewsets.ModelViewSet):

    serializer_class   = PubPendingCreateSerializer
    queryset           = PubPendingCreate.objects.all()
    permission_classes = (permissions.IsAdminUser, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS


#############################
# PubPendingPatch API Views #
#############################

class PubPendingPatchViewSet(viewsets.ModelViewSet):

    serializer_class   = PubPendingPatchSerializer
    queryset           = PubPendingPatch.objects.all()
    permission_classes = (permissions.IsAdminUser, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS


########################
# Statistics API Views #
########################

class StatisticsViewSet(viewsets.ModelViewSet):

    serializer_class   = StatisticsSerializer
    queryset           = StatisticsSingleton.objects.filter(id = 1)
    permission_classes = (permissions.AllowAny, )
    http_method_names  = ['get']


#########################
# Contributor API Views #
#########################

class ContributorViewSet(viewsets.ModelViewSet):

    serializer_class   = ContributorSerializer
    queryset           = User.objects.all()
    http_method_names  = ['get', 'patch']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = (permissions.IsAdminUser, )
        else:
            permission_classes = (IsContributorOrAdminUser, )

        return [permission() for permission in permission_classes]


#####################
# Contact API Views #
#####################

class ContactThrottle(SimpleRateThrottle):
    scope = "contact"
    rate = "5/hour"  # adjust as needed

    def get_cache_key(self, request, view):
        return self.get_ident(request)

class Contact(generics.CreateAPIView):

    serializer_class   = ContactSerializer
    permission_classes = (permissions.AllowAny, )
    throttle_classes   = [ContactThrottle]

    def __init__(self, *args, **kwargs):

        logger.debug("Received Contact request")

        # Access base class constructor
        super(Contact, self).__init__(*args, **kwargs)
