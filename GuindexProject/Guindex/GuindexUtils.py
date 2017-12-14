import logging

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub

from UserProfile.models import UserProfile

from TelegramUser import TelegramUserUtils

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

    return user_profile


def getPubs():
    """
        Returns list of all Pub objects
        sorted alphabetically.
    """

    pub_list = []

    pubs = Pub.objects.all()

    for pub in pubs:

        pub_dict = {}

        pub_dict['id']           = str(pub.id)
        pub_dict['creator']      = pub.creator.user.username
        pub_dict['creationDate'] = pub.creationDate
        pub_dict['name']         = pub.name
        pub_dict['guini']        = pub.getGuini()

        if len(pub_dict['guini']): # TODO Fix this. Just take first Gunness object for now
            pub_dict['guini'] = pub_dict['guini'][0:1]

        pub_list.append(pub_dict.copy())

    return sorted(pub_list, key = lambda k: k['name'], reverse = False)
