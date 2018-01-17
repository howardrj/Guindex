# -*- coding: utf-8 -*-
import socket

from Guindex.GuindexParameters import GuindexParameters
from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf


class GuindexAlertsClient():

    def __init__(self, logger):

        self.logger     = logger
        self._connection = self._createConnection()

        self.logger.debug("Created GuindexAlertsClient %s", self)

    def __del__(self):

        self.logger.debug("Destroying GuindexAlertsClient %s", self)
        self._connection.close()

    def _createConnection(self):

        alerts_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.logger.info("Creating TCP connection to Alerts Server")
            alerts_socket.connect((GuindexParameters.ALERTS_LISTEN_IP, GuindexParameters.ALERTS_LISTEN_PORT))
            self.logger.info("Successfully connected to Alerts Server")
        except socket.error:
            self.logger.error("Failed to connect to Alerts Server")
            alerts_socket.close()
            raise

        return alerts_socket

    def sendMessage(self, message, prependTwoByteHeader = True):
        """
            Sends string 'message' to Alerts Server
            (prepending two byte length header by default)
        """

        self.logger.debug("Sending message to Guindex Alerts Server - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        if prependTwoByteHeader:

            self.logger.debug("Prepending two byte length header to message")

            message_length = len(message)

            self.logger.debug("Message length = %d", message_length)

            message_length_first_byte = (message_length >> 8) & 0xFF
            message_length_second_byte = message_length & 0xFF
            message = chr(message_length_first_byte) + chr(message_length_second_byte) + message

            self.logger.debug("Updated message - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        try:
            self._connection.send(message)
        except:
            self.logger.error("Failed to send message to Alerts Server")
            raise

    def sendNewGuinnessAlertRequest(self, guinness):

        self.logger.info("Sending New Guinnness Alert Request")

        # Create New Guinness Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.newGuinnessAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.newGuinnessAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.newGuinnessAlertRequest.username     = guinness.creator.user.username
        guindex_alerts_msg.newGuinnessAlertRequest.approved     = guinness.approved
        guindex_alerts_msg.newGuinnessAlertRequest.creationDate = '%s' % guinness.creationDate

        if not guinness.approved: # Give url of pending contributions
            guindex_alerts_msg.newGuinnessAlertRequest.uri = "https://guindex.ie"

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Guinness Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendNewPubAlertRequest(self, pub):

        self.logger.info("Sending New Pub Alert Request")

        # Create New Pub Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.newPubAlertRequest.pub          = pub.name
        guindex_alerts_msg.newPubAlertRequest.latitude     = str(pub.latitude)
        guindex_alerts_msg.newPubAlertRequest.longitude    = str(pub.longitude)
        guindex_alerts_msg.newPubAlertRequest.username     = pub.pendingApprovalContributor.user.username
        guindex_alerts_msg.newPubAlertRequest.approved     = not pub.pendingApproval
        guindex_alerts_msg.newPubAlertRequest.creationDate = '%s' % pub.pendingApprovalTime

        if pub.pendingApproval: # Give url of pending contributions
            guindex_alerts_msg.newPubAlertRequest.uri = "https://guindex.ie"

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Pub Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendPubClosedAlertRequest(self, pub):

        self.logger.info("Sending Pub Closed Alert Request")

        # Create Pub Closed Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubClosedAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubClosedAlertRequest.username     = pub.pendingClosedContributor.user.username
        guindex_alerts_msg.pubClosedAlertRequest.approved     = not pub.pendingClosed
        guindex_alerts_msg.pubClosedAlertRequest.creationDate = '%s' % pub.pendingClosedTime

        if pub.pendingClosed: # Give url of pending contributions
            guindex_alerts_msg.pubClosedAlertRequest.uri = "https://guindex.ie"

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Closed Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendPubNotServingGuinnessAlertRequest(self, pub):

        self.logger.info("Sending Pub Not Serving Guinness Alert Request")

        # Create Pub Not Serving Guinness Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.username     = pub.pendingNotServingGuinnessContributor.user.username
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.approved     = not pub.pendingNotServingGuinness
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.creationDate = '%s' % pub.pendingNotServingGuinnessTime

        if pub.pendingNotServingGuinness: # Give url of pending contributions
            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.uri = "https://guindex.ie"

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Not Serving Guinness Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendNewGuinnessDecisionAlertRequest(self, guinness):

        self.logger.info("Sending New Guinness Decision Alert Request")

        # Create New Guinness Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.newGuinnessDecisionAlertRequest.creatorId    = str(guinness.creator.id)
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.approved     = guinness.approved
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.creationDate = '%s' % guinness.creationDate

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Guinness Decision Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendNewPubDecisionAlertRequest(self, pub):

        self.logger.info("Sending New Pub Decision Alert Request")

        # Create New Pub Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.newPubDecisionAlertRequest.creatorId    = str(pub.pendingApprovalContributor.id)
        guindex_alerts_msg.newPubDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.newPubDecisionAlertRequest.latitude     = str(pub.latitude)
        guindex_alerts_msg.newPubDecisionAlertRequest.longitude    = str(pub.longitude)
        guindex_alerts_msg.newPubDecisionAlertRequest.approved     = not pub.pendingApproval
        guindex_alerts_msg.newPubDecisionAlertRequest.creationDate = '%s' % pub.pendingApprovalTime

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Pub Decision Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendPubClosedDecisionAlertRequest(self, pub):

        self.logger.info("Sending Pub Closed Decision Alert Request")

        # Create Pub Closed Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubClosedDecisionAlertRequest.creatorId    = str(pub.pendingClosedContributor.id)
        guindex_alerts_msg.pubClosedDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubClosedDecisionAlertRequest.approved     = not pub.pendingClosed
        guindex_alerts_msg.pubClosedDecisionAlertRequest.creationDate = '%s' % pub.pendingClosedTime

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Closed Decision Alert Request message")
            raise

        self.sendMessage(message_string)

    def sendPubNotServingGuinnessDecisionAlertRequest(self, pub):

        self.logger.info("Sending Pub Not Serving Guinness Decision Alert Request")

        # Create Pub Not Serving Guinness Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.creatorId    = str(pub.pendingNotServingGuinnessContributor.id)
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.approved     = not pub.pendingNotServingGuinness
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.creationDate = '%s' % pub.pendingNotServingGuinnessTime

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Not Serving Guinness Decision Alert Request message")
            raise

        self.sendMessage(message_string)
