# -*- coding: utf-8 -*-
import logging
import json

from Guindex.GuindexClient import GuindexClient
from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf
from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


class GuindexAlertsClient(GuindexClient):

    def __init__(self):

        logger.debug("Creating GuindexAlerts client")

        super(GuindexAlertsClient, self).__init__('Alerts',
                                                  GuindexParameters.ALERTS_LISTEN_IP,
                                                  GuindexParameters.ALERTS_LISTEN_PORT)

    def sendGuinnessCreateAlertRequest(self, guinness, approved):

        logger.info("Sending Guinnness Create Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.guinnessCreateAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.guinnessCreateAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.guinnessCreateAlertRequest.username     = guinness.creator.username
        guindex_alerts_msg.guinnessCreateAlertRequest.creationDate = '%s' % guinness.creationDate # TODO Display this nicer
        guindex_alerts_msg.guinnessCreateAlertRequest.approved     = approved

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Guinness Create Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)

    def sendGuinnessPendingCreateDecisionAlertRequest(self, guinness, approved, reason):

        logger.info("Sending Guinness Pending Create Decision Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        price = '€%.2f' % guinness.price

        guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.pub          = guinness.pub.name
        guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.price        = price.decode('utf-8')
        guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.userId       = guinness.creator.id
        guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.creationDate = '%s' % guinness.creationDate # TODO Display this nicer
        guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.approved     = approved

        if not approved and reason:
            guindex_alerts_msg.guinnessPendingCreateDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Guinness Pending Create Decision Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)

    def sendPubCreateAlertRequest(self, pub, approved):

        logger.info("Sending Pub Create Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubCreateAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubCreateAlertRequest.latitude     = str(pub.latitude)
        guindex_alerts_msg.pubCreateAlertRequest.longitude    = str(pub.longitude)
        guindex_alerts_msg.pubCreateAlertRequest.username     = pub.creator.username
        guindex_alerts_msg.pubCreateAlertRequest.creationDate = '%s' % pub.creationDate # TODO Display this nicer
        guindex_alerts_msg.pubCreateAlertRequest.approved     = approved

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Pub Create Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)

    def sendPubPatchAlertRequest(self, pub, contributor, changedFields, approved):

        logger.info("Sending Pub Create Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubPatchAlertRequest.pub           = pub.name
        guindex_alerts_msg.pubPatchAlertRequest.username      = contributor.username
        guindex_alerts_msg.pubPatchAlertRequest.changedFields = json.dump(changedFields) # Encode as JSON
        guindex_alerts_msg.pubPatchAlertRequest.approved      = approved

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Pub Patch Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)

    def sendPubPendingCreateDecisionAlertRequest(self, pub, approved, reason):

        logger.info("Sending Pub Pending Create Decision Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.latitude     = str(pub.latitude)
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.longitude    = str(pub.longitude)
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.userId       = pub.creator.id
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.creationDate = '%s' % pub.creationDate # TODO Display this nicer
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.approved     = approved

        if not approved and reason:
            guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Pub Pending Create Decision Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)

    def sendPubPendingPatchDecisionAlertRequest(self, pub, approved, reason):

        logger.info("Sending Pub Pending Patch Decision Alert Request")

        guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

        guindex_alerts_msg.pubPendingPatchDecisionAlertRequest.pub          = pub.name
        guindex_alerts_msg.pubPendingPatchDecisionAlertRequest.userId       = pub.creator.id
        guindex_alerts_msg.pubPendingPatchDecisionAlertRequest.creationDate = '%s' % pub.creationDate # TODO Display this nicer
        guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.approved    = approved

        if not approved and reason:
            guindex_alerts_msg.pubPendingCreateDecisionAlertRequest.reason = reason

        try:
            message_string = guindex_alerts_msg.SerializeToString()
        except:
            error_message = "Failed to serialize Pub Pending Patch Decision Alert Request message"
            logger.error(error_message)
            raise Exception(error_message)

        self.sendMessage(message_string)
