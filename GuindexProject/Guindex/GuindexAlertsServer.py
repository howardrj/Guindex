from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from django.template.loader import render_to_string

from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf
from Guindex.GuindexBot import GuindexBot

from UserProfile.models import UserProfile
from UserProfile.UserProfileParameters import UserProfileParameters


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

        if msg.HasField('newGuinnessAlertRequest'):

            self._handleNewGuinnessAlertRequest(msg)

        elif msg.HasField('newPubAlertRequest'):

            self._handleNewPubAlertRequest(msg)

        elif msg.HasField('pubClosedAlertRequest'):

            self._handlePubClosedAlertRequest(msg)

        elif msg.HasField('pubNotServingGuinnessAlertRequest'):

            self._handlePubNotServingGuinnessAlertRequest(msg)

        elif msg.HasField('newGuinnessDecisionAlertRequest'):

            self._handleNewGuinnessDecisionAlertRequest(msg)

        elif msg.HasField('newPubDecisionAlertRequest'):

            self._handleNewPubDecisionAlertRequest(msg)

        elif msg.HasField('pubClosedDecisionAlertRequest'):

            self._handlePubClosediDecisionAlertRequest(msg)

        elif msg.HasField('pubNotServingGuinnessDecisionAlertRequest'):

            self._handlePubNotServingGuinnessDecisionAlertRequest(msg)

        else:
            self.logger.error("Received unknown message type")

    def _handleNewGuinnessAlertRequest(self, message):

        self.logger.info("Received New Guinness Alert Request")

        if message.newGuinnessAlertRequest.approved:
            self.logger.info("Guinness is approved")
            self._handleApprovedNewGuinnessAlertRequest(message)
        else:
            self.logger.info("Guinness is not approved")
            self._handleUnapprovedNewGuinnessAlertRequest(message)

    def _handleNewPubAlertRequest(self, message):

        self.logger.info("Received New Pub Alert Request")

        if message.newPubAlertRequest.approved:
            self.logger.info("Pub is approved")
            self._handleApprovedNewPubAlertRequest(message)
        else:
            self.logger.info("Pub is not approved")
            self._handleUnapprovedNewPubAlertRequest(message)

    def _handlePubClosedAlertRequest(self, message):

        self.logger.info("Received Pub Closed Alert Request")

        if message.pubClosedAlertRequest.approved:
            self.logger.info("Pub closure is approved")
            self._handleApprovedPubCloseAlertRequest(message)
        else:
            self.logger.info("Pub closure is not approved")
            self._handleUnapprovedPubCloseAlertRequest(message)

    def _handlePubNotServingGuinnessAlertRequest(self, message):

        self.logger.info("Received Pub Not Serving Guinness Alert Request")

        if message.pubNotServingGuinnessAlertRequest.approved:
            self.logger.info("Pub not serving Guinness is approved")
            self._handleApprovedPubNotServingGuinnessAlertRequest(message)
        else:
            self.logger.info("Pub not serving Guinness is not approved")
            self._handleUnapprovedPubNotServingGuinnessAlertRequest(message)

    def _handleApprovedNewGuinnessAlertRequest(self, message, userProfileToIgnore = None):

        self.logger.info("Handling Approved New Guinness Alert Request")

        for user_profile in UserProfile.objects.all():

            # In case of reecently approved submission, don't alert that contributor
            if user_profile == userProfileToIgnore:
                self.logger.debug("Skipping creator of recently approved Guinness: UserProfile %s", user_profile)
                continue

            self.logger.debug("Processing Approved New Guinness Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Approved New Guinness Alerts email to UserProfile %s", user_profile)

                new_guinness_dict = {}

                new_guinness_dict['name']         = message.newGuinnessAlertRequest.pub
                new_guinness_dict['price']        = message.newGuinnessAlertRequest.price
                new_guinness_dict['creator']      = message.newGuinnessAlertRequest.username
                new_guinness_dict['creationDate'] = message.newGuinnessAlertRequest.creationDate

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['new_guinness']            = new_guinness_dict

                try:
                    html_content = render_to_string('approved_new_guinness_alert_email.html', data)
                except:
                    self.logger.error("Failed to render email to string")
                    continue

                try:
                    user_profile.user.email_user('New Guindex Submission Alert', html_content, None, html_message = html_content)
                except:
                    self.logger.error("Failed to send email to %s", user_profile)
                    continue

            if not user_profile.telegramuser:
                self.logger.debug("UserProfile %s does not have a TelegramUser", user_profile)
                continue

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending Approved New Guinness Alerts telegram to UserProfile %s", user_profile)

                telegram_message = "The following event has been added to the Guindex:\n\n"

                telegram_message += "Pub: %s\n"         % message.newGuinnessAlertRequest.pub
                telegram_message += "Price: %s\n"       % message.newGuinnessAlertRequest.price[1:]
                telegram_message += "Contributor: %s\n" % message.newGuinnessAlertRequest.username
                telegram_message += "Time: %s\n"        % message.newGuinnessAlertRequest.creationDate

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleUnapprovedNewGuinnessAlertRequest(self, message):

        self.logger.info("Handling Unapproved New Guinness Alert Request")

        for user_profile in UserProfile.objects.all():

            if not user_profile.user.is_staff:
                continue

            self.logger.debug("Processing Unapproved New Guinness Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Unapproved New Guinness Alert email to UserProfile %s", user_profile)

                new_guinness_dict = {}

                new_guinness_dict['name']         = message.newGuinnessAlertRequest.pub
                new_guinness_dict['price']        = message.newGuinnessAlertRequest.price[1:]
                new_guinness_dict['creator']      = message.newGuinnessAlertRequest.username
                new_guinness_dict['creationDate'] = message.newGuinnessAlertRequest.creationDate

                if message.newGuinnessAlertRequest.HasField('uri'):
                    new_guinness_dict['pendingContributionsUrl'] = message.newGuinnessAlertRequest.uri + "/pending_contributions/"
                else:
                    new_guinness_dict['pendingContributionsUrl'] = "http://guindex.ie/pending_contributions/"

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['new_guinness']            = new_guinness_dict

                try:
                    html_content = render_to_string('unapproved_new_guinness_alert_email.html', data)
                except:
                    self.logger.error("Failed to render email to string")
                    continue

                try:
                    user_profile.user.email_user('Pending Guindex Submission Alert', html_content, None, html_message = html_content)
                except:
                    self.logger.error("Failed to send email to %s", user_profile)
                    continue

            if not user_profile.telegramuser:
                self.logger.debug("UserProfile %s does not have a TelegramUser", user_profile)
                continue

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending Unapproved New Guinness Alert Telegram to UserProfile %s", user_profile)

                telegram_message = "The following event has been submitted to the Guindex by a non-staff member:\n\n"

                telegram_message += "Pub: %s\n"         % message.newGuinnessAlertRequest.pub
                telegram_message += "Price: %s\n"       % message.newGuinnessAlertRequest.price[1:]
                telegram_message += "Contributor: %s\n" % message.newGuinnessAlertRequest.username
                telegram_message += "Time: %s\n\n"      % message.newGuinnessAlertRequest.creationDate

                if message.newGuinnessAlertRequest.HasField('uri'):
                    pending_contributions_url = message.newGuinnessAlertRequest.uri + "/pending_contributions/"
                else:
                    pending_contributions_url = "http://guindex.ie/pending_contributions/"

                telegram_message += "Please visit %s to approve the submission." % pending_contributions_url

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)
