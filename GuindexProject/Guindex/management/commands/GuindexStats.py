import logging
import time
import math
from decimal import Decimal

from django.core.management.base import BaseCommand

from Guindex.models import Pub, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters
from Guindex import GuindexUtils

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Calculating Statistics")
            statistics_singleton = StatisticsSingleton.load()

            try:
                logger.info("Calculating number of pubs")
                GuindexUtils.calculateNumberOfPubs(statistics_singleton)
            except:
                logger.error("Failed to calculate number of pubs")
                
            try:
                logger.info("Calculating cheapest pub")
                GuindexUtils.calculateCheapestPub(statistics_singleton)
            except:
                logger.error("Failed to calculate cheapest pub")
                
            try:
                logger.info("Calculating dearest pub")
                GuindexUtils.calculateDearestPub(statistics_singleton)
            except:
                logger.error("Failed to calculate dearest pub")
                
            try:
                logger.info("Calculating average price")
                GuindexUtils.calculateAveragePrice(statistics_singleton)
            except:
                logger.error("Failed to calculate average price")

            try:
                logger.info("Calculating standard deviation")
                GuindexUtils.calculateStandardDeviation(statistics_singleton)
            except:
                logger.error("Failed to calculate standard deviation")
                
            try:
                logger.info("Calculating percentage visited")
                GuindexUtils.calculatePercentageVisited(statistics_singleton)
            except:
                logger.error("Failed to calculate percentage visited")
                
            try:
                logger.info("Calculating closed pubs")
                GuindexUtils.calculateClosedPubs(statistics_singleton)
            except:
                logger.error("Failed to calculate closed pubs")

            try:
                logger.info("Calculating not serving Guinness")
                GuindexUtils.calculateNotServingGuinness(statistics_singleton)
            except:
                logger.error("Failed to calculate not serving Guinness")

            try:
                logger.info("Saving Statistics")
                statistics_singleton.save()
            except:
                logger.error("Failed to save statistics")

            logger.info("Sleeping for %d seconds", GuindexParameters.STATISTICS_CALCULATION_PERIOD)
            time.sleep(GuindexParameters.STATISTICS_CALCULATION_PERIOD)
