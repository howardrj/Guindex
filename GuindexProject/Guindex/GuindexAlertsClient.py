# -*- coding: utf-8 -*-
from UserProfile import UserProfileUtils

from Guindex.GuindexClient import GuindexClient
from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf


class GuindexAlertsClient(GuindexClient):

    def __init__(self, logger, serverIp, serverPort):

        logger.debug("Creating GuindexAlerts client")

        super(GuindexAlertsClient, self).__init__(logger, 'Alerts', serverIp, serverPort)

    def sendNewGuinnessAlertRequest(self, guinness, httpRequest):

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
            guindex_alerts_msg.newGuinnessAlertRequest.uri = UserProfileUtils.getProjectUri(httpRequest)

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Guinness Alert Request message")
            raise Exception("Failed to serialize New Guinness Alert Request message")

        self.sendMessage(message_string)

    def sendNewPubAlertRequest(self, pub, httpRequest):

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
            guindex_alerts_msg.newPubAlertRequest.uri = UserProfileUtils.getProjectUri(httpRequest)

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Pub Alert Request message")
            raise Exception("Failed to serialize New Pub Alert Request message")

        self.sendMessage(message_string)

    def sendPubClosedAlertRequest(self, pub, httpRequest):

        self.logger.info("Sending Pub Closed Alert Request")

        # Create Pub Closed Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubClosedAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubClosedAlertRequest.username     = pub.pendingClosedContributor.user.username
        guindex_alerts_msg.pubClosedAlertRequest.approved     = not pub.pendingClosed
        guindex_alerts_msg.pubClosedAlertRequest.creationDate = '%s' % pub.pendingClosedTime

        if pub.pendingClosed: # Give url of pending contributions
            guindex_alerts_msg.pubClosedAlertRequest.uri = UserProfileUtils.getProjectUri(httpRequest)

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Closed Alert Request message")
            raise Exception("Failed to serialize Pub Closed Alert Request message")

        self.sendMessage(message_string)

    def sendPubNotServingGuinnessAlertRequest(self, pub, httpRequest):

        self.logger.info("Sending Pub Not Serving Guinness Alert Request")

        # Create Pub Not Serving Guinness Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.username     = pub.pendingNotServingGuinnessContributor.user.username
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.approved     = not pub.pendingNotServingGuinness
        guindex_alerts_msg.pubNotServingGuinnessAlertRequest.creationDate = '%s' % pub.pendingNotServingGuinnessTime

        if pub.pendingNotServingGuinness: # Give url of pending contributions
            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.uri = UserProfileUtils.getProjectUri(httpRequest)

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Not Serving Guinness Alert Request message")
            raise Exception("Failed to serialize Pub Not Serving Guinness Alert Request message")

        self.sendMessage(message_string)

    def sendNewGuinnessDecisionAlertRequest(self, guinness, reason = None):

        self.logger.info("Sending New Guinness Decision Alert Request")

        # Create New Guinness Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.newGuinnessDecisionAlertRequest.creatorId    = str(guinness.creator.id)
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.approved     = guinness.approved # Approved if approved field is true
        guindex_alerts_msg.newGuinnessDecisionAlertRequest.creationDate = '%s' % guinness.creationDate

        if reason:
            guindex_alerts_msg.newGuinnessDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Guinness Decision Alert Request message")
            raise Exception("Failed to serialize New Guinness Decision Alert Request message")

        self.sendMessage(message_string)

    def sendNewPubDecisionAlertRequest(self, pub, reason = None):

        self.logger.info("Sending New Pub Decision Alert Request")

        # Create New Pub Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.newPubDecisionAlertRequest.creatorId    = str(pub.pendingApprovalContributor.id)
        guindex_alerts_msg.newPubDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.newPubDecisionAlertRequest.latitude     = str(pub.latitude)
        guindex_alerts_msg.newPubDecisionAlertRequest.longitude    = str(pub.longitude)
        guindex_alerts_msg.newPubDecisionAlertRequest.approved     = not pub.pendingApproval and not pub.pendingApprovalRejected
        guindex_alerts_msg.newPubDecisionAlertRequest.creationDate = '%s' % pub.pendingApprovalTime

        if reason:
            guindex_alerts_msg.newPubDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize New Pub Decision Alert Request message")
            raise Exception("Failed to serialize New Pub Decision Alert Request message")

        self.sendMessage(message_string)

    def sendPubClosedDecisionAlertRequest(self, pub, reason = None):

        self.logger.info("Sending Pub Closed Decision Alert Request")

        # Create Pub Closed Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubClosedDecisionAlertRequest.creatorId    = str(pub.pendingClosedContributor.id)
        guindex_alerts_msg.pubClosedDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubClosedDecisionAlertRequest.approved     = pub.closed # Approved if pub now marked as closed
        guindex_alerts_msg.pubClosedDecisionAlertRequest.creationDate = '%s' % pub.pendingClosedTime

        if reason:
            guindex_alerts_msg.pubClosedDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Closed Decision Alert Request message")
            raise Exception("Failed to serialize Pub Closed Decision Alert Request message")

        self.sendMessage(message_string)

    def sendPubNotServingGuinnessDecisionAlertRequest(self, pub, reason = None):

        self.logger.info("Sending Pub Not Serving Guinness Decision Alert Request")

        # Create Pub Not Serving Guinness Decision Alert Request message
        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.creatorId    = str(pub.pendingNotServingGuinnessContributor.id)
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.approved     = not pub.servingGuinness # Approved if pub now marked as not serving Guinness
        guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.creationDate = '%s' % pub.pendingNotServingGuinnessTime

        if reason:
            guindex_alerts_msg.pubNotServingGuinnessDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            self.logger.error("Failed to serialize Pub Not Serving Guinness Decision Alert Request message")
            raise Exception("Failed to serialize Pub Not Serving Guinness Decision Alert Request message")

        self.sendMessage(message_string)
