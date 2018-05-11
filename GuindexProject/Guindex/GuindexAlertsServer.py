from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from django.template.loader import render_to_string

from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf
from Guindex.GuindexBot import GuindexBot


class GuindexAlertsServerFactory(protocol.ServerFactory):
    """
        Factory for creating GuindexAlertsServers
    """

    def __init__(self, logger):

        self.logger = logger

    def buildProtocol(self, addr):
        return GuindexAlertsServer(self.logger)


class GuindexAlertsServer(Int16StringReceiver):
    """
        Class to deal with alerts asynchronously
    """

    def __init__(self, logger):

        # Use logger created in management command
        self.logger = logger

        self.logger.debug("GuindexAlertsServer init")

    def connectionMade(self):

        self.logger.info("Made connection with client from %s", self.transport.getPeer())

    def connectionLost(self, reason):

        self.logger.info("Lost connection with client from %s because %s",
                         self.transport.getPeer(), reason)

    def stringReceived(self, message):

        self.logger.debug("Received message - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        try:
            msg.ParseFromString(message)
            self.logger.debug("Successfully parsed received message")
        except:
            self.logger.error("Failed to parse received message")
            return

        if msg.HasField('guinnessCreateAlertRequest'):

            self._handleGuinnessCreateAlertRequest(msg.guinnessCreateAlertRequest)

        elif msg.HasField('guinnessPendingCreateDecisionAlertRequest'):

            self._handleGuinnessPendingCreateDecisionAlertRequest(msg.guinnessPendingCreateDecisionAlertRequest)

        elif msg.HasField('pubCreateAlertRequest'):

            self._handlePubCreateAlertRequest(msg.pubCreateAlertRequest)

        elif msg.HasField('pubPatchAlertRequest'):

            self._handlePubPatchAlertRequest(msg.pubPatchAlertRequest)

        elif msg.HasField('pubPendingCreateDecisionAlertRequest'):

            self._handlePubPendingCreateDecisionAlertRequest(msg.pubPendingCreateDecisionAlertRequest)

        elif msg.HasField('pubPendingPatchDecisionAlertRequest'):

            self._handlePubPendingPatchDecisionAlertRequest(msg.pubPendingPatchDecisionAlertRequest)

        else:
            self.logger.error("Received invalid message type")

    def _handleGuinnessCreateAlertRequest(self, message):

        self.logger.info("Received Guinness Create Alert Request message")

    def _handleGuinnessPendingCreateDecisionAlertRequest(self, message):

        self.logger.info("Received Guinness Pending Create Decision Alert Request message")

    def _handlePubCreateAlertRequest(self, message):

        self.logger.info("Received Pub Create Alert Request message")

    def _handlePubPatchAlertRequest(self, message):

        self.logger.info("Received Pub Patch Alert Request message")

    def _handlePubPendingCreateDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Pending Create Decision Alert Request message")

    def _handlePubPendingPatchDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Pending Patch Decision Alert Request message")
