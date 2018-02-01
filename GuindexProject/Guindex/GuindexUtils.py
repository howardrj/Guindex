# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub, Guinness

from UserProfile.models import UserProfile

from TelegramUser import TelegramUserUtils

from GuindexUser.models import GuindexUser


logger = logging.getLogger(__name__)


def getUserProfileFromUser(user):

    logger.debug("Attempting to find UserProfile with user %s", user)

    # Get UserProfile from user
    try:
        user_profile = UserProfile.objects.get(user = user)
    except ObjectDoesNotExist:
        logger.error("Could not find UserProfile with user %s", user)
        raise Exception("Could not find UserProfile with user %s" % user)

    # Create TelegramUser if not defined already
    if not user_profile.telegramuser:

        logger.info("UserProfile %s does not have a TelegramUser. Creating one", user_profile)

        TelegramUserUtils.createNewTelegramUser(user_profile)

    else:
        logger.debug("UserProfile %s has a TelegramUser %s. No need to create one", user_profile, user_profile.telegramuser)

    if not user_profile.guindexuser:

        logger.info("UserProfile %s does not have a GuindexUser. Creating one", user_profile)
        createNewGuindexUser(user_profile)

    else:
        logger.debug("UserProfile %s has a GuindexUser %s. No need to create one", user_profile, user_profile.guindexuser)

    return user_profile


def createNewGuindexUser(userProfile):

    logger.info("Creating new GuindexUser for UserProfile %s", userProfile)

    guindex_user = GuindexUser()

    guindex_user.save()

    userProfile.guindexuser = guindex_user
    userProfile.save()

    logger.info("Successfully created new GuindexUser %s for UserProfile %s", guindex_user, userProfile)


def getPubs():
    """
        Returns list of all Pub objects
        sorted alphabetically.
    """

    pub_list = []

    pubs = Pub.objects.filter(pendingApproval = False, pendingApprovalRejected = False)

    for pub in pubs:

        pub_dict = {}

        pub_dict['id']               = str(pub.id)
        pub_dict['name']             = pub.name
        pub_dict['first_guinness']   = pub.getFirstVerifiedGuinness()
        pub_dict['last_guinness']    = pub.getLastVerifiedGuinness()
        pub_dict['map_link']         = pub.mapLink
        pub_dict['closed']           = pub.closed
        pub_dict['serving_guinness'] = pub.servingGuinness

        pub_list.append(pub_dict.copy())

    return sorted(pub_list, key = lambda k: k['name'].lower(), reverse = False)


def getPendingContributions():

    pending_contributions_dict = {}

    # Check pending prices
    pending_prices = Guinness.objects.filter(approved = False, rejected = False)

    pending_prices_list = []

    for guin in pending_prices:

        pending_price_dict = {}

        pending_price_dict['id']           = str(guin.id)
        pending_price_dict['pub']          = guin.pub.name
        pending_price_dict['contributor']  = guin.creator.user.username
        pending_price_dict['creationDate'] = guin.creationDate
        pending_price_dict['price']        = guin.price

        pending_prices_list.append(pending_price_dict)

    pending_contributions_dict['pending_prices'] = sorted(pending_prices_list, key = lambda k: k['creationDate'], reverse = False)

    # Checking pending new pubs
    pending_pubs = Pub.objects.filter(pendingApproval = True, pendingApprovalRejected = False)

    pending_pubs_list = []

    for pub in pending_pubs:

        pending_pub_dict = {}

        pending_pub_dict['id']           = str(pub.id)
        pending_pub_dict['pub']          = pub.name
        pending_pub_dict['contributor']  = pub.pendingApprovalContributor.user.username
        pending_pub_dict['creationDate'] = pub.pendingApprovalTime
        pending_pub_dict['mapLink']      = pub.mapLink

        pending_pubs_list.append(pending_pub_dict)

    pending_contributions_dict['pending_pubs'] = sorted(pending_pubs_list, key = lambda k: k['creationDate'], reverse = False)

    # Check pending closures
    pending_closures = Pub.objects.filter(pendingClosed = True)

    pending_closures_list = []

    for pub in pending_closures:

        pending_closure_dict = {}

        pending_closure_dict['id']           = str(pub.id)
        pending_closure_dict['pub']          = pub.name
        pending_closure_dict['contributor']  = pub.pendingClosedContributor.user.username
        pending_closure_dict['creationDate'] = pub.pendingClosedTime
        pending_closure_dict['mapLink']      = pub.mapLink

        pending_closures_list.append(pending_closure_dict)

    pending_contributions_dict['pending_closures'] = sorted(pending_closures_list, key = lambda k: k['creationDate'], reverse = False)

    # Check pending not serving Guinness
    pending_not_serving = Pub.objects.filter(pendingNotServingGuinness = True)

    pending_not_serving_list = []

    for pub in pending_not_serving:

        pending_not_serving_dict = {}

        pending_not_serving_dict['id']           = str(pub.id)
        pending_not_serving_dict['pub']          = pub.name
        pending_not_serving_dict['contributor']  = pub.pendingNotServingGuinnessContributor.user.username
        pending_not_serving_dict['creationDate'] = pub.pendingNotServingGuinnessTime
        pending_not_serving_dict['mapLink']      = pub.mapLink

        pending_not_serving_list.append(pending_not_serving_dict)

    pending_contributions_dict['pending_not_serving_guinness'] = sorted(pending_not_serving_list, key = lambda k: k['creationDate'], reverse = False)

    return pending_contributions_dict


def arePendingContributions():
    """
        Return boolean signalling if there are pending contributions.
        Means we don't have to return full list to main Guindex view
    """

    if len(Guinness.objects.filter(approved = False, rejected = False)):

        return True

    if len(Pub.objects.filter(pendingApproval = True)):

        return True

    if len(Pub.objects.filter(pendingClosed = True)):

        return True

    if len(Pub.objects.filter(pendingNotServingGuinness = True)):

        return True

    return False
