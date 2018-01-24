import logging
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework import generics
from rest_framework import permissions

from Guindex.forms import NewPubForm, NewGuinnessForm
from Guindex.serializers import PubSerializer, GuinnessSerializer, StatisticsSerializer
from Guindex.models import Pub, Guinness, StatisticsSingleton
from GuindexParameters import GuindexParameters
from GuindexAlertsClient import GuindexAlertsClient
import GuindexUtils

from UserProfile.UserProfileParameters import UserProfileParameters

logger = logging.getLogger(__name__)


def guindexMapFull(request):

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    return render(request, 'guindex_map_full.html')


@login_required
@require_http_methods(['GET', 'POST'])
def guindex(request):

    logger.info("Received %s request to %s", request.method, request.get_full_path())

    new_pub_form      = NewPubForm()
    new_guinness_form = NewGuinnessForm()

    modal_to_display = ""
    warning_text     = ""

    try:
        user_profile = GuindexUtils.getUserProfileFromUser(request.user)
        logger.debug("Found UserProfile %s with user '%s'", user_profile, request.user)
    except:
        logger.error("Could not retrieve UserProfile with user '%s'. Raising 404 exception", request.user)

        error_message = "No UserProfile exists with user '%s'" % request.user

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters(),
                        'message'                : error_message}

        return render(request, 'error_404.html', context_dict, status = 404)

    if request.method == 'POST':

        if 'new_pub' in request.POST:

            modal_to_display, new_pub_form, warning_text = handleNewPubRequest(user_profile, request.POST)

        elif 'new_guinness' in request.POST:

            modal_to_display, new_guinness_form, warning_text = handleNewGuinnessRequest(user_profile, request.POST)

        elif 'verify_guinness' in request.POST:

            modal_to_display, warning_text = handleVerifyGuinnessRequest(user_profile, request.POST)

        elif 'close_pub' in request.POST:

            modal_to_display, warning_text = handleClosePubRequest(user_profile, request.POST)

        elif 'not_serving_guinness' in request.POST:

            modal_to_display, warning_text = handleNotServingGuinnessRequest(user_profile, request.POST)

        else:
            logger.error("Received POST request to unknown resource")

            context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

            return render(request, 'error_404.html', context_dict, status = 404)

        if not modal_to_display:

            logger.info("Successful POST")

            return HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

        elif modal_to_display == 'warning':

            logger.info("POST comes with warning")

            response = HttpResponseRedirect(UserProfileParameters.LOGIN_SUCCESS_REDIRECT_URL)

            response.set_cookie('modal_to_display', 'warning')
            response.set_cookie('warning_text', warning_text)

            return response

        else:
            logger.info("Returning form %s with errors to correct", modal_to_display)

    # Retrieve cookies that may or may not be set
    if not modal_to_display:
        modal_to_display = request.COOKIES.get('modal_to_display', "")
        warning_text     = request.COOKIES.get('warning_text', "")

    context_dict = {'pubs'                   : GuindexUtils.getPubs(),
                    'stats'                  : GuindexUtils.getStats(),
                    'personal_contributions' : GuindexUtils.getPersonalContributions(user_profile),
                    'pending_contributions'  : GuindexUtils.arePendingContributions(),
                    'best_contributions'     : GuindexUtils.getBestContributions(),
                    'modal_to_display'       : modal_to_display,
                    'warning_text'           : warning_text,
                    'new_pub_form'           : new_pub_form,
                    'new_guinness_form'      : new_guinness_form,
                    'user_profile'           : user_profile,
                    'user_profile_parameters': UserProfileParameters.getParameters(),
                    'guindex_parameters'     : GuindexParameters.getParameters(),
                    'google_maps_api_token'  : settings.GOOGLE_MAPS_API_KEY,
                    }

    response = render(request, 'guindex_main.html', context_dict)

    # Delete cookies if they exist
    response.delete_cookie('modal_to_display')
    response.delete_cookie('warning_text')

    return response


def handleNewPubRequest(userProfile, postData):

    logger.info("Received new pub request - %s", postData)

    modal_to_display = "new_pub_form"
    new_pub_form     = NewPubForm(userProfile = userProfile, data = postData)
    warning_text     = ""

    if new_pub_form.is_valid():

        logger.info("UserProfile %s: New pub form data was valid. Creating new pub", userProfile)

        try:
            new_pub = new_pub_form.save()
            modal_to_display = ""
        except:
            logger.error("Failed to save form")
            modal_to_display = "warning"
            warning_text = "Failed to save new Pub object."
            return modal_to_display, new_pub_form, warning_text

    else:
        logger.error("UserProfile %s: New pub form data was invalid", userProfile)
        return modal_to_display, new_pub_form, warning_text

    # Pub object has been saved at this point

    if not userProfile.user.is_staff:

        logger.info("Contribution was made by non-staff member")

        # Set relevant return variables
        modal_to_display  = "warning"
        warning_text      = "Thank you for your contribution. A staff member will verify your submission shortly."

    else:
        logger.info("Contribution was made by staff member")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return modal_to_display, new_pub_form, warning_text

    try:
        alerts_client.sendNewPubAlertRequest(new_pub)
    except:
        logger.error("Failed to send New Pub Alert Request")
        return modal_to_display, new_pub_form, warning_text

    return modal_to_display, new_pub_form, warning_text


