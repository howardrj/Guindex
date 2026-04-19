import logging

from django.db import models
from django.contrib.auth.models import User

from TelegramUserParameters import TelegramUserParameters

logger = logging.getLogger(__name__)


class TelegramUser(models.Model):

    user                = models.OneToOneField(User,
                                               null         = True,
                                               blank        = True,
                                               default      = None,
                                               related_name = 'telegramuser')
    activated           = models.BooleanField(default = False)
    activationKey       = models.CharField(max_length = TelegramUserParameters.ACTIVATION_KEY_LENGTH,
                                           default    = "",
                                           unique     = True)
    chatId              = models.CharField(max_length = TelegramUserParameters.CHAT_ID_LENGTH,
                                           default    = "",
                                           unique     = True) # TODO Possible that user could have multiple chat IDs
    usingTelegramAlerts = models.BooleanField(default = False)
    activationKeyHash   = models.CharField(max_length = 64,
                                           default    = "",
                                           db_index     = True)
