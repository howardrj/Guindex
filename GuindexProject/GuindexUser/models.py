# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from UserProfile.UserProfilePlugin import UserProfilePlugin


class GuindexUser(UserProfilePlugin):
    """
        Class to keep track of settings and user contributions.
    """

    pubsVisited          = models.IntegerField(default = True)
    originalPrices       = models.IntegerField(default = True)
    currentVerifications = models.IntegerField(default = True)
