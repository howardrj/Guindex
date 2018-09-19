import logging

from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets

from Guindex.serializers import GuinnessSerializer
from Guindex.serializers import GuinnessPendingCreateSerializer
from Guindex.serializers import PubSerializer
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
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS


#################
# Pub API Views #
#################

class PubViewSet(viewsets.ModelViewSet):

    serializer_class   = PubSerializer
    queryset           = Pub.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'post', 'patch']


##############################
# PubPendingCreate API Views #
##############################

class PubPendingCreateViewSet(viewsets.ModelViewSet):

    serializer_class   = PubPendingCreateSerializer
    queryset           = PubPendingCreate.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS


#############################
# PubPendingPatch API Views #
#############################

class PubPendingPatchViewSet(viewsets.ModelViewSet):

    serializer_class   = PubPendingPatchSerializer
    queryset           = PubPendingPatch.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
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

    def get_permission(self):

        if self.action == 'list':
            permission_classes = (permissions.IsAdminUser, )
        else:
            permission_classes = (IsContributorOrAdminUser, )

        return [permission() for permission in permission_classes]


#####################
# Contact API Views #
#####################

class Contact(generics.CreateAPIView):

    serializer_class   = ContactSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received Contact request")

        # Access base class constructor
        super(Contact, self).__init__(*args, **kwargs)
