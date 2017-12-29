import logging
import time

from django.core.management.base import BaseCommand

from Guindex.GuindexParameters import GuindexParameters
from Guindex.models import Pub, Guinness, UserContributionsSingleton
from Guindex import GuindexUtils

from GuindexUser import GuindexUserUtils

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:
        
            GuindexUtils.calculateUserContributions(logger)
            
            logger.info("Sleeping for %d seconds", GuindexParameters.USER_CONTRIBUTIONS_CALCULATION_PERIOD)
            time.sleep(GuindexParameters.USER_CONTRIBUTIONS_CALCULATION_PERIOD)
