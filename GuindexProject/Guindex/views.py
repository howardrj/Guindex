import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

from rest_framework import generics
from rest_framework import permissions

from Guindex.forms import NewPubForm, NewGuinnessForm
from Guindex.serializers import PubGetSerializer, PubPostSerializer, PubPatchSerializer
from Guindex.serializers import GuinnessGetSerializer, GuinnessPostSerializer, GuinnessPatchSerializer
from Guindex.serializers import ContributorGetSerializer, ContributorPatchSerializer
from Guindex.serializers import StatisticsSerializer
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
        serializer.onCreateSuccess(pub, self.request, user_profile)

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return PubPostSerializer
        return PubGetSerializer

    def get_queryset(self):
        return Pub.objects.filter()


class PubDetail(generics.RetrieveUpdateAPIView):

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

        pub = serializer.save()

        # On patch success
        serializer.onPatchSuccess(pub, self.request, user_profile)

    def get_serializer_class(self):

        if self.request.method == 'PATCH':
            if self.request.user.is_staff:
                return PubPatchSerializer.StaffMemberSerializer
            else:
                return PubPatchSerializer.NormalUserSerializer
        return PubGetSerializer

    def get_queryset(self):
        return Pub.objects.filter()


class GuinnessList(generics.ListCreateAPIView):

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
        serializer.onCreateSuccess(guinness, self.request, user_profile)

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return GuinnessPostSerializer
        return GuinnessGetSerializer

    def get_queryset(self):
        return Guinness.objects.all()


class GuinnessDetail(generics.RetrieveUpdateAPIView):
    """
        Note: Only staff members can patch a Guinness object
        i.e. permission class IsAdminUser
    """

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

    permission_classes = (IsAdminOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.error("Received GuinnesDetail request")

        # Access base class constructor
        super(GuinnessDetail, self).__init__(*args, **kwargs)

    def perform_update(self, serializer):

        logger.info("Updating Guinness object")

        # UserProfile member is set in has_permission function
        # Note: this won't save object yet, just returns updated object
        guinness = serializer.save()

        # On update success
        serializer.onPatchSuccess(guinness, self.request, self.userProfile)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return GuinnessPatchSerializer
        return GuinnessGetSerializer

    def get_queryset(self):
        return Guinness.objects.all()


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

    serializer_class   = ContributorGetSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributorList request")

        # Access base class constructor
        super(ContributorList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return UserProfile.objects.exclude(guindexuser__isnull = True).exclude(telegramuser__isnull = True)


class ContributorDetail(generics.RetrieveUpdateAPIView):
    """
        A contributor can allow patch it's own UserProfile model.
        The alert settings are the only editable fields
    """

    class IsContributorOrReadOnly(permissions.IsAdminUser):
        """
            Custom permissions class that only allows admins
            to perform non-safe methods but any user can read
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

    permission_classes = (IsContributorOrReadOnly, )
    http_method_names  = ['get', 'patch'] # Disallow PUTS

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributorDetail request")

        # Access base class constructor
        super(ContributorDetail, self).__init__(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ContributorPatchSerializer
        return ContributorGetSerializer

    def get_queryset(self):
        return UserProfile.objects.exclude(guindexuser__isnull = True).exclude(telegramuser__isnull = True)
