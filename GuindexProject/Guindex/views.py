import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from rest_framework import generics
from rest_framework import permissions

from Guindex.forms import NewPubForm, NewGuinnessForm

from Guindex.serializers import PubGetSerializer, PubPostSerializer, PubPatchSerializer
from Guindex.serializers import PubPendingCreateGetSerializer, PubPendingCreatePatchSerializer
from Guindex.serializers import PubPendingPatchGetSerializer, PubPendingPatchPatchSerializer
from Guindex.serializers import GuinnessGetSerializer, GuinnessPostSerializer, GuinnessPatchSerializer
from Guindex.serializers import GuinnessPendingCreateGetSerializer, GuinnessPendingCreatePatchSerializer
from Guindex.serializers import GuinnessPendingPatchGetSerializer, GuinnessPendingPatchPatchSerializer
from Guindex.serializers import StatisticsSerializer
from Guindex.serializers import ContributorGetSerializer, ContributorPatchSerializer

from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import Guinness, GuinnessPendingCreate, GuinnessPendingPatch
from Guindex.models import StatisticsSingleton
from GuindexParameters import GuindexParameters
import GuindexUtils

from UserProfile.models import UserProfile
from UserProfile.UserProfileParameters import UserProfileParameters

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

        try:
            view.userProfile = GuindexUtils.getUserProfileFromUser(request.user)
            logger.debug("Found UserProfile %s with user '%s'", view.userProfile, request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", request.user)
            return False

        return request.method in ['GET'] or view.userProfile.user.is_staff


class IsContributorOrReadOnly(permissions.IsAdminUser):
    """
        Custom permissions class that only allows a contributor
        to update it's own fields
    """

    def has_permission(self, request, view):

        # Get primary key used in request
        try:
            pk = int(request.path.split('/')[::-1][1])
        except:
            return False

        try:
            view.userProfile = GuindexUtils.getUserProfileFromUser(request.user)
            logger.debug("Found UserProfile %s with user '%s'", view.userProfile, request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", request.user)
            return False

        return request.method in ['GET'] or view.userProfile.id == pk


#################
# Pub API Views #
#################

class PubList(generics.ListCreateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubList request")

        # Access base class constructor
        super(PubList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Pub")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            return

        # Sets creator field in Pub object
        # prior to calling object's save method
        serializer.save(creator = user_profile)

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return PubPostSerializer
        return PubGetSerializer

    def get_queryset(self):
        return Pub.objects.all()


class PubDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubDetail request")

        # Access base class constructor
        super(PubDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Pub object")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            return

        serializer.save(userProfile = user_profile)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            return PubPatchSerializer
        return PubGetSerializer

    def get_queryset(self):
        return Pub.objects.all()


class PubPendingCreateList(generics.ListAPIView):

    serializer_class   = PubPendingCreateGetSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingCreateList request")

        # Access base class constructor
        super(PubPendingCreateList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingCreate.objects.all()


class PubPendingCreateDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingCreateDetail request")

        # Access base class constructor
        super(PubPendingCreateDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            return PubPendingCreatePatchSerializer
        return PubPendingCreateGetSerializer

    def get_queryset(self):
        return PubPendingCreate.objects.all()


class PubPendingPatchList(generics.ListAPIView):

    serializer_class = PubPendingPatchGetSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingPatchList request")

        # Access base class constructor
        super(PubPendingPatchList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return PubPendingPatch.objects.all()


class PubPendingPatchDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received PubPendingPatchDetail request")

        # Access base class constructor
        super(PubPendingPatchDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            return PubPendingPatchPatchSerializer
        return PubPendingPatchGetSerializer

    def get_queryset(self):
        return PubPendingPatch.objects.all()


######################
# Guinness API Views #
######################

class GuinnessList(generics.ListCreateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessList request")

        # Access base class constructor
        super(GuinnessList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Guinness")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            return

        # Sets creator field in Guinness object
        # prior to calling object's save method
        serializer.save(creator = user_profile)

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return GuinnessPostSerializer
        return GuinnessGetSerializer

    def get_queryset(self):
        return Guinness.objects.all()


class GuinnessDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnesDetail request")

        # Access base class constructor
        super(GuinnessDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Guinness object")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            return

        serializer.save(userProfile = user_profile)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return GuinnessPatchSerializer
        return GuinnessGetSerializer

    def get_queryset(self):
        return Guinness.objects.all()


class GuinnessPendingCreateList(generics.ListAPIView):

    serializer_class   = GuinnessPendingCreateGetSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingCreateList request")

        # Access base class constructor
        super(GuinnessPendingCreateList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuinnessPendingCreate.objects.all()


class GuinnessPendingCreateDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingCreateDetail request")

        # Access base class constructor
        super(GuinnessPendingCreateDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            return GuinnessPendingCreatePatchSerializer
        return GuinnessPendingCreateGetSerializer

    def get_queryset(self):
        return GuinnessPendingCreate.objects.all()


class GuinnessPendingPatchList(generics.ListAPIView):

    serializer_class   = GuinnessPendingPatchGetSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingPatchList request")

        # Access base class constructor
        super(GuinnessPendingPatchList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuinnessPendingPatch.objects.all()


class GuinnessPendingPatchDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received GuinnessPendingPatchDetail request")

        # Access base class constructor
        super(GuinnessPendingPatchDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            return GuinnessPendingPatchPatchSerializer
        return GuinnessPendingPatchGetSerializer

    def get_queryset(self):
        return GuinnessPendingPatch.objects.all()


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

    serializer_class   = ContributorGetSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def __init__(self, *args, **kwargs):

        logger.debug("Received ContributorList request")

        # Access base class constructor
        super(ContributorList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # Returns null on guindexuser/telegramuser related fields if either
        # does not exist for a UserProfile
        # No need for exclude filter
        return UserProfile.objects.all()


class ContributorDetail(generics.RetrieveUpdateAPIView):
    """
        A contributor can allow patch its own UserProfile model.
        The alert settings are the only editable fields
    """

    permission_classes = (IsContributorOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.debug("Received ContributorDetail request")

        # Access base class constructor
        super(ContributorDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ContributorPatchSerializer
        return ContributorGetSerializer

    def get_queryset(self):
        # Returns null on guindexuser/telegramuser related fields if either
        # does not exist for a UserProfile
        # No need for exclude filter
        return UserProfile.objects.all()
