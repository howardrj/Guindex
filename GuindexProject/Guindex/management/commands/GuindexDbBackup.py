import logging
import time
from subprocess import call

from django.core.management.base import BaseCommand

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Backing up Guindex database")

            call("/usr/bin/backup_guindex_db.sh")

            logger.info("Sleeping for %d seconds", GuindexParameters.DB_BACKUP_PERIOD)
            time.sleep(GuindexParameters.DB_BACKUP_PERIOD)
