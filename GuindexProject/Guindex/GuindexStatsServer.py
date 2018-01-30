from decimal import Decimal

from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from Guindex import GuindexStatsIf_pb2 as GuindexStatsIf
from Guindex.models import Pub, Guinness, StatisticsSingleton, UserContributionsSingleton


class GuindexStatsServerFactory(protocol.ServerFactory):
    """
        Factory for creating GuindexStatsServers
    """

    def __init__(self, logger):

        self.logger = logger

    def buildProtocol(self, addr):
        return GuindexStatsServer(self.logger)


class GuindexStatsServer(Int16StringReceiver):
    """
        Class to deal with updating statistics asynchronously
    """

    def __init__(self, logger):

        # Use logger created in management command
        self.logger = logger

        self.stats              = StatisticsSingleton.load()
        self.user_contributions = UserContributionsSingleton.load()

        self.logger.debug("GuindexStatsServer init")

    def __del__(self):

        self.logger("GuindexStatsServer delete. Saving stats and user contributions")

        try:
            self.stats.save()
            self.logger.info("Saved stats")
        except:
            self.logger.error("Failed to save stats")

        try:
            self.user_contributions.save()
            self.logger.info("Saved user contributions")
        except:
            self.logger.error("Failed to save user contributions")

    def connectionMade(self):

        self.logger.info("Made connection with client from %s", self.transport.getPeer())

    def connectionLost(self, reason):

        self.logger.info("Lost connection with client from %s because %s",
                         self.transport.getPeer(), reason)

    def stringReceived(self, message):

        self.logger.debug("Received message - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        msg = GuindexStatsIf.GuindexStatsIfMessage()

        try:
            msg.ParseFromString(message)
            self.logger.debug("Successfully parsed received message")
        except:
            self.logger.error("Failed to parse received message")
            return

        if msg.HasField('newGuinnessStatsRequest'):

            self._handleNewGuinnessStatsRequest(msg)

        elif msg.HasField('newPubStatsRequest'):

            self._handleNewPubStatsRequest(msg)

        elif msg.HasField('pubClosedStatsRequest'):

            self._handlePubClosedStatsRequest(msg)

        elif msg.HasField('pubNotServingGuinnessStatsRequest'):

            self._handlePubNotServingGuinnessStatsRequest(msg)

        else:
            self.logger.error("Received unknown message type")

    def _handleNewGuinnessStatsRequest(self, message):

        self.logger.info("Received New Guinness Stats Request")

        guinness_id = message.newGuinnessStatsRequest.guinnessId

        try:
            guinness = Guinness.objects.get(id = guinness_id)
        except:
            self.logger.error("Could not find Guinness with id %d", guinness_id)
            return

        # Note: Order of function calls is important
        # Be careful if you shuffle them around

        try:
            self.adjustPercentageOfPubsVisited(guinness)
        except:
            self.logger.error("Failed to adjust percentage of pubs visited")

        try:
            self.adjustAveragePrice(guinness)
        except:
            self.logger.error("Failed to adjust average price")

        try:
            self.adjustStandardDeviation(guinness)
        except:
            self.logger.error("Failed to adjust standard deviation")

        try:
            self.adjustCheapestPints(guinness)
        except:
            self.logger.error("Failed to adjust cheapest pints")

        try:
            self.adjustDearestPints(guinness)
        except:
            self.logger.error("Failed to adjust dearest pints")

        try:
            self.adjustUserContributions(guinness)
        except:
            self.logger.error("Failed to adjust user contributions")

    def _handleNewPubStatsRequest(self, message):

        self.logger.info("Received New Pub Stats Request")

        pub_id = message.newPubStatsRequest.pubId

        try:
            pub = Pub.objects.get(id = pub_id)
        except:
            self.logger.error("Could not find Pub with id %d", pub_id)
            return

        # Note: Order of function calls is important
        # Be careful if you shuffle them around

        try:
            self.adjustnumberOfPubsInDatabase(pub)
        except:
            self.logger.error("Failed to adjust number of pubs in database")

        try:
            self.adjustPercentageOfPubsVisited(pub)
        except:
            self.logger.error("Failed to adjust percentage of pubs visited")

    def _handlePubClosedStatsRequest(self, message):

        self.logger.info("Received Pub Closed Stats Request")

        pub_id = message.pubClosedStatsRequest.pubId

        try:
            pub = Pub.objects.get(id = pub_id)
        except:
            self.logger.error("Could not find Pub with id %d", pub_id)
            return

        # Note: Order of function calls is important
        # Be careful if you shuffle them around

        try:
            self.adjustNumberOfPubsInDatabase(pub)
        except:
            self.logger.error("Failed to adjust number of pubs in database")

        try:
            self.adjustNumberOfClosedPubs(pub)
        except:
            self.logger.error("Failed to adjust number of closed pubs")

        try:
            self.adjustPercentageOfPubsVisited(pub)
        except:
            self.logger.error("Failed to adjust percentage of pubs visited")

        try:
            self.adjustAveragePrice(pub)
        except:
            self.logger.error("Failed to adjust average price")

    def _handlePubNotServingGuinnessStatsRequest(self, message):

        self.logger.info("Received Pub Not Serving Guinness Stats Request")

        pub_id = message.pubNotServingGuinnessStatsRequest.pubId

        try:
            pub = Pub.objects.get(id = pub_id)
        except:
            self.logger.error("Could not find Pub with id %d", pub_id)
            return

        # Note: Order of function calls is important
        # Be careful if you shuffle them around

        try:
            self.adjustNumberOfPubsNotServingGuinness(pub)
        except:
            self.logger.error("Failed to adjust number of pubs not serving Guinness")

        try:
            self.adjustPercentageOfPubsVisited(pub)
        except:
            self.logger.error("Failed to adjust percentage of pubs visited")

    def adjustPercentageOfPubsVisited(self, guindexObject):

        if type(guindexObject) == Pub:

            self.logger.debug("Object is a pub. Decrementing percentage of pubs visited")

            # Assume pubsInDb has already been incremeneted at this point
            self.stats.percentageVisited = self.stats.percentageVisited  * ((self.stats.pubsInDb - 1) / Decimal(self.stats.pubsInDb))

        elif type(guindexObject) == Guinness:

            self.logger.debug("Object is a Guinness")

            if guindexObject.pub.getFirstVerifiedGuinness() == guindexObject.pub.getLastVerifiedGuinness():

                self.logger.debug("Incrementing percentage of pubs visited")

                self.stats.percentageVisited = self.stats.percentageVisited + (100 / Decimal(self.stats.pubsInDb))

                return

            self.logger.debug("Pub has already been visited. Not incrementing percentage of pubs visited")

        else:
            self.logger.error("Invalid object type")
            return

    def adjustAveragePrice(self, guindexObject):

        if type(guindexObject) == Pub and guindexObject.closed:

            self.logger.debug("Object is a pub that has been closed")

            pub = guindexObject

            if not pub.getLastVerifiedGuinness():
                self.logger.debug("Pub had no verified prices. No need to adjust average price")
                return

            inverse_average = 1 / self.stats.averagePrice

            old_num_pubs_with_prices = self.stats.pubsWithPrices
            new_num_pubs_with_prices = self.stats.pubsWithPrices - 1

            last_price = pub.getLastVerifiedGuinness().price

            self.stats.averagePrice = (self.stats.averagePrice *
                                      ((old_num_pubs_with_prices / Decimal(new_num_pubs_with_prices)) -
                                      inverse_average * (last_price / new_num_pubs_with_prices)))

            self.stats.pubsWithPrices = new_num_pubs_with_prices

        elif type(guindexObject) == Guinness:

            self.logger.debug("Object is a Guinness")

            guinness = guindexObject

            if guinness.pub.getFirstVerifiedGuinness() == guinness.pub.getLastVerifiedGuinness():

                self.logger.debug("This is the first price added for this pub")

                inverse_average = 1 / self.stats.averagePrice

                old_num_pubs_with_prices = self.stats.pubsWithPrices
                new_num_pubs_with_prices = self.stats.pubsWithPrices + 1

                self.stats.averagePrice = (self.stats.averagePrice *
                                          ((old_num_pubs_with_prices / Decimal(new_num_pubs_with_prices)) +
                                          inverse_average * (guinness.price / new_num_pubs_with_prices)))

                self.stats.pubsWithPrices = new_num_pubs_with_prices

            else:

                self.logger.debug("This is not the first price added for this pub")

                # Get last price for this pub
                prices = guinness.pub.prices.all()[::-1]

                new_price  = guinness.price
                last_price = prices[1].price

                if new_price == last_price:

                    self.logger.debug("New price is the same as the last. No need to adjust average price")
                    return

                self.stats.averagePrice = self.stats.averagePrice + ((new_price - last_price) / self.stats.pubsWithPrices)

        else:
            self.logger.error("Invalid object type")
            return

    def adjustStandardDeviation(self, guinness):
        pass

    def adjustCheapestPints(self, guinness):

        # TODO Optimize this so we don't have to regenerate list

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

    def adjustDearestPints(self, guinness):

        # TODO Optimize this so we don't have to regenerate list
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
    
    def adjustUserContributions(self, guinness):
        pass

    def adjustNumberOfPubsInDatabase(self, pub):

        if pub.closed:
            self.logger.debug("Pub is closed. Decrementing number of pubs in DB")
            self.stats.pubsInDb = self.stats.pubsInDb - 1
        else:
            self.logger.debug("Incrementing number of pubs in DB")
            self.stats.pubsInDb = self.stats.pubsInDb + 1

    def adjustNumberOfClosedPubs(self, pub):

        if pub.closed:
            self.logger.debug("Incrementing number of closed pubs")
            self.stats.closedPubs = self.stats.closedPubs + 1

    def adjustNumberOfPubsNotServingGuinness(self, pub):

        if not pub.servingGuinness:
            self.logger.debug("Incrementing number of pubs not serving Guinness")
            self.stats.notServingGuinness = self.stats.notServingGuinness + 1