def handleNewGuinnessRequest(userProfile, postData):

    logger.info("Received new Guinness request - %s", postData)

    modal_to_display  = "new_guinness_form"
    new_guinness_form = NewGuinnessForm(userProfile = userProfile, data = postData)
    warning_text      = ""

    if new_guinness_form.is_valid():

        logger.info("UserProfile %s: New Guinness form data was valid. Creating new Guinness", userProfile)

        try:
            new_guinness = new_guinness_form.save()
            modal_to_display = ""
        except:
            logger.error("Failed to save form")
            modal_to_display = "warning"
            warning_text = "Failed to save new Guinness object"
            return modal_to_display, new_guinness_form, warning_text

    else:
        logger.error("UserProfile %s: New Guinness form data was invalid", userProfile)
        return modal_to_display, new_guinness_form, warning_text

    # Guinness object has been saved at this point

    if not userProfile.user.is_staff:

        logger.info("Contribution was made by non-staff member")

        # Set relevant return variables
        modal_to_display  = "warning"
        warning_text      = "Thank you for your contribution. A staff member will verify your submission shortly."

    else:
        logger.info("Contribution was made by staff member")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return modal_to_display, new_guinness_form, warning_text

    try:
        alerts_client.sendNewGuinnessAlertRequest(new_guinness)
    except:
        logger.error("Failed to send New Guinness Alert Request")
        return modal_to_display, new_guinness_form, warning_text

    return modal_to_display, new_guinness_form, warning_text


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

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    last_verified_guinness = pub.getLastVerifiedGuinness()

    logger.debug("Creating new Guinness object")

    # Create new Guinness object
    guinness = Guinness()

    guinness.creator  = userProfile
    guinness.price    = last_verified_guinness['price']
    guinness.pub      = pub
    guinness.approved = userProfile.user.is_staff

    try:
        guinness.full_clean()
    except:
        logger.error("Guinness object data could not be validated")

        warning_text = "Failed to validate new Guinness object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        guinness.save()
    except:
        logger.error("Guinness object could not be saved")

        warning_text = "Failed to save new Guinness object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    # Guinness object has been saved at this point

    if not userProfile.user.is_staff:

        logger.info("Contribution was made by non-staff member")

        # Set relevant return variables
        modal_to_display  = "warning"
        warning_text      = "Thank you for your contribution. A staff member will verify your submission shortly."

    else:
        logger.info("Contribution was made by staff member")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return (modal_to_display, warning_text)

    try:
        alerts_client.sendNewGuinnessAlertRequest(guinness)
    except:
        logger.error("Failed to send New Guinness Alert Request")
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

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    if pub.closed:
        logger.error("Pub is already closed")

        modal_to_display = "warning"
        warning_text = "Pub is already closed."

        return modal_to_display, warning_text

    if userProfile.user.is_staff:

        logger.debug("UserProfile is a staff member so closing pub is allowed")
        pub.closed = True

    else:
        logger.debug("UserProfile is not a staff member. Submission will need to be approved")

        if not pub.pendingClosed:
            # Set relevant return variables
            modal_to_display  = "warning"
            warning_text      = "Thank you for your contribution. A staff member will verify your submission shortly."

            pub.pendingClosed = True
        else:
            modal_to_display  = "warning"
            warning_text      = "Another user has already marked this pub as closed."

            return modal_to_display, warning_text

    pub.pendingClosedContributor = userProfile
    pub.pendingClosedTime        = timezone.now()

    try:
        pub.full_clean()
    except:
        warning_text = "Failed to validate new Pub object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        pub.save()
    except:
        warning_text = "Failed to save new Pub object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return modal_to_display, warning_text

    try:
        alerts_client.sendPubClosedAlertRequest(pub)
    except:
        logger.error("Failed to send Pub Closure Alert Request")
        return modal_to_display, warning_text

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

    try:
        pub = Pub.objects.get(id = int(pub_id))
        logger.debug("Found pub %s", pub)
    except ObjectDoesNotExist:
        logger.error("No pub exists with id %s", pub_id)

        modal_to_display = "warning"
        warning_text = "Invalid pub ID."

        return modal_to_display, warning_text

    if not pub.servingGuinness:
        logger.error("Pub is marked as not serving Guinness")

        modal_to_display = "warning"
        warning_text = "Pub is already marked as not serving Guinness."

        return modal_to_display, warning_text

    if userProfile.user.is_staff:

        logger.debug("UserProfile is a staff member so marking pub as not serving Guinness is allowed")
        pub.servingGuinness = False

    else:
        logger.debug("UserProfile is not a staff member. Submission will need to be approved")

        if not pub.pendingNotServingGuinness:
            # Set relevant return variables
            modal_to_display  = "warning"
            warning_text      = "Thank you for your contribution. A staff member will verify your submission shortly."

            pub.pendingNotServingGuinness = True
        else:
            modal_to_display  = "warning"
            warning_text      = "Another user has already marked this pub as not serving Guinness."

            return modal_to_display, warning_text

    pub.pendingNotServingGuinnessContributor = userProfile
    pub.pendingNotServingGuinnessTime        = timezone.now()

    try:
        pub.full_clean()
    except:
        warning_text = "Failed to validate new Pub object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        pub.save()
    except:
        warning_text = "Failed to save new Pub object."
        modal_to_display = "warning"
        return modal_to_display, warning_text

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return modal_to_display, warning_text

    try:
        alerts_client.sendPubNotServingGuinnessAlertRequest(pub)
    except:
        logger.error("Failed to send Pub Not Serving Guinness Alert Request")
        return modal_to_display, warning_text

    return modal_to_display, warning_text


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

    context_dict = {'pending_contributions'  : GuindexUtils.getPendingContributions(),
                    'user_profile'           : user_profile,
                    'user_profile_parameters': UserProfileParameters.getParameters(),
                    'guindex_parameters'     : GuindexParameters.getParameters(),
                    'modal_to_display'       : "",
                    }

    return render(request, 'guindex_pending_contributions.html', context_dict)


