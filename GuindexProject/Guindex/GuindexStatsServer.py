import math
from decimal import Decimal

from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from Guindex import GuindexStatsIf_pb2 as GuindexStatsIf
from Guindex.models import Pub, Guinness, StatisticsSingleton


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
        self.stats  = StatisticsSingleton.load()

        self.logger.debug("GuindexStatsServer init")

    def __del__(self):

        self.logger.debug("GuindexStatsServer delete. Saving stats and user contributions")

        try:
            self.stats.save()
            self.logger.info("Saved stats")
        except:
            self.logger.error("Failed to save stats")

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
            self.adjustPubsWithPrices(guinness)
        except:
            self.logger.error("Failed to adjust pubs with prices list")

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
            self.adjustNumberOfPubsInDatabase(pub)
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
            self.adjustPubsWithPrices(pub)
        except:
            self.logger.error("Failed to adjust pubs with prices list")

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
            self.adjustAveragePrice(pub) # In case where pub had approved price before closing
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
            self.adjustPubsWithPrices(pub)
        except:
            self.logger.error("Failed to adjust pubs with prices")

        try:
            self.adjustNumberOfPubsNotServingGuinness(pub)
        except:
            self.logger.error("Failed to adjust number of pubs not serving Guinness")

        try:
            self.adjustPercentageOfPubsVisited(pub)
        except:
            self.logger.error("Failed to adjust percentage of pubs visited")

        try:
            self.adjustAveragePrice(pub) # In case where pub previously served Guinness
        except:
            self.logger.error("Failed to adjust average price")

    def adjustPubsWithPrices(self, guindexObject):

        self.logger.info("Adjusting pubs with prices list")

        if type(guindexObject) == Guinness:

            guinness = guindexObject

            # Add pub to pubWithPrices list if this is the pub's first approved price
            if guinness.pub.getLastVerifiedGuinness() == guinness.pub.getFirstVerifiedGuinness():
                self.logger.info("Adding pub %s to pubs with prices list", guinness.pub)
                self.stats.pubsWithPrices.add(guinness.pub)
            else:
                self.logger.debug("Pub is already in pubs with prices list")

        elif type(guindexObject) == Pub:

            pub = guindexObject

            # If pub is closed or not serving Guinness, remove from list
            if pub.closed or not pub.servingGuinness:
                self.logger.info("Attempting to remove %s from pubs with prices list", pub)
                self.stats.pubsWithPrices.remove(pub)
            else:
                self.logger.debug("Pub does not need to be removed from pubs with prices list")

        else:
            self.logger.error("Invalid object type")
            raise Exception("Invalid object type")

    def adjustPercentageOfPubsVisited(self, guindexObject):

        self.logger.info("Adjusting percentage of pubs visited")

        if type(guindexObject) == Guinness:

            guinness = guindexObject

            # Only adjust percentage visited if this is only price for this pub
            if guinness.pub.getFirstVerifiedGuinness() == guinness.pub.getLastVerifiedGuinness():
                self.logger.debug("Incrementing percentage of pubs visited")
                self.stats.percentageVisited = self.stats.percentageVisited + (100 / Decimal(self.stats.pubsInDb))
            else:
                self.logger.debug("Pub has already been visited. Not incrementing percentage of pubs visited")

        elif type(guindexObject) == Pub:

            pub = guindexObject

            # Assume pubsInDb has already been incremented at this point

            if not pub.servingGuinness: # Pub was marked as not serving Guinness

                self.logger.debug("Pub marked as not serving Guinness, incrementing percentage of pubs visited")
                self.stats.percentageVisited = self.stats.percentageVisited + (100 / Decimal(self.stats.pubsInDb))

            elif pub.closed:
                self.logger.debug("Pub closed, decrementing percentage of pubs visited")

                if pub.getLastVerifiedGuinness():
                    self.logger.debug("Pub had been visited")
                    self.stats.percentageVisited = self.stats.percentageVisited  * ((self.stats.pubsInDb + 1) / Decimal(self.stats.pubsInDb)) - \
                                                   (100 / Decimal(self.stats.pubsInDb))

                else:
                    self.logger.debug("Pub had not been visited")
                    self.stats.percentageVisited = self.stats.percentageVisited  * ((self.stats.pubsInDb + 1) / Decimal(self.stats.pubsInDb))

            else: # New pub was added

                self.logger.debug("Pub added, decrementing percentage of pubs visited")
                self.stats.percentageVisited = self.stats.percentageVisited  * ((self.stats.pubsInDb - 1) / Decimal(self.stats.pubsInDb))

        else:
            self.logger.error("Invalid object type")
            raise Exception("Invalid object type")

    def adjustAveragePrice(self, guindexObject):

        self.logger.info("Adjusting average price")

        if type(guindexObject) == Guinness:

            guinness = guindexObject

            if guinness.pub.getFirstVerifiedGuinness() == guinness.pub.getLastVerifiedGuinness():

                self.logger.debug("This is the first price added for this pub")

                inverse_average = 1 / self.stats.averagePrice

                # Assume pubsWithPrices has been updated at this point

                old_num_pubs_with_prices = len(self.stats.pubsWithPrices.all()) - 1
                new_num_pubs_with_prices = old_num_pubs_with_prices + 1

                self.stats.averagePrice = (self.stats.averagePrice *
                                          ((old_num_pubs_with_prices / Decimal(new_num_pubs_with_prices)) +
                                          inverse_average * (guinness.price / new_num_pubs_with_prices)))

            else:

                self.logger.debug("This is not the first price added for this pub")

                # Get last price for this pub
                prices = guinness.pub.prices.filter(approved = True)[::-1]

                new_price  = guinness.price
                last_price = prices[1].price

                if new_price == last_price:

                    self.logger.debug("New price is the same as the last. No need to adjust average price")
                    return

                self.stats.averagePrice = self.stats.averagePrice + ((new_price - last_price) / len(self.stats.pubsWithPrices.all()))

        elif type(guindexObject) == Pub:

            pub = guindexObject

            if pub.closed:
                self.logger.debug("Pub has closed. Removing it's price from average")
            elif not pub.servingGuinness:
                self.logger.debug("Pub has beeen marked as not serving Guinness. Removing it's price from average")
            else:
                self.logger.error("Pub has not closed and is serving Guinness. Not adjusting average price")
                return

            if not pub.getLastVerifiedGuinness():
                self.logger.debug("Pub had no verified prices. No need to adjust average price")
                return

            # Assume pubsWithPrices has been updated at this point
            inverse_average = 1 / self.stats.averagePrice

            old_num_pubs_with_prices = len(self.stats.pubsWithPrices.all()) - 1
            new_num_pubs_with_prices = old_num_pubs_with_prices + 1

            last_price = pub.getLastVerifiedGuinness().price

            self.stats.averagePrice = (self.stats.averagePrice *
                                      ((old_num_pubs_with_prices / Decimal(new_num_pubs_with_prices)) -
                                      inverse_average * (last_price / new_num_pubs_with_prices)))

        else:
            self.logger.error("Invalid object type")
            raise Exception("Invalid object type")

    def adjustStandardDeviation(self, guinness):

        self.logger.info("Adjusting standard deviation")

        # TODO Optimize this so we don't have to fully calculate it again
        # Assume pubsWithPrices has been populated at this point

        if self.stats.averagePrice == 0:
            self.stats.standardDeviation = 0
            return

        variance_tmp = 0

        # Assume pubsWithPrices has been updated at this point

        pubs_with_prices     = self.stats.pubsWithPrices.all()
        pubs_with_prices_len = len(pubs_with_prices)

        for pub in pubs_with_prices:

            variance_tmp = variance_tmp + math.pow((pub.getLastVerifiedGuinness().price - self.stats.averagePrice), 2)

        variance = Decimal(variance_tmp) / pubs_with_prices_len

        self.stats.standardDeviation = variance.sqrt()

    def adjustUserContributions(self, guinness):

        self.logger.info("Adjusting user contributions statistics")

        # First price added for this pub
        if guinness.pub.getFirstVerifiedGuinness() == guinness.pub.getLastVerifiedGuinness():

            self.logger.debug("Incrementing number of original prices for %s", guinness.creator)
            guinness.creator.guindexuser.originalPrices = guinness.creator.guindexuser.originalPrices + 1

            self.logger.debug("Incrementing number of current verifications for %s", guinness.creator)
            guinness.creator.guindexuser.currentVerifications = guinness.creator.guindexuser.currentVerifications + 1

            guinness.creator.guindexuser.save()

        else: # More than one price has been approved for this pub

            previous_verifier = guinness.pub.prices.filter(approved = True)[::-1][1].creator

            if not previous_verifier == guinness.creator:

                self.logger.debug("Incrementing number of current verifications for %s", guinness.creator)
                guinness.creator.guindexuser.currentVerifications  = guinness.creator.guindexuser.currentVerifications + 1

                self.logger.debug("Decrementing number of current verifications for %s", previous_verifier)
                previous_verifier.guindexuser.currentVerifications = previous_verifier.guindexuser.currentVerifications - 1

                guinness.creator.guindexuser.save()
                previous_verifier.guindexuser.save()

        # Do we need to adjust number of visits?
        if len(Guinness.objects.filter(approved = True,
                                       pub = guinness.pub,
                                       creator = guinness.creator)) == 1:

            self.logger.debug("Increasing number of visits for %s", guinness.creator)
            guinness.creator.guindexuser.pubsVisited = guinness.creator.guindexuser.pubsVisited + 1

            guinness.creator.guindexuser.save()

    def adjustNumberOfPubsInDatabase(self, pub):

        self.logger.info("Adjusting number of pubs in database")

        if pub.closed:
            self.logger.debug("Pub is closed. Decrementing number of pubs in DB")
            self.stats.pubsInDb = self.stats.pubsInDb - 1
        else:
            self.logger.debug("Incrementing number of pubs in DB")
            self.stats.pubsInDb = self.stats.pubsInDb + 1

    def adjustNumberOfClosedPubs(self, pub):

        self.logger.info("Adjusting number of closed pubs")

        if pub.closed:
            self.logger.debug("Incrementing number of closed pubs")
            self.stats.closedPubs = self.stats.closedPubs + 1

    def adjustNumberOfPubsNotServingGuinness(self, pub):

        self.logger.info("Adjusting number of pubs not serving Guinness")

        if not pub.servingGuinness:
            self.logger.debug("Incrementing number of pubs not serving Guinness")
            self.stats.notServingGuinness = self.stats.notServingGuinness + 1
