from Guindex.GuindexClient import GuindexClient
from Guindex import GuindexStatsIf_pb2 as GuindexStatsIf


class GuindexStatsClient(GuindexClient):

    def __init__(self, logger, serverIp, serverPort):

        logger.debug("Creating GuindexStats client")

        super(GuindexStatsClient, self).__init__(logger, 'Stats', serverIp, serverPort)

    def sendNewGuinnessStatsRequest(self, guinness):

        self.logger.info("Sending New Guinnness Stats Request")

        # Create New Guinness Stats Request message
        guindex_stats_msg = GuindexStatsIf.GuindexStatsIfMessage()

        guindex_stats_msg.newGuinnessStatsRequest.guinnessId = guinness.id

        try:
            message_string = guindex_stats_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Guinness Stats Request message")
            raise Exception("Failed to serialize New Guinness Stats Request message")

        self.sendMessage(message_string)

    def sendNewPubStatsRequest(self, pub):

        self.logger.info("Sending New Pub Stats Request")

        # Create New Pub Stats Request message
        guindex_stats_msg = GuindexStatsIf.GuindexStatsIfMessage()

        guindex_stats_msg.newPubStatsRequest.pubId = pub.id

        try:
            message_string = guindex_stats_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Pub Stats Request message")
            raise Exception("Failed to serialize New Pub Stats Request message")

        self.sendMessage(message_string)

    def sendPubClosedStatsRequest(self, pub):

        self.logger.info("Sending Pub Closed Stats Request")

        # Create Pub Closed Stats Request message
        guindex_stats_msg = GuindexStatsIf.GuindexStatsIfMessage()

        guindex_stats_msg.pubClosedStatsRequest.pubId = pub.id

        try:
            message_string = guindex_stats_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Closed Stats Request message")
            raise Exception("Failed to serialize Pub Closed Stats Request message")

        self.sendMessage(message_string)

    def sendPubNotServingGuinnessStatsRequest(self, pub):

        self.logger.info("Sending Pub Not Serving Guinness Stats Request")

        # Create Pub Not Serving Guinness Stats Request message
        guindex_stats_msg = GuindexStatsIf.GuindexStatsIfMessage()

        guindex_stats_msg.pubNotServingGuinnessStatsRequest.pubId = pub.id

        try:
            message_string = guindex_stats_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Not Serving Guinness Stats Request message")
            raise Exception("Failed to serialize Pub Not Serving Guinness Stats Request message")

        self.sendMessage(message_string)
