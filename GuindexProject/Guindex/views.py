import logging
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics
from rest_framework import permissions

from Guindex.forms import NewPubForm, NewGuinnessForm, RenamePubForm
from Guindex.serializers import PubSerializer, GuinnessSerializer, StatisticsSerializer
from Guindex.models import Pub, Guinness, StatisticsSingleton
from GuindexParameters import GuindexParameters
import GuindexUtils

from UserProfile.UserProfileParameters import UserProfileParameters

logger = logging.getLogger(__name__)


@login_required
def guindex(request):

    modal_to_display = ""
    warning_text     = ""

    new_pub_form      = NewPubForm()
    rename_pub_form   = RenamePubForm()
    new_guinness_form = NewGuinnessForm()

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    try:
        user_profile = GuindexUtils.getUserProfileFromUser(request.user)
        logger.debug("Found UserProfile %s with user '%s'", user_profile, request.user)
    except:
        logger.error("Could not retrieve UserProfile with user '%s'. Raising 404 exception", request.user)

        error_message = "No UserProfile exists with user '%s'" % request.user

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict)

    if request.method == 'POST':

        if 'new_pub' in request.POST:

            modal_to_display, new_pub_form, warning_text = handleNewPubRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'delete_pub' in request.POST:

            modal_to_display, warning_text = handleDeletePubRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'rename_pub' in request.POST:

            modal_to_display, rename_pub_form, warning_text = handleRenamePubRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'new_guinness' in request.POST:

            modal_to_display, new_guinness_form, warning_text = handleNewGuinnessRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'delete_guinness' in request.POST:

            modal_to_display, warning_text = handleDeleteGuinnessRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'verify_guinness' in request.POST:

            modal_to_display, warning_text = handleVerifyGuinnessRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif 'close_pub' in request.POST:
        
            modal_to_display, warning_text = handleClosePubRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)
            
        elif 'not_serving_guinness' in request.POST: 

            modal_to_display, warning_text = handleNotServingGuinnessRequest(user_profile, request.POST)

            if not modal_to_display:
                return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        else:
            logger.error("Received POST request to unknown resource")

            context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

            return render(request, 'error_404.html', context_dict)

    context_dict = {'pubs'                   : GuindexUtils.getPubs(),
                    'stats'                  : GuindexUtils.getStats(),
                    'personal_contributions' : GuindexUtils.getPersonalContributions(user_profile),
                    'best_contributions'     : GuindexUtils.getBestContributions(),
                    'modal_to_display'       : modal_to_display,
                    'warning_text'           : warning_text,
                    'new_pub_form'           : new_pub_form,
                    'rename_pub_form'        : rename_pub_form,
                    'new_guinness_form'      : new_guinness_form,
                    'username'               : user_profile.user.username,
                    'user_profile_parameters': UserProfileParameters.getParameters(),
                    'guindex_parameters'     : GuindexParameters.getParameters(),
                    'using_email_alerts'     : user_profile.usingEmailAlerts,
                    'using_telegram_alerts'  : user_profile.telegramuser.usingTelegramAlerts,
                    }

    return render(request, 'guindex_main.html', context_dict)


def handleNewPubRequest(userProfile, postData):

    logger.info("Received new pub request - %s", postData)

    modal_to_display = "new_pub_form"
    new_pub_form     = NewPubForm(userProfile = userProfile, data = postData)
    warning_text     = ""

    if new_pub_form.is_valid():

        logger.info("UserProfile %s: New pub form data was valid. Creating new pub", userProfile)

        try:
            new_pub_form.save()
            modal_to_display = ""
        except:
            logger.error("Failed to save form")
            modal_to_display = "warning"
            warning_text = "Failed to save new Pub object."

    else:
        logger.error("UserProfile %s: New pub form data was invalid", userProfile)

    return (modal_to_display, new_pub_form, warning_text)


