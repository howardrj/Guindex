import logging

from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import permissions

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

class GuinnessList(generics.ListCreateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class   = GuinnessSerializer

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessList request")

        # Access base class constructor
        super(GuinnessList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Guinness")

        # Sets creator field in Guinness object
        # prior to calling object's save method
        serializer.save(creator = self.request.user)

    def get_queryset(self):
        return Guinness.objects.all()


class GuinnessDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class   = GuinnessSerializer

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnesDetail request")

        # Access base class constructor
        super(GuinnessDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Guinness.objects.all()


###################################
# GuinnessPendingCreate API Views #
###################################

class GuinnessPendingCreateList(generics.ListAPIView):

    serializer_class   = GuinnessPendingCreateSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingCreateList request")

        # Access base class constructor
        super(GuinnessPendingCreateList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuinnessPendingCreate.objects.all()


class GuinnessPendingCreateDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = GuinnessPendingCreateSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingCreateDetail request")

        # Access base class constructor
        super(GuinnessPendingCreateDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuinnessPendingCreate.objects.all()


#################
# Pub API Views #
#################

class PubList(generics.ListCreateAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubList request")

        # Access base class constructor
        super(PubList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Pub")

        # Sets creator field in Pub object
        # prior to calling object's save method
        serializer.save(creator = self.request.user)

    def get_queryset(self):
        return Pub.objects.all()


class PubDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubDetail request")

        # Access base class constructor
        super(PubDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Pub object")

        serializer.save(user = self.request.user)

    def get_queryset(self):
        return Pub.objects.all()


##############################
# PubPendingCreate API Views #
##############################


class PubPendingCreateList(generics.ListAPIView):

    serializer_class   = PubPendingCreateSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingCreateList request")

        # Access base class constructor
        super(PubPendingCreateList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingCreate.objects.all()


class PubPendingCreateDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = PubPendingCreateSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingCreateDetail request")

        # Access base class constructor
        super(PubPendingCreateDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingCreate.objects.all()


#############################
# PubPendingPatch API Views #
#############################

class PubPendingPatchList(generics.ListAPIView):

    serializer_class   = PubPendingPatchSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingPatchList request")

        # Access base class constructor
        super(PubPendingPatchList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingPatch.objects.all()


class PubPendingPatchDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = PubPendingPatchSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingPatchDetail request")

        # Access base class constructor
        super(PubPendingPatchDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingPatch.objects.all()


########################
# Statistics API Views #
########################

class StatisticsList(generics.ListAPIView):

    serializer_class   = StatisticsSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received StatisticsList request")

        # Access base class constructor
        super(StatisticsList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return StatisticsSingleton.objects.filter(id = 1)


#########################
# Contributor API Views #
#########################

class ContributorList(generics.ListAPIView):

    serializer_class   = ContributorSerializer
    permission_classes = (permissions.IsAdminUser, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received ContributorList request")

        # Access base class constructor
        super(ContributorList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # Returns null on guindexuser/telegramuser related fields if either
        # does not exist for a User
        # No need for exclude filter
        return User.objects.all()


class ContributorDetail(generics.RetrieveUpdateAPIView):
    """
        A contributor can only patch its own User model.
        The alert settings are the only editable fields.
        A contributor can access detailed serializer for
        its own User model.
    """

    serializer_class   = ContributorSerializer
    permission_classes = (IsContributorOrAdminUser, )
    http_method_names  = ['get', 'patch']  # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received ContributorDetail request")

        # Access base class constructor
        super(ContributorDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # Returns null on guindexuser/telegramuser related fields if either
        # does not exist for a User
        # No need for exclude filter
        return User.objects.all()


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