@login_required
@require_http_methods(['POST'])
def approveContribution(request):

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

    if request.method != "POST" or not request.is_ajax():

        logger.error("Received invalid request type")

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

        return render(request, 'error_404.html', context_dict, status = 404)

    try:
        contribution_type = json.loads(request.body)['contributionType']
    except:
        logger.error("Failed to load contribution type")
        raise Http404("Failed to load contribution type")

    try:
        contribution_id = json.loads(request.body)['contributionId']
    except:
        logger.error("Failed to load contribution ID")
        raise Http404("Failed to load contribution ID")

    try:
        contribution_method = json.loads(request.body)['contributionMethod']
    except:
        logger.error("Failed to load contribution method")
        raise Http404("Failed to load contribution method")

    if contribution_method == 'approve':
        logger.debug("Contribution was approved")
        contribution_approved = True
        reason = None
    elif contribution_method == 'reject':
        logger.debug("Contribution was rejected")
        contribution_approved = False

        # Try get reason for rejection
        try:
            reason = json.loads(request.body)['contributionReason']
            logger.debug("Rejection reason - %s", reason)
        except:
            logger.debug("Reason for rejecton was not provided in request")
            reason = None

    else:
        logger.error("Received invalid contributionMethod: %s", contribution_method)
        raise Http404("Received invalid contributionMethod: %s" % contribution_method)
        
    if contribution_type == 'pending_price':

        logger.info("Received pending price decision")

        return handleNewPriceDecision(contribution_id, contribution_approved, reason)

    if contribution_type == 'pending_pub':

        logger.info("Received pending new pub decision")

        return handleNewPubDecision(contribution_id, contribution_approved, reason)

    if contribution_type == 'pending_closure':

        logger.info("Received pending pub closure decision")

        return handlePubClosureDecision(contribution_id, contribution_approved, reason)

    if contribution_type == 'pending_not_serving_guinness':

        logger.info("Received pending pub not serving Guinness decision")

        return handlePubNotServingGuinnessDecision(contribution_id, contribution_approved, reason)

    logger.error("Received invalid contribution type")

    raise Http404("Received invalid contribution type")

@login_required
@require_http_methods(['GET'])
def arePendingContributions(request):

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

    if request.method != "GET":

        logger.error("Received invalid request type")

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

        return render(request, 'error_404.html', context_dict, status = 404)

    are_pending_contributions = GuindexUtils.arePendingContributions()

    if are_pending_contributions:
        logger.debug("There are pending contributions")
    else:
        logger.error("There are no pending contributons")
    
    response = {'arePendingContributions': are_pending_contributions}

    return HttpResponse(json.dumps(response), content_type="application/json") # Send 200 OK anyway


