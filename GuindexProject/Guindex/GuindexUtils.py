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

    userProfile.guindexuser = GuindexUser()
    userProfile.guindexuser.save()
    userProfile.save()

    logger.info("Successfully created new GuindexUser %s for UserProfile %s", guindex_user, userProfile)
