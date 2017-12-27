import logging
import time

from django.core.management.base import BaseCommand

from Guindex.models import Pub, Guinness, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Calculating Statistics")
            statistics_singleton = StatisticsSingleton.load()

            try:
                logger.info("Calculating number of pubs")
                self.calculateNumberOfPubs(statistics_singleton)
            except:
                logger.error("Failed to calculate number of pubs")
                
            try:
                logger.info("Calculating cheapest pub")
                self.calculateCheapestPub(statistics_singleton)
            except:
                logger.error("Failed to calculate cheapest pub")
                
            try:
                logger.info("Calculating dearest pub")
                self.calculateDearestPub(statistics_singleton)
            except:
                logger.error("Failed to calculate dearest pub")
                
            try:
                logger.info("Calculating average price")
                self.calculateAveragePrice(statistics_singleton)
            except:
                logger.error("Failed to calculate average price")

            try:
                logger.info("Calculating standard deviation")
                self.calculateStandardDeviation(statistics_singleton)
            except:
                logger.error("Failed to calculate standard deviation")
                
            try:
                logger.info("Calculating percentage visited")
                self.calculatePercentageVisited(statistics_singleton)
            except:
                logger.error("Failed to calculate percentage visited")
                
            try:
                logger.info("Calculating closed pubs")
                self.calculateClosedPubs(statistics_singleton)
            except:
                logger.error("Failed to calculate closed pubs")

            try:
                logger.info("Calculating not serving Guinness")
                self.calculateNotServingGuinness(statistics_singleton)
            except:
                logger.error("Failed to calculate not serving Guinness")

            try:
                logger.info("Saving Statistics")
                statistics_singleton.save()
            except:
                logger.error("Failed to save statistics")

            logger.info("Sleeping for %d seconds", GuindexParameters.STATISTICS_CALCULATION_PERIOD)
            time.sleep(GuindexParameters.STATISTICS_CALCULATION_PERIOD)

    def calculateNumberOfPubs(self, statsSingleton): 

    def calculateCheapestPub(self, statsSingleton):

    def calculateDearestPub(self, statsSingleton):

    def calculateAveragePrice(self, statsSingleton):

    def calculateStandardDeviation(self, statsSingleton):

    def calculatePercentageVisited(self, statsSingleton):

    def calculateClosedPubs(self, statsSingleton):

    def calculateNotServingGuinness(self, statsSingleton):
