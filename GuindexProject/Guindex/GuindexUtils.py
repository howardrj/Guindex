# -*- coding: utf-8 -*-
import logging
import math
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub, Guinness, StatisticsSingleton, UserContributionsSingleton

from UserProfile.models import UserProfile

from TelegramUser import TelegramUserUtils
from GuindexUser import GuindexUserUtils


logger = logging.getLogger(__name__)


def getUserProfileFromUser(user):

    logger.debug("Attempting to find UserProfile with user %s", user)

    # Get UserProfile from user
    try:
        user_profile = UserProfile.objects.get(user = user)
    except ObjectDoesNotExist:
        logger.error("Could not find UserProfile with user %s", user)
        raise

    # Create TelegramUser if not defined already
    if not user_profile.telegramuser:

        logger.info("UserProfile %s does not have a TelegramUser. Creating one", user_profile)

        TelegramUserUtils.createNewTelegramUser(user_profile)

    else:
        logger.debug("UserProfile %s has a TelegramUser %s. No need to create one", user_profile, user_profile.telegramuser)

    if not user_profile.guindexuser:

        logger.info("UserProfile %s does not have a GuindexUser. Creating one", user_profile)
        GuindexUserUtils.createNewGuindexUser(user_profile)

    else:
        logger.debug("UserProfile %s has a GuindexUser %s. No need to create one", user_profile, user_profile.guindexuser)

    return user_profile


def getPubs():
    """
        Returns list of all Pub objects
        sorted alphabetically.
    """

    pub_list = []

    pubs = Pub.objects.filter(pendingApproval = False)

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
    pending_prices = Guinness.objects.filter(approved = False)

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
    pending_pubs = Pub.objects.filter(pendingApproval = True)

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

    if len(Guinness.objects.filter(approved = False)):

        return True

    if len(Pub.objects.filter(pendingApproval = True)):

        return True

    if len(Pub.objects.filter(pendingClosed = True)):

        return True

    if len(Pub.objects.filter(pendingNotServingGuinness = True)):

        return True

    return False


def getStats():

    logger.debug("Retrieving stats")

    stats_singleton = StatisticsSingleton.load()

    stats_list = []

    stats_dict = {}

    stats_dict['title'] = 'Number of Pubs in Database'
    stats_dict['value'] = stats_singleton.pubsInDb

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Percentage Visited'
    stats_dict['value'] = '%.2f%%' % stats_singleton.percentageVisited

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Average Price'
    stats_dict['value'] = u'€%.2f' % stats_singleton.averagePrice

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Standard Deviation'
    stats_dict['value'] = '%.3f' % stats_singleton.standardDevation

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Cheapest Pint'
    if not stats_singleton.cheapestPub:
        stats_dict['value'] = 'TBD'
    else:
        stats_dict['value'] = u'€%s' % (stats_singleton.cheapestPub)

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Dearest Pint'
    if not stats_singleton.dearestPub:
        stats_dict['value'] = 'TBD'
    else:
        stats_dict['value'] = u'€%s' % (stats_singleton.dearestPub)

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Closed Pubs'
    stats_dict['value'] = stats_singleton.closedPubs

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Not Serving Guinness'
    stats_dict['value'] = stats_singleton.notServingGuinness

    stats_list.append(stats_dict.copy())

    stats_dict['title'] = 'Last Calculated'
    stats_dict['value'] = stats_singleton.lastCalculated

    stats_list.append(stats_dict.copy())

    logger.debug("Returning stats list - %s", stats_list)

    return stats_list


def getPersonalContributions(userProfile):

    logger.debug("Retrieving personal contributions")

    contribution_list = []

    contribution_dict = {}

    contribution_dict['title'] = 'Pubs Visited'
    contribution_dict['value'] = userProfile.guindexuser.pubsVisited

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Original Prices'
    contribution_dict['value'] = userProfile.guindexuser.originalPrices

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Current Verifications'
    contribution_dict['value'] = userProfile.guindexuser.currentVerifications

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Last Calculated'
    contribution_dict['value'] = userProfile.guindexuser.lastCalculated

    contribution_list.append(contribution_dict.copy())

    logger.debug("Returning contributions list - %s", contribution_list)

    return contribution_list


def getBestContributions():

    logger.debug("Retrieving best user contributions")

    user_contribution_singleton = UserContributionsSingleton.load()

    contribution_list = []

    contribution_dict = {}

    contribution_dict['title'] = 'Most Pubs Visited'
    if user_contribution_singleton.mostVisited:
        contribution_dict['value'] = "%s (%d)" % (user_contribution_singleton.mostVisited.user.username,
                                                  user_contribution_singleton.mostVisited.guindexuser.pubsVisited)
    else:
        contribution_dict['value'] = 'NA'

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Most Original Prices'
    if user_contribution_singleton.mostFirstVerified:
        contribution_dict['value'] = "%s (%d)" % (user_contribution_singleton.mostFirstVerified.user.username,
                                                  user_contribution_singleton.mostFirstVerified.guindexuser.originalPrices)
    else:
        contribution_dict['value'] = 'NA'

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Most Current Verifications'
    if user_contribution_singleton.mostLastVerified:
        contribution_dict['value'] = "%s (%d)" % (user_contribution_singleton.mostLastVerified.user.username,
                                                  user_contribution_singleton.mostLastVerified.guindexuser.currentVerifications)
    else:
        contribution_dict['value'] = 'NA'

    contribution_list.append(contribution_dict.copy())

    contribution_dict['title'] = 'Last Calculated'
    contribution_dict['value'] = user_contribution_singleton.lastCalculated

    contribution_list.append(contribution_dict.copy())

    logger.debug("Returning best contributions list - %s", contribution_list)

    return contribution_list


