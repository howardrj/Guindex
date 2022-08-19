import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from Guindex.models import GuindexUser

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_guindex_user(sender, **kwargs):
    """
        Function used to initialise GuindexUser fields
        for newly created Users.
    """

    user = kwargs.get('instance')

    if not hasattr(user, 'guindexuser'):

        logger.info("User %d does not have a GuindexUser. Creating one", user.id)

        guindexuser = GuindexUser()

        guindexuser.user = user
        guindexuser.save()

@receiver(post_save, sender=User)
def create_access_token(sender, instance=None, created=False, **kwargs):
    """
        Function used to create access token
        for newly created Users.
    """

    if created:
        logger.info("User %d does not have an access token. Creating one", instance.id)

        Token.objects.create(user=instance)
