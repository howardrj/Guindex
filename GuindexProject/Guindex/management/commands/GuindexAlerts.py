import logging
import time

from django.core.management.base import BaseCommand

from UserProfile.models import UserProfile

from Guindex.models import Pub, AlertsSingleton
from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
            Note: This could be more sophisticated.
            As of now, it only checks the most last verified Guinness
            and not all.
        """
        
        while True:

            logger.info("Checking Alerts")
            alerts_singleton = AlertsSingleton.load()
            pub_list = []

            for pub in Pub.objects.all():

                pub_dict = {}

                if pub.getLastVerfiedGuinness():

                    if pub.getLastVerfiedGuinness()['creationDate'] > alerts_singleton.lastAlertsCheck:
                        logger.info("Pub %s received a new price") 

                        pub_dict['name']         = pub.name
                        pub_dict['price']        = pub.getLastVerfiedGuinness()['price']
                        pub_dict['creationDate'] = pub.getLastVerfiedGuinness()['creationDate']
                        pub_dict['creator']      = pub.getLastVerfiedGuinness()['creator']

                        pub_list.append(pub_dict.copy())
                        
                else:
                    continue

            for user_profile in UserProfile.objects.all():
               pass 

            try:
                logger.info("Saving Alerts state")
                alerts_singleton.save()
            except:
                logger.error("Failed to save Alerts state")

            logger.info("Sleeping for %d seconds", GuindexParameters.ALERTS_CHECK_PERIOD)
            time.sleep(GuindexParameters.ALERTS_CHECK_PERIOD)