def calculateNumberOfPubs(statsSingleton):

    statsSingleton.pubsInDb = len(Pub.objects.all())


def calculateCheapestPub(statsSingleton):

    cheapest_pub = None

    for pub_index, pub in enumerate(Pub.objects.all()):

        if pub_index == 0:
            cheapest_pub = pub

        if not pub.getLastVerifiedGuinness():
            continue
        elif pub.getLastVerifiedGuinness()['price'] < cheapest_pub.getLastVerifiedGuinness()['price']:
            cheapest_pub = pub

    statsSingleton.cheapestPub = '%.2f (%s)' % (cheapest_pub.getLastVerifiedGuinness()['price'], cheapest_pub.name)


def calculateDearestPub(statsSingleton):

    dearest_pub = None

    for pub_index, pub in enumerate(Pub.objects.all()):

        if pub_index == 0:
            dearest_pub = pub

        if not pub.getLastVerifiedGuinness():
            continue
        elif pub.getLastVerifiedGuinness()['price'] > dearest_pub.getLastVerifiedGuinness()['price']:
            dearest_pub = pub

    statsSingleton.dearestPub = '%.2f (%s)' % (dearest_pub.getLastVerifiedGuinness()['price'], dearest_pub.name)


def calculateAveragePrice(statsSingleton):

    visited_pubs = 0
    sum_total    = 0

    for pub in Pub.objects.all():

        if pub.getLastVerifiedGuinness():
            visited_pubs = visited_pubs + 1
            sum_total    = sum_total + pub.getLastVerifiedGuinness()['price']

    if visited_pubs == 0:
        statsSingleton.averagePrice = 0
        return

    statsSingleton.averagePrice = Decimal(sum_total / visited_pubs)


def calculateStandardDeviation(statsSingleton):

    variance_tmp = 0
    visited_pubs = 0

    if statsSingleton.averagePrice == 0:
        statsSingleton.standardDevation = 0
        return

    for pub in Pub.objects.all():

        if pub.getLastVerifiedGuinness():
            visited_pubs = visited_pubs + 1
            variance_tmp = variance_tmp + math.pow((pub.getLastVerifiedGuinness()['price'] - statsSingleton.averagePrice), 2)

    variance = Decimal(variance_tmp) / visited_pubs

    statsSingleton.standardDevation = variance.sqrt()


def calculatePercentageVisited(statsSingleton):

    visited_pubs = 0

    if statsSingleton.pubsInDb == 0:
        statsSingleton.percentageVisited = 0
        return

    for pub in Pub.objects.all():

        if pub.getLastVerifiedGuinness() or not pub.servingGuinness:
            visited_pubs = visited_pubs + 1

    statsSingleton.percentageVisited = (Decimal(visited_pubs) / statsSingleton.pubsInDb) * 100


def calculateClosedPubs(statsSingleton):

    statsSingleton.closedPubs = len(Pub.objects.filter(closed = True))


def calculateNotServingGuinness(statsSingleton):

    statsSingleton.notServingGuinness = len(Pub.objects.filter(servingGuinness = False))


def calculateUserContributions(logger):

    logger.info("Calculating User Contributions")

    most_pubs_visited          = None
    most_first_verifications   = None
    most_current_verifications = None

    for loop_index, user_profile in enumerate(UserProfile.objects.all()):

        logger.debug("Calculating contributions for UserProfile %s", user_profile)

        if not user_profile.guindexuser:
            logger.debug("Need to create GuindexUser for UserProfile %s", user_profile)

            GuindexUserUtils.createNewGuindexUser(user_profile)

        number_of_current_verifications = 0
        number_of_first_verifications   = 0
        number_of_pubs_visited          = 0

        for pub in Pub.objects.all():

            if pub.getLastVerifiedGuinness():
                if pub.getLastVerifiedGuinness()['creator'] == user_profile.user.username:
                    number_of_current_verifications = number_of_current_verifications + 1

            if pub.getFirstVerifiedGuinness():
                if pub.getFirstVerifiedGuinness()['creator'] == user_profile.user.username:
                    number_of_first_verifications = number_of_first_verifications + 1

            # TODO Test this
            if len(Guinness.objects.filter(pub = pub, creator = user_profile)):
                number_of_pubs_visited = number_of_pubs_visited + 1

        user_profile.guindexuser.originalPrices       = number_of_first_verifications
        user_profile.guindexuser.currentVerifications = number_of_current_verifications
        user_profile.guindexuser.pubsVisited          = number_of_pubs_visited

        user_profile.guindexuser.save()
        user_profile.save() # Pedantic

        if loop_index == 0:
            most_first_verifications   = user_profile
            most_current_verifications = user_profile
            most_pubs_visited          = user_profile

        elif user_profile.guindexuser.originalPrices > most_first_verifications.guindexuser.originalPrices:
            most_first_verifications = user_profile
        elif user_profile.guindexuser.currentVerifications > most_current_verifications.guindexuser.currentVerifications:
            most_current_verifications = user_profile
        elif user_profile.guindexuser.pubsVisited > most_first_verifications.guindexuser.pubsVisited:
            most_pubs_visited = user_profile

    user_contributions_singleton = UserContributionsSingleton.load()

    user_contributions_singleton.mostVisited       = most_pubs_visited
    user_contributions_singleton.mostLastVerified  = most_current_verifications
    user_contributions_singleton.mostFirstVerified = most_first_verifications

    logger.info("Saving User Contributions Singleton %s", user_contributions_singleton)

    user_contributions_singleton.save()
