import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from Guindex.models import GuindexUser

from TelegramUser import TelegramUserUtils

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def newUserInit(sender, **kwargs):
    """
        Function used to initialise TelegramUser and GuindexUser fields
        for newly created Users.
    """

    if kwargs.get('created', False):

        user = kwargs.get('instance')

        logger.info("New User %d was created", user.id)

        if not hasattr(user, 'telegramuser'):

            logger.info("User %d does not have a TelegramUser. Creating one", user.id)

            TelegramUserUtils.createNewTelegramUser(user)

        if not hasattr(user, 'guindexuser'):

            logger.info("User %d does not have a GuindexUser. Creating one", user.id)

            guindexuser = GuindexUser()

            guindexuser.user = user
            guindexuser.save()
