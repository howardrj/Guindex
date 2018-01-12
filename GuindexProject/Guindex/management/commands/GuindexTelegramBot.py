import logging

from django.core.management.base import BaseCommand

from Guindex.GuindexBot import GuindexBot

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        guindex_bot = GuindexBot()

        print("Polling for incoming messages ...")

        guindex_bot.start_polling()
