import logging

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub

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
