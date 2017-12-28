import logging
import argparse

from django.conf import settings

from TelegramUser.TelegramBot import TelegramBot

logger = logging.getLogger(__name__.split('.')[-1])


class GuindexBot(TelegramBot):

    def __init__(self, apiKey = settings.BOT_HTTP_API_TOKEN):

        logger.info("Creating GuindexBot")

        # Initialise underlying Telegram class
        super(GuindexBot, self).__init__(apiKey)

        # Add custom commands handlers
