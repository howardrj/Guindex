# -*- coding: utf-8 -*-
import socket

from Guindex.GuindexParameters import GuindexParameters
from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf

from UserProfile import UserProfileUtils


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
            (appending two byte length header by default)
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

    def sendApprovalDecisionAlertRequest(self, guinness):

        self.logger.info("Sending Approval Decision Alert Request")

        # Create Approval Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.approvalDecisionAlertRequest.creatorId    = str(guinness.creator.id)
        guindex_alerts_msg.approvalDecisionAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.approvalDecisionAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.approvalDecisionAlertRequest.approved     = guinness.approved
        guindex_alerts_msg.approvalDecisionAlertRequest.creationDate = '%s' % guinness.creationDate

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Approval Decision Alert Request message")
            raise

        self.sendMessage(message_string)
