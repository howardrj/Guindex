import logging
import time
import math
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from Guindex.models import Pub, Guinness, StatisticsSingleton, GuindexUser
from Guindex.GuindexParameters import GuindexParameters


logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("***** Calculating statistics and user contributions *****")

            self.stats = StatisticsSingleton.load()

            # Note: Order of function calls is important
            # Be careful if you shuffle them around

            try:
                logger.info("Gathering pub price list")
                self.gatherPubPrices()
            except:
                logger.error("Failed to gather pub prices")

            try:
                logger.info("Calculating number of pubs")
                self.calculateNumberOfPubs()
            except:
                logger.error("Failed to calculate number of pubs")

            try:
                logger.info("Calculating pubs with prices")
                self.calculatePubsWithPrices()
            except:
                logger.error("Failed to calculate pubs with prices")

            try:
                logger.info("Calculating average price")
                self.calculateAveragePrice()
            except:
                logger.error("Failed to calculate average price")

            try:
                logger.info("Calculating standard deviation")
                self.calculateStandardDeviation()
            except:
                logger.error("Failed to calculate standard deviation")

            try:
                logger.info("Calculating closed pubs")
                self.calculateClosedPubs()
            except:
                logger.error("Failed to calculate closed pubs")

            try:
                logger.info("Calculating pubs not serving Guinness")
                self.calculateNotServingGuinness()
            except:
                logger.error("Failed to calculate not serving Guinness")

            try:
                logger.info("Calculating percentage visited")
                self.calculatePercentageVisited()
            except:
                logger.error("Failed to calculate percentage visited")

            try:
                logger.info("Calculating number of users")
                self.calculateNumberOfUsers()
            except:
                logger.error("Failed to calculate number of users")                

            try:
                logger.info("Saving statistics")
                self.stats.save()
            except:
                logger.error("Failed to save statistics")

            try:
                logger.info("Calculating user contributions")
                self.calculateUserContributions()
            except:
                logger.error("Failed to calculate user contributions")

            logger.info("Sleeping for %s seconds", GuindexParameters.STATS_CALCULATION_PERIOD)

            time.sleep(GuindexParameters.STATS_CALCULATION_PERIOD)

    def gatherPubPrices(self):
        """
            Fill up prices list for each pub in database
        """

        for pub in Pub.objects.all():

            pub.prices.clear()

            for guin in Guinness.objects.filter(pub = pub):

                pub.prices.add(guin)

            pub.save()

    def calculateNumberOfPubs(self):
        """
            Counts approved, open pubs
        """

        self.stats.pubsInDb = len(Pub.objects.all())

    def calculatePubsWithPrices(self):
        """
            Store approved, open pubs that are serving Guinness
            and have at least one verified price
        """

        self.stats.pubsWithPrices.clear()

        for pub in Pub.objects.all():

            if pub.getLastVerifiedGuinness() and pub.servingGuinness:
                self.stats.pubsWithPrices.add(pub)

    def calculateAveragePrice(self):
        """
            Calculate average price from pubs in pubsWithPrices list
        """

        sum_total = 0

        pubs_with_prices     = self.stats.pubsWithPrices.all()
        pubs_with_prices_len = len(pubs_with_prices)

        for pub in pubs_with_prices:

            sum_total = sum_total + pub.getLastVerifiedGuinness().price

        self.stats.averagePrice = sum_total / pubs_with_prices_len if pubs_with_prices_len else 0

    def calculateStandardDeviation(self):
        """
            Calculate standard deviation from pubs in pubsWithPrices list
        """

        if self.stats.averagePrice == 0:
            self.stats.standardDeviation = 0
            return

        variance_tmp = 0

        pubs_with_prices     = self.stats.pubsWithPrices.all()
        pubs_with_prices_len = len(pubs_with_prices)

        for pub in pubs_with_prices:

            variance_tmp = variance_tmp + math.pow((pub.getLastVerifiedGuinness().price - self.stats.averagePrice), 2)

        variance = Decimal(variance_tmp) / pubs_with_prices_len

        self.stats.standardDeviation = variance.sqrt()

    def calculateClosedPubs(self):

        self.stats.closedPubs = len(Pub.objects.filter(closed = True))

    def calculateNotServingGuinness(self):

        self.stats.notServingGuinness = len(Pub.objects.filter(servingGuinness = False))

    def calculatePercentageVisited(self):

        if self.stats.pubsInDb == 0:
            self.stats.percentageVisited = 0
            return

        self.stats.percentageVisited = 100 * (len(self.stats.pubsWithPrices.all()) + self.stats.notServingGuinness) / \
                                       Decimal(self.stats.pubsInDb)

    def calculateNumberOfUsers(self):

        self.stats.numUsers = len(User.objects.all())

    def calculateUserContributions(self):
        """
            Populate all GuindexUser fields for each User
        """

        logger.info("Calculating User Contributions")

        for user in User.objects.all():

            logger.debug("Calculating contributions for User %s", user)

            if not hasattr(user, 'guindexuser'):
                logger.debug("Need to create GuindexUser for User %s", user)

                guindexuser = GuindexUser()

                guindexuser.user = user
                guindexuser.save()

            number_of_current_verifications = 0
            number_of_first_verifications   = 0
            number_of_pubs_visited          = 0

            # Do it this way since we want to keep user stats
            # for closed and pubs marked as no longer serving Guinness
            for pub in Pub.objects.all():

                if pub.getLastVerifiedGuinness() and pub.getLastVerifiedGuinness().creator == user:
                    number_of_current_verifications = number_of_current_verifications + 1

                if pub.getFirstVerifiedGuinness() and pub.getFirstVerifiedGuinness().creator == user:
                    number_of_first_verifications = number_of_first_verifications + 1

                if len(Guinness.objects.filter(pub = pub, creator = user)):
                    number_of_pubs_visited = number_of_pubs_visited + 1

            user.guindexuser.originalPrices       = number_of_first_verifications
            user.guindexuser.currentVerifications = number_of_current_verifications
            user.guindexuser.pubsVisited          = number_of_pubs_visited

            user.guindexuser.save()
