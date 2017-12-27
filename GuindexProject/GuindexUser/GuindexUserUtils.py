import logging

from GuindexUser.models import GuindexUser

logger = logging.getLogger(__name__)


def createNewGuindexUser(userProfile):

    logger.info("Creating new GuindexUser for UserProfile %s", userProfile)

    guindex_user = GuindexUser()

    guindex_user.save()

    userProfile.guindexuser = guindex_user
    userProfile.save()

    logger.info("Successfully created new GuindexUser %s for UserProfile %s", guindex_user, userProfile)
