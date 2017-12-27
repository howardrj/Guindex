# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub, StatisticsSingleton

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

    pubs = Pub.objects.all()

    for pub in pubs:

        if not pub.closed and pub.servingGuinness:
            pub_dict = {}

            pub_dict['id']             = str(pub.id)
            pub_dict['name']           = pub.name
            pub_dict['first_guinness'] = pub.getFirstVerifiedGuinness()
            pub_dict['last_guinness']  = pub.getLastVerifiedGuinness()
            pub_dict['map_link']       = pub.mapLink

            pub_list.append(pub_dict.copy())

    return sorted(pub_list, key = lambda k: k['name'], reverse = False)


def getStats():

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

    stats_dict['title'] = 'Cheapest Pint'
    if not stats_singleton.cheapestPub:
        stats_dict['value'] = 'TBD'
    else:
        stats_dict['value'] = u'€%.2f (%s)' % (stats_singleton.cheapestPub.getLastVerifiedGuinness()['price'], stats_singleton.cheapestPub.name)

    stats_list.append(stats_dict.copy())
    
    stats_dict['title'] = 'Dearest Pint'
    if not stats_singleton.dearestPub:
        stats_dict['value'] = 'TBD'
    else:
        stats_dict['value'] = u'€%.2f (%s)' % (stats_singleton.dearestPub.getLastVerifiedGuinness()['price'], stats_singleton.dearestPub.name)

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

    return stats_list

