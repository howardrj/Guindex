import logging
import time
import math
from decimal import Decimal

from django.core.management.base import BaseCommand

from Guindex.models import Pub, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

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

        statsSingleton.pubsInDb = len(Pub.objects.all())

        logger.info("%d", statsSingleton.pubsInDb)

    def calculateCheapestPub(self, statsSingleton):
             
        cheapest_pub = None

        for pub_index, pub in enumerate(Pub.objects.all()): 

            if pub_index == 0:
                cheapest_pub = pub

            if not pub.getLastVerifiedGuinness():
                continue
            elif pub.getLastVerifiedGuinness()['price'] < cheapest_pub.getLastVerifiedGuinness()['price']:
                cheapest_pub = pub

        statsSingleton.cheapestPub = cheapest_pub

        logger.info("%s", statsSingleton.cheapestPub)

    def calculateDearestPub(self, statsSingleton):

        dearest_pub = None

        for pub_index, pub in enumerate(Pub.objects.all()): 

            if pub_index == 0:
                dearest_pub = pub

            if not pub.getLastVerifiedGuinness():
                continue
            elif pub.getLastVerifiedGuinness()['price'] > dearest_pub.getLastVerifiedGuinness()['price']:
                dearest_pub = pub

        statsSingleton.dearestPub = dearest_pub
        
        logger.info("%s", statsSingleton.dearestPub)

    def calculateAveragePrice(self, statsSingleton):

        visited_pubs = 0
        sum_total    = 0

        for pub in Pub.objects.all(): 

            if pub.getLastVerifiedGuinness():
                visited_pubs = visited_pubs + 1
                sum_total    = sum_total + pub.getLastVerifiedGuinness()['price']

        statsSingleton.averagePrice = Decimal(sum_total / visited_pubs)

        logger.info("%s", statsSingleton.averagePrice)

    def calculateStandardDeviation(self, statsSingleton):

        variance_tmp = 0

        for pub in Pub.objects.all(): 

            if pub.getLastVerifiedGuinness():
                variance_tmp = variance_tmp + math.pow((pub.getLastVerifiedGuinness()['price'] - statsSingleton.averagePrice), 2)

        variance = Decimal(variance_tmp) / statsSingleton.averagePrice    

        statsSingleton.standardDevation = variance.sqrt()

        logger.info("%s", statsSingleton.standardDevation)

    def calculatePercentageVisited(self, statsSingleton):

        visited_pubs = 0

        for pub in Pub.objects.all(): 

            if pub.getLastVerifiedGuinness() or not pub.servingGuinness:
                visited_pubs = visited_pubs + 1

        statsSingleton.percentageVisited = Decimal(visited_pubs) / statsSingleton.pubsInDb

        logger.info("%s", statsSingleton.percentageVisited)

    def calculateClosedPubs(self, statsSingleton):

        statsSingleton.closedPubs = len(Pub.objects.filter(closed = True))

        logger.info("%d", statsSingleton.closedPubs)

    def calculateNotServingGuinness(self, statsSingleton):

        statsSingleton.notServingGuinness = len(Pub.objects.filter(servingGuinness = False))

        logger.info("%d", statsSingleton.notServingGuinness)
