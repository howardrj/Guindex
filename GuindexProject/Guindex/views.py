import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from Guindex.forms import NewPubForm, NewGuinnessForm, RenamePubForm
from Guindex.models import Pub, Guinness
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

        else:
            logger.error("Received POST request to unknown resource")

            context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

            return render(request, 'error_404.html', context_dict)

    pubs = GuindexUtils.getPubs()

    guindex_parameters      = GuindexParameters.getParameters()
    user_profile_parameters = UserProfileParameters.getParameters()

    context_dict = {'pubs'                   : pubs,
                    'modal_to_display'       : modal_to_display,
                    'warning_text'           : warning_text,
                    'new_pub_form'           : new_pub_form,
                    'rename_pub_form'        : rename_pub_form,
                    'new_guinness_form'      : new_guinness_form,
                    'username'               : user_profile.user.username,
                    'user_profile_parameters': user_profile_parameters,
                    'guindex_parameters'     : guindex_parameters}

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
            warning_text = "Failed to save new Pub object"

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
