from django.db import models

from UserProfile.UserProfilePlugin import UserProfilePlugin


class GuindexUser(UserProfilePlugin):
    """
        Class to keep track of user contributions.
    """

    pubsVisited          = models.IntegerField(default = 0)
    originalPrices       = models.IntegerField(default = 0)
    currentVerifications = models.IntegerField(default = 0)
    lastCalculated       = models.DateTimeField(auto_now = True)
