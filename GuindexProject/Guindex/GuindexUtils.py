# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import GuindexUser

from TelegramUser import TelegramUserUtils

logger = logging.getLogger(__name__)


def getUser(user):
    """
        Does some checks on request User object and makes
        sure corresponding GuindexUser and TelegramUser objects 
        are instantiated.
    """

    if user.is_anonymous: 
        # Let permission classes decide what to do after this 
        logger.debug("User is anonymous")

        return user

    # Create TelegramUser if not defined already
    if not hasattr(user, 'telegramuser'):

        logger.info("User %s does not have a TelegramUser. Creating one", user)

        # TelegramUserUtils.createNewTelegramUser(user)

    else:
        logger.debug("User %s has a TelegramUser %s. No need to create one", user, user.telegramuser)

    if not hasattr(user, 'guindexuser'):

        logger.info("User %s does not have a GuindexUser. Creating one", user)
        createNewGuindexUser(user)

    else:
        logger.debug("User %s has a GuindexUser %s. No need to create one", user, user.guindexuser)

    return user


def createNewGuindexUser(user):

    logger.info("Creating new GuindexUser for User %s", user)

    guindexuser = GuindexUser()
    guindexuser.user = user
    guindexuser.save()

    logger.info("Successfully created new GuindexUser %s for User %s", guindexuser, user)