def handleDeletePubRequest(userProfile, postData):

    logger.info("Received delete pub request - %s", postData)

    modal_to_display = ""
    warning_text     = ""

    try:
        pub_id = postData.get("pub_id")
    except:
        logger.error("Could not get pub id")

        modal_to_display = "warning"
        warning_text = "Could not get pub ID in request."

        return modal_to_display, warning_text

    if not pub_id.isnumeric():
        logger.error("Pub id is not a number %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    if userProfile.user.is_staff:
        logger.debug("UserProfile is a staff member so delete is allowed")

        pub.delete()
    else:
        logger.debug("UserProfile is not a staff member. Not deleting object")

        modal_to_display = "warning"
        warning_text = "This operation is only permitted for staff members."

    return modal_to_display, warning_text


def handleRenamePubRequest(userProfile, postData):

    logger.info("Received rename pub request - %s", postData)

    modal_to_display = "rename_pub_form"
    rename_pub_form  = RenamePubForm(userProfile = userProfile, data = postData)
    warning_text     = ""

    if rename_pub_form.is_valid():

        logger.info("UserProfile %s: Rename pub form data was valid. Renaming pub", userProfile)

        try:
            rename_pub_form.save()
            modal_to_display = ""
        except:
            logger.error("Failed to save form")
            modal_to_display = "warning"
            warning_text = "Failed to save Pub object"

    else:
        logger.error("UserProfile %s: Rename pub form data was invalid", userProfile)

    return (modal_to_display, rename_pub_form, warning_text)


def handleNewGuinnessRequest(userProfile, postData):

    logger.info("Received new Guinness request - %s", postData)

    modal_to_display  = "new_guinness_form"
    new_guinness_form = NewGuinnessForm(userProfile = userProfile, data = postData)
    warning_text      = ""

    if new_guinness_form.is_valid():

        logger.info("UserProfile %s: New Guinness form data was valid. Creating new Guinness", userProfile)

        try:
            new_guinness_form.save()
            modal_to_display = ""
        except:
            logger.error("Failed to save form")
            modal_to_display = "warning"
            warning_text = "Failed to save new Guinness object"

    else:
        logger.error("UserProfile %s: New Guinness form data was invalid", userProfile)

    return (modal_to_display, new_guinness_form, warning_text)


def handleDeleteGuinnessRequest(userProfile, postData):

    logger.info("Received delete Guinness request - %s", postData)

    modal_to_display = ""
    warning_text     = ""

    try:
        guinness_id = postData.get("delete_guinness_id")
    except:
        logger.error("Could not get guinness id")

        modal_to_display = "warning"
        warning_text = "Could not get guinness ID in request."

        return modal_to_display, warning_text

    if not guinness_id.isnumeric():
        logger.error("Guinness id is not a number %s", guinness_id)

        modal_to_display = "warning"
        warning_text = "Invalid guinness ID."

        return modal_to_display, warning_text

    try:
        guinness = Guinness.objects.get(id = int(guinness_id))
        logger.debug("Found Guinness %s", guinness)
    except ObjectDoesNotExist:
        logger.error("No Guinness exists with id %s", guinness_id)

        modal_to_display = "warning"
        warning_text = "Invalid guinness ID."

        return modal_to_display, warning_text

    if userProfile.user.is_staff:
        logger.debug("UserProfile is a staff member so delete is allowed")
        guinness.delete()
    else:
        logger.debug("UserProfile is not a staff member. Not deleting object")

        modal_to_display = "warning"
        warning_text = "This operation is only permitted for staff members."

    return modal_to_display, warning_text


def handleVerifyGuinnessRequest(userProfile, postData):

    logger.info("Received verify Guinness request - %s", postData)

    modal_to_display = ""
    warning_text     = ""

    try:
        pub_id = postData.get("pub_id")
    except:
        logger.error("Could not get pub id")

        modal_to_display = "warning"
        warning_text = "Could not get pub ID in request."

        return modal_to_display, warning_text

    if not pub_id.isnumeric():
        logger.error("Pub id is not a number %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text
        
    if userProfile.user.is_staff:
        logger.debug("UserProfile is a staff member so price verification is allowed")
    else:
        logger.debug("UserProfile is not a staff member. Not deleting object")

        modal_to_display = "warning"
        warning_text = "This operation is only permitted for staff members."
        return modal_to_display, warning_text

    last_verified_guinness = pub.getLastVerifiedGuinness()

    logger.debug("Creating new guinness object")

    # Create new Guinness object
    guinness = Guinness()

    guinness.creator = userProfile
    guinness.price   = last_verified_guinness['price']
    guinness.pub     = pub

    try:
        guinness.full_clean()
    except:
        logger.error("Guinness object data could not be validated")

        warning_text = "Failed to verify."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        guinness.save()
    except:
        logger.error("Guinness object could not be saved")

        warning_text = "Failed to verify."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    return modal_to_display, warning_text


def handleClosePubRequest(userProfile, postData):

    logger.info("Received close Pub request - %s", postData)

    modal_to_display = ""
    warning_text     = ""

    try:
        pub_id = postData.get("pub_id")
    except:
        logger.error("Could not get pub id")

        modal_to_display = "warning"
        warning_text = "Could not get pub ID in request."

        return modal_to_display, warning_text

    if not pub_id.isnumeric():
        logger.error("Pub id is not a number %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    if userProfile.user.is_staff:
        logger.debug("UserProfile is a staff member so closing pub is allowed")
    else:
        logger.debug("UserProfile is not a staff member. Not closing pub")

        modal_to_display = "warning"
        warning_text = "This operation is only permitted for staff members."
        return modal_to_display, warning_text

    pub.closed = True
    pub.save()

    return modal_to_display, warning_text

def handleNotServingGuinnessRequest(userProfile, postData):

    logger.info("Received not serving Guinness request - %s", postData)

    modal_to_display = ""
    warning_text     = ""

    try:
        pub_id = postData.get("pub_id")
    except:
        logger.error("Could not get pub id")

        modal_to_display = "warning"
        warning_text = "Could not get pub ID in request."

        return modal_to_display, warning_text

    if not pub_id.isnumeric():
        logger.error("Pub id is not a number %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text
        
    if userProfile.user.is_staff:
        logger.debug("UserProfile is a staff member so marking pub as not serving Guinness is allowed")
    else:
        logger.debug("UserProfile is not a staff member. Not marking pub as not serving Guinness")

        modal_to_display = "warning"
        warning_text = "This operation is only permitted for staff members."
        return modal_to_display, warning_text

    pub.servingGuinness = False
    pub.save()

    return modal_to_display, warning_text


@login_required
def guindexAlertSettings(request):

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    try:
        user_profile = GuindexUtils.getUserProfileFromUser(request.user)
        logger.debug("Found UserProfile %s with user '%s'", user_profile, request.user)
    except:
        logger.error("Could not retrieve UserProfile with user '%s'. Raising 404 exception", request.user)

        error_message = "No UserProfile exists with user '%s'" % request.user

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict)

    if request.method == "POST" and request.is_ajax():

        try:
            using_email = json.loads(request.body)['usingEmail']
        except:
            logger.error("Failed to load email setting")
            raise Http404("Failed to load email setting")

        try:
            using_telegram = json.loads(request.body)['usingTelegram']
        except:
            logger.error("Failed to load telegram setting")
            raise Http404("Failed to load telegram setting")

        logger.debug("Apllying settings email: %s, telegram: %s", using_email, using_telegram)

        user_profile.usingEmailAlerts = using_email

        try:
            user_profile.save()
        except:
            logger.error("Failed to save updated UserProfile")
            raise Http404("Failed to save updated UserProfile")

        user_profile.telegramuser.usingTelegramAlerts = using_telegram

        if not user_profile.telegramuser.activated and using_telegram:
            logger.error("Telegram account has not yet been activated. Can't set this alert option")
            raise Http404("Telegram account has not been activated yet")

        try:
            user_profile.telegramuser.save()
        except:
            logger.error("Failed to save updated TelegramUser")
            raise Http404("Failed to save updated TelegramUser")

        return HttpResponse(json.dumps({}), content_type="application/json")

    else:
        logger.error("Received invalid request type")

        return render(request, 'error_404.html', {'user_profile_parameters': UserProfileParameters.getParameters()})


class PubList(generics.ListAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received PubList request")

        # Access base class constructor
        super(PubList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Pub.objects.all()


class PubDetail(generics.RetrieveAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received PubDetail request")

        # Access base class constructor
        super(PubDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Pub.objects.all()


class GuinnessList(generics.ListAPIView):

    serializer_class   = GuinnessSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received GuinnessList request")

        # Access base class constructor
        super(GuinnessList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Guinness.objects.all()


class GuinnessDetail(generics.RetrieveAPIView):

    serializer_class   = GuinnessSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received GuinnesDetail request")

        # Access base class constructor
        super(GuinnessDetail, self).__init__(*args, **kwargs)

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
