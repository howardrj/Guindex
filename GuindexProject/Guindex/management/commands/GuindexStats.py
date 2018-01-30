import logging
from decimal import Decimal
from twisted.internet import reactor

from django.core.management.base import BaseCommand

from Guindex.models import StatisticsSingleton, UserContributionsSingleton
from Guindex.GuindexParameters import GuindexParameters
from Guindex.GuindexStatsServer import GuindexStatsServerFactory

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Calculating Statistics on startup")

            self.stats              = StatisticsSingleton.load()
            self.user_contributions = UserContributionsSingleton.load()

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
                logger.info("Calculating cheapest pubs")
                self.calculateCheapestPubs()
            except:
                logger.error("Failed to calculate cheapest pubs")

            try:
                logger.info("Calculating dearest pubs")
                self.calculateDearestPubs()
            except:
                logger.error("Failed to calculate dearest pubs")

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
                logger.info("Calculating not serving Guinness")
                self.calculateNotServingGuinness()
            except:
                logger.error("Failed to calculate not serving Guinness")

            try:
                logger.info("Calculating percentage visited")
                self.calculatePercentageVisited()
            except:
                logger.error("Failed to calculate percentage visited")

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

            try:
                logger.info("Saving user contributions")
                self.user_contributions.save()
            except:
                logger.error("Failed to save user contributions")
                
            logger.info("Creating Guindex stats server")

            reactor.listenTCP(GuindexParameters.STATS_LISTEN_PORT,
                              GuindexAlertsServerFactory(logger),
                              GuindexParameters.STATS_BACKLOG,
                              GuindexParameters.STATS_LISTEN_IP)

            logger.info("Created TCP server listening on %s:%d. Waiting for stats updates ...",
                        GuindexParameters.STATS_LISTEN_IP, GuindexParameters.STATS_LISTEN_PORT)

            reactor.run()

    def gatherPubPrices(self):

        for pub in Pub.objects.all():

            pub.prices.clear()

            for guin in Guinness.objects.filter(pub = pub).order_by('creationDate'):

                pub.prices.add(guin)

            pub.save()

    def calculateNumberOfPubs(self):

        # Only returns approved, open pubs
        self.stats.pubsInDb = len(Pub.objects.filter(closed = False,
                                                     pendingApproval = False,
                                                     pendingApprovalRejected = False))

    def calculateCheapestPubs(self):

        cheapest_pubs = []

        for pub in Pub.objects.filter(closed = False,
                                      pendingApproval = False,
                                      pendingApprovalRejected = False):

            if pub.getLastVerifiedGuinness():
                cheapest_pubs.append(pub)

        cheapest_pubs = sorted(cheapest_pubs, 
                               key = lambda x: x.getLastVerifiedGuinness().price,
                               reverse = False)

        self.cheapestPubs.clear()
        self.cheapestPubs.add(*cheapest_pubs)

    def calculateDearestPubs(self):

        dearest_pubs = []

        for pub in Pub.objects.filter(closed = False,
                                      pendingApproval = False,
                                      pendingApprovalRejected = False):

            if pub.getLastVerifiedGuinness():
                dearest_pubs.append(pub)

        dearest_pubs = sorted(dearest_pubs,
                              key = lambda x: x.getLastVerifiedGuinness().price,
                              reverse = True)

        self.dearestPubs.clear()
        self.dearestPubs.add(*dearest_pubs)

    def calculateAveragePrice(self):

        visited_pubs = 0
        sum_total    = 0

        for pub in Pub.objects.filter(closed = False,
                                      pendingApproval = False,
                                      pendingApprovalRejected = False):

            if pub.getLastVerifiedGuinness():
                visited_pubs = visited_pubs + 1
                sum_total    = sum_total + pub.getLastVerifiedGuinness().price

        if visited_pubs == 0:
            self.stats.averagePrice = 0
            return

        self.stats.pubsWithPrices = visited_pubs
        self.stats.averagePrice   = sum_total / visited_pubs

    def calculateStandardDeviation(self):

        variance_tmp = 0
        visited_pubs = 0

        if self.stats.averagePrice == 0:
            self.stats.standardDevation = 0
            return

        for pub in Pub.objects.filter(closed = False,
                                      pendingApproval = False,
                                      pendingApprovalRejected = False):

            if pub.getLastVerifiedGuinness():
                visited_pubs = visited_pubs + 1
                variance_tmp = variance_tmp + math.pow((pub.getLastVerifiedGuinness().price - self.stats.averagePrice), 2)

        variance = variance_tmp / visited_pubs

        self.stats.pubsWithPrices   = visited_pubs
        self.stats.standardDevation = variance.sqrt()

    def calculateClosedPubs(self):

        self.stats.closedPubs = len(Pub.objects.filter(closed = True))

    def calculateNotServingGuinness(self):

        self.stats.notServingGuinness = len(Pub.objects.filter(servingGuinness = False))

    def calculatePercentageVisited(self):

        visited_pubs = 0

        if self.stats.pubsInDb == 0:
            self.stats.percentageVisited = 0
            return

        for pub in Pub.objects.filter(closed = False,
                                      pendingApproval = False,
                                      pendingApprovalRejected = False):

            if pub.getLastVerifiedGuinness() or not pub.servingGuinness:
                visited_pubs = visited_pubs + 1

        self.stats.percentageVisited = (Decimal(visited_pubs) / self.stats.pubsInDb) * 100

    def calculateUserContributions(self):

        logger.info("Calculating User Contributions")

        most_pubs_visited          = []
        most_first_verifications   = []
        most_current_verifications = []

        for user_profile in UserProfile.objects.all():

            logger.debug("Calculating contributions for UserProfile %s", user_profile)

            if not user_profile.guindexuser:
                logger.debug("Need to create GuindexUser for UserProfile %s", user_profile)

                GuindexUserUtils.createNewGuindexUser(user_profile)

            number_of_current_verifications = 0
            number_of_first_verifications   = 0
            number_of_pubs_visited          = 0

            for pub in Pub.objects.all():

                if pub.getLastVerifiedGuinness():
                    if pub.getLastVerifiedGuinness().creator == user_profile:
                        number_of_current_verifications = number_of_current_verifications + 1

                if pub.getFirstVerifiedGuinness():
                    if pub.getFirstVerifiedGuinness().creator == user_profile:
                        number_of_first_verifications = number_of_first_verifications + 1

                if len(Guinness.objects.filter(pub = pub, creator = user_profile)):
                    number_of_pubs_visited = number_of_pubs_visited + 1

            user_profile.guindexuser.originalPrices       = number_of_first_verifications
            user_profile.guindexuser.currentVerifications = number_of_current_verifications
            user_profile.guindexuser.pubsVisited          = number_of_pubs_visited

            user_profile.guindexuser.save()

            most_pubs_visited.append(user_profile)
            most_first_verifications.append(user_profile)
            most_current_verifications.append(user_profile)

        # Sort lists
        most_pubs_visited          = sorted(most_pubs_visited,
                                            key = lambda x: x.guindexuser.pubsVisited,
                                            reverse = True)
        most_first_verifications   = sorted(most_first_verifications,
                                            key = lambda x: x.guindexuser.originalPrices,
                                            reverse = True)
        most_current_verifications = sorted(most_current_verifications,
                                            key = lambda x: x.guindexuser.currentVerifications,
                                            reverse = True)

        # Add lists to model fields
        self.user_contributions.mostVisited.clear()
        self.user_contributions.mostVisited.add(*most_visited)

        self.user_contributions.mostLastVerified.clear()
        self.user_contributions.mostLastVerified.add(*most_current_verifications)

        self.user_contributions.mostFirstVerified.clear()
        self.user_contributions.mostFirstVerified.add(*most_first_verifications)

        logger.info("Saving User Contributions Singleton %s", self.user_contributions)
