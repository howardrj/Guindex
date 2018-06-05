import logging
import time
from shutil import copyfile
from datetime import datetime
from subprocess import call

import dropbox

from django.conf import settings
from django.core.management.base import BaseCommand

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__.split('.')[-1])

G_DB_NAME = settings.DATABASES['default']['NAME']


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Backing up Guindex database")

            # Append current time to database
            current_time = datetime.now().strftime('%Y-%B-%d_%H:%M:%S')

            copied_db_name = "%s-%s" % (G_DB_NAME, current_time)
            copied_db_leaf = copied_db_name.split('/')[-1] 
            
            # Copy file locally
            copyfile(G_DB_NAME, copied_db_name)

            # Copy file to dropbox
            dropbox_context = dropbox.Dropbox(settings.DROPBOX_API_ACCESS_TOKEN)

            try:
                with open(copied_db_name, 'rb') as f:
                    dropbox_context.files_upload(f.read(), '/GuindexDbBackups/' + copied_db_leaf, mute = True) 

                logger.info("Successfully uploaded %s to dropbox", copied_db_leaf)
            except:
                logger.error("Failed to upload %s to dropbox", copied_db_leaf)
                # TODO Take action     

            logger.info("Sleeping for %d seconds", GuindexParameters.DB_BACKUP_PERIOD)
            time.sleep(GuindexParameters.DB_BACKUP_PERIOD)
