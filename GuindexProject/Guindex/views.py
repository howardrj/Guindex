import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

from rest_framework import generics
from rest_framework import permissions

from Guindex.forms import NewPubForm, NewGuinnessForm
from Guindex.serializers import PubSerializer, GuinnessSerializer, StatisticsSerializer, ContributorSerializer
from Guindex.models import Pub, Guinness, StatisticsSingleton
from GuindexParameters import GuindexParameters
import GuindexUtils

from UserProfile.models import UserProfile
from UserProfile.UserProfileParameters import UserProfileParameters

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def guindex(request):

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    try:
        user_profile = GuindexUtils.getUserProfileFromUser(request.user)
        logger.debug("Found UserProfile %s with user '%s'", user_profile, request.user)
    except:
        logger.error("Could not retrieve UserProfile with user '%s'. Raising 404 exception", request.user)

        error_message = "No UserProfile exists with user '%s'" % request.user

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict, status = 404)

    context_dict = {'new_pub_form'           : NewPubForm(),
                    'new_guinness_form'      : NewGuinnessForm(),
                    'user_profile'           : user_profile,
                    'user_profile_parameters': UserProfileParameters.getParameters(),
                    'guindex_parameters'     : GuindexParameters.getParameters(),
                    }

    return render(request, 'guindex_main.html', context_dict)


@login_required
@require_http_methods(['GET'])
def pendingContributions(request):

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    try:
        user_profile = GuindexUtils.getUserProfileFromUser(request.user)
        logger.debug("Found UserProfile %s with user '%s'", user_profile, request.user)
    except:
        logger.error("Could not retrieve UserProfile with user '%s'. Raising 404 exception", request.user)

        error_message = "No UserProfile exists with user '%s'" % request.user

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict, status = 404)

    if not user_profile.user.is_staff:

        logger.error("This resource is only available to staff members")

        error_message = "This resource is only available to staff members."

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict, status = 404)

    context_dict = {'user_profile'           : user_profile,
                    'user_profile_parameters': UserProfileParameters.getParameters(),
                    'guindex_parameters'     : GuindexParameters.getParameters(),
                    }

    return render(request, 'guindex_pending_contributions.html', context_dict)


class PubList(generics.ListCreateAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.error("Received PubList request")

        # Access base class constructor
        super(PubList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Pub")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            raise ValidationError('Could not retrieve UserProfile from request')

        # Sets pendingApprovalContributor field in Pub object
        # prior to calling object's save method
        pub = serializer.save(pendingApprovalContributor = user_profile)

        # On create success
        serializer.onCreateSuccess(pub, self.request)

    def get_queryset(self):
        return Pub.objects.filter(pendingApproval = False, pendingApprovalRejected = False)


class PubDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.error("Received PubDetail request")

        # Access base class constructor
        super(PubDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Pub object")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            raise ValidationError('Could not retrieve UserProfile from request')

        # TODO Update this
        pub = serializer.save(creator = user_profile)

        # On update success
        serializer.onUpdateSuccess(pub)

    def get_queryset(self):
        return Pub.objects.filter(pendingApproval = False, pendingApprovalRejected = False)


class GuinnessList(generics.ListCreateAPIView):

    serializer_class   = GuinnessSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def __init__(self, *args, **kwargs):

        logger.error("Received GuinnessList request")

        # Access base class constructor
        super(GuinnessList, self).__init__(*args, **kwargs)

    def perform_create(self, serializer):

        logger.info("Creating new Guinness")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            raise ValidationError('Could not retrieve UserProfile from request')

        # Sets creator field in Guinness object
        # prior to calling object's save method
        guinness = serializer.save(creator = user_profile)

        # On create success
        serializer.onCreateSuccess(guinness, self.request)

    def get_queryset(self):
        return Guinness.objects.filter(approved = True)


class GuinnessDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = GuinnessSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.error("Received GuinnesDetail request")

        # Access base class constructor
        super(GuinnessDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Guinness object")

        try:
            user_profile = GuindexUtils.getUserProfileFromUser(self.request.user)
            logger.debug("Found UserProfile %s with user '%s'", user_profile, self.request.user)
        except:
            logger.error("Could not retrieve UserProfile with user '%s'", self.request.user)
            raise ValidationError('Could not retrieve UserProfile from request')

        # TODO Update this
        guinness = serializer.save(creator = user_profile)

        # On update success
        serializer.onUpdateSuccess(guinness)

    def get_queryset(self):
        return Guinness.objects.filter(approved = True)


class StatisticsList(generics.ListAPIView):

    serializer_class   = StatisticsSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received StatisticsList request")

        # Access base class constructor
        super(StatisticsList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return StatisticsSingleton.objects.filter(id = 1)


class ContributorList(generics.ListAPIView):

    serializer_class   = ContributorSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributorList request")

        # Access base class constructor
        super(ContributorList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.exclude(guindexuser__isnull = True)


class ContributorDetail(generics.RetrieveUpdateAPIView):

    serializer_class   = ContributorSerializer
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributorDetail request")

        # Access base class constructor
        super(ContributorDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # TODO Update this for protection against modifying other user settings
        return UserProfile.objects.exclude(guindexuser__isnull = True)
