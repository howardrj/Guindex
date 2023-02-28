import logging

from django.db import models
from django.contrib.auth.models import User

from TelegramUser.TelegramUserParameters import TelegramUserParameters

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
                                           unique     = True) # Doesn't really need to be unique but let's do it in case
    chatId              = models.CharField(max_length = TelegramUserParameters.CHAT_ID_LENGTH,
                                           default    = "",
                                           unique     = True) # TODO Possible that user could have multiple chat IDs
    usingTelegramAlerts = models.BooleanField(default = False)