def handleNewPriceDecision(contributionId, contributionApproved, reason = None):

    try:
        guinness = Guinness.objects.get(id = int(contributionId))
    except:
        logger.error("Failed to Guinness with ID %s", contributionId)
        raise Http404("Invalid contribution ID")

    if guinness.approved:

        logger.error("Guinness %s has already been approved", guinness)
        return HttpResponse(json.dumps({}), content_type="application/json") # Send 200 OK anyway

    if contributionApproved:
        guinness.approved = True
        guinness.rejected = False
    else:
        guinness.approved = False
        guinness.rejected = True 

    try:
        guinness.full_clean()
    except:
        logger.error("Guinness object data could not be validated")
        raise Http404("Failed to validate Guinness object")

    try:
        guinness.save()
    except:
        logger.error("Guinness object could not be saved")
        raise Http404("Failed to save Guinness object")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        alerts_client.sendNewGuinnessDecisionAlertRequest(guinness, reason)
    except:
        logger.error("Failed to send New Guinness Decision Alert Request")
        return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(json.dumps({}), content_type="application/json")


def handleNewPubDecision(contributionId, contributionApproved, reason = None):

    try:
        pub = Pub.objects.get(id = int(contributionId))
    except:
        logger.error("Failed to Pub with ID %s", contributionId)
        raise Http404("Invalid contribution ID")

    if not pub.pendingApproval:

        logger.error("Pub %s is not pending approval", pub)
        return HttpResponse(json.dumps({}), content_type="application/json") # Send 200 OK anyway

    if contributionApproved:
        pub.pendingApproval = False
        pub.pendingApprovalRejected = False
    else:
        pub.pendingApproval = False
        pub.pendingApprovalRejected = True

    try:
        pub.full_clean()
    except:
        logger.error("Pub object data could not be validated")
        raise Http404("Failed to validate Guinness object")

    try:
        pub.save()
    except:
        logger.error("Pub object could not be saved")
        raise Http404("Failed to save Guinness object")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        alerts_client.sendNewPubDecisionAlertRequest(pub, reason)
    except:
        logger.error("Failed to send New Pub Decision Alert Request")
        return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(json.dumps({}), content_type="application/json")


def handlePubClosureDecision(contributionId, contributionApproved, reason = None):

    try:
        pub = Pub.objects.get(id = int(contributionId))
    except:
        logger.error("Failed to Pub with ID %s", contributionId)
        raise Http404("Invalid contribution ID")

    if not pub.pendingClosed:

        logger.error("Pub %s is not pending closure", pub)
        return HttpResponse(json.dumps({}), content_type="application/json") # Send 200 OK anyway

    if contributionApproved:
        pub.pendingClosed = False
        pub.closed = True
    else:
        pub.pendingClosed = False
        pub.closed = False

    try:
        pub.full_clean()
    except:
        logger.error("Pub object data could not be validated")
        raise Http404("Failed to validate Guinness object")

    try:
        pub.save()
    except:
        logger.error("Pub object could not be saved")
        raise Http404("Failed to save Guinness object")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        alerts_client.sendPubClosedDecisionAlertRequest(pub, reason)
    except:
        logger.error("Failed to send Pub Closed Decision Alert Request")
        return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(json.dumps({}), content_type="application/json")


def handlePubNotServingGuinnessDecision(contributionId, contributionApproved, reason = None):

    try:
        pub = Pub.objects.get(id = int(contributionId))
    except:
        logger.error("Failed to Pub with ID %s", contributionId)
        raise Http404("Invalid contribution ID")

    if not pub.pendingNotServingGuinness:

        logger.error("Pub %s is not pending not serving Guinness", pub)
        return HttpResponse(json.dumps({}), content_type="application/json") # Send 200 OK anyway

    if contributionApproved:
        pub.pendingNotServingGuinness = False
        pub.servingGuinness = False
    else:
        pub.pendingNotServingGuinness = False
        pub.servingGuinness = True

    try:
        pub.full_clean()
    except:
        logger.error("Pub object data could not be validated")
        raise Http404("Failed to validate Guinness object")

    try:
        pub.save()
    except:
        logger.error("Pub object could not be saved")
        raise Http404("Failed to save Guinness object")

    try:
        alerts_client = GuindexAlertsClient(logger)
    except:
        logger.error("Failed to create Alerts Client")
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        alerts_client.sendPubNotServingGuinnessDecisionAlertRequest(pub, reason)
    except:
        logger.error("Failed to send Pub Not Serving Guinness Decision Alert Request")
        return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(json.dumps({}), content_type="application/json")


@login_required
@require_http_methods(['POST'])
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

        return render(request, 'error_404.html', context_dict, status = 404)

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

        logger.debug("Applying settings email: %s, telegram: %s", using_email, using_telegram)

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

        context_dict = {'user_profile_parameters': UserProfileParameters.getParameters()}

        return render(request, 'error_404.html', context_dict, status = 404)


class PubList(generics.ListAPIView):

    serializer_class   = PubSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received PubList request")

        # Access base class constructor
        super(PubList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Pub.objects.filter(pendingApproval = False, pendingApprovalRejected = False)


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
        return Guinness.objects.filter(approved = True)


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
