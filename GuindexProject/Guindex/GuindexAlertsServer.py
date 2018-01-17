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

            self._handlePubClosedDecisionAlertRequest(msg)

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

                self.logger.debug("Sending Approved New Guinness Alert email to UserProfile %s", user_profile)

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

                self.logger.debug("Sending Approved New Guinness Alert telegram to UserProfile %s", user_profile)

                telegram_message = "The following Guinness price has been added to the Guindex:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.newGuinnessAlertRequest.pub
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

                telegram_message = "The following Guinness price has been submitted to the Guindex by a non-staff member:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.newGuinnessAlertRequest.pub
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

    def _handleApprovedNewPubAlertRequest(self, message, userProfileToIgnore = None):

        self.logger.info("Handling Approved New Pub Alert Request")

        for user_profile in UserProfile.objects.all():

            # In case of reecently approved submission, don't alert that contributor
            if user_profile == userProfileToIgnore:
                self.logger.debug("Skipping creator of recently approved Pub: UserProfile %s", user_profile)
                continue

            self.logger.debug("Processing Approved New Pub Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Approved New Pub Alert email to UserProfile %s", user_profile)

                new_pub_dict = {}

                new_pub_dict['name']         = message.newPubAlertRequest.pub
                new_pub_dict['latitude']     = message.newPubAlertRequest.latitude
                new_pub_dict['longitude']    = message.newPubAlertRequest.longitude
                new_pub_dict['creator']      = message.newPubAlertRequest.username
                new_pub_dict['creationDate'] = message.newPubAlertRequest.creationDate

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['new_pub']                 = new_pub_dict

                try:
                    html_content = render_to_string('approved_new_pub_alert_email.html', data)
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

                self.logger.debug("Sending Approved New Pub Alert telegram to UserProfile %s", user_profile)

                telegram_message = "The following pub has been added to the Guindex:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.newPubAlertRequest.pub
                telegram_message += "Latitude: %s\n"    % message.newPubAlertRequest.latitude
                telegram_message += "Longitude: %s\n"   % message.newPubAlertRequest.longitude
                telegram_message += "Contributor: %s\n" % message.newPubAlertRequest.username
                telegram_message += "Time: %s\n"        % message.newPubAlertRequest.creationDate

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleUnapprovedNewPubAlertRequest(self, message):

        self.logger.info("Handling Unapproved New Pub Alert Request")

        for user_profile in UserProfile.objects.all():

            if not user_profile.user.is_staff:
                continue

            self.logger.debug("Processing Unapproved New Pub Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Unapproved New Pub Alert email to UserProfile %s", user_profile)

                new_pub_dict = {}

                new_pub_dict['name']         = message.newPubAlertRequest.pub
                new_pub_dict['latitude']     = message.newPubAlertRequest.latitude
                new_pub_dict['longitude']    = message.newPubAlertRequest.longitude
                new_pub_dict['creator']      = message.newPubAlertRequest.username
                new_pub_dict['creationDate'] = message.newPubAlertRequest.creationDate

                if message.newPubAlertRequest.HasField('uri'):
                    new_pub_dict['pendingContributionsUrl'] = message.newPubAlertRequest.uri + "/pending_contributions/"
                else:
                    new_pub_dict['pendingContributionsUrl'] = "http://guindex.ie/pending_contributions/"

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['new_pub']                 = new_pub_dict

                try:
                    html_content = render_to_string('unapproved_new_pub_alert_email.html', data)
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

                telegram_message = "The following pub has been submitted to the Guindex by a non-staff member:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.newPubAlertRequest.pub
                telegram_message += "Latitude: %s\n"    % message.newPubAlertRequest.latitude
                telegram_message += "Longitude: %s\n"   % message.newPubAlertRequest.longitude
                telegram_message += "Contributor: %s\n" % message.newPubAlertRequest.username
                telegram_message += "Time: %s\n\n"      % message.newPubAlertRequest.creationDate

                if message.newPubAlertRequest.HasField('uri'):
                    pending_contributions_url = message.newPubAlertRequest.uri + "/pending_contributions/"
                else:
                    pending_contributions_url = "http://guindex.ie/pending_contributions/"

                telegram_message += "Please visit %s to approve the submission." % pending_contributions_url

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleApprovedPubCloseAlertRequest(self, message, userProfileToIgnore = None):

        self.logger.info("Handling Approved Pub Close Alert Request")

        for user_profile in UserProfile.objects.all():

            # In case of reecently approved submission, don't alert that contributor
            if user_profile == userProfileToIgnore:
                self.logger.debug("Skipping creator of recently closed Pub: UserProfile %s", user_profile)
                continue

            self.logger.debug("Processing Approved Pub Close Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Approved Pub Close Alert email to UserProfile %s", user_profile)

                closed_pub_dict = {}

                closed_pub_dict['name']         = message.pubClosedAlertRequest.pub
                closed_pub_dict['creator']      = message.pubClosedAlertRequest.username
                closed_pub_dict['creationDate'] = message.pubClosedAlertRequest.creationDate

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['closed_pub']              = closed_pub_dict

                try:
                    html_content = render_to_string('approved_pub_closed_alert_email.html', data)
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

                self.logger.debug("Sending Approved Pub Close Alert telegram to UserProfile %s", user_profile)

                telegram_message = "The following Pub has been marked as closed:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.pubClosedAlertRequest.pub
                telegram_message += "Contributor: %s\n" % message.pubClosedAlertRequest.username
                telegram_message += "Time: %s\n"        % message.pubClosedAlertRequest.creationDate

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleUnapprovedPubCloseAlertRequest(self, message):

        self.logger.info("Handling Unapproved Pub Close Alert Request")

        for user_profile in UserProfile.objects.all():

            if not user_profile.user.is_staff:
                continue

            self.logger.debug("Processing Unapproved Pub Close Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Unapproved Pub Close Alert email to UserProfile %s", user_profile)

                closed_pub_dict = {}

                closed_pub_dict['name']         = message.pubClosedAlertRequest.pub
                closed_pub_dict['creator']      = message.pubClosedAlertRequest.username
                closed_pub_dict['creationDate'] = message.pubClosedAlertRequest.creationDate

                if message.pubClosedAlertRequest.HasField('uri'):
                    closed_pub_dict['pendingContributionsUrl'] = message.pubClosedAlertRequest.uri + "/pending_contributions/"
                else:
                    closed_pub_dict['pendingContributionsUrl'] = "http://guindex.ie/pending_contributions/"

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['closed_pub']              = closed_pub_dict

                try:
                    html_content = render_to_string('unapproved_pub_closed_alert_email.html', data)
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

                self.logger.debug("Sending Unapproved Pub Close Alert Telegram to UserProfile %s", user_profile)

                telegram_message = "The following Pub has been marked as closed by a non-staff member:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.pubClosedAlertRequest.pub
                telegram_message += "Contributor: %s\n" % message.pubClosedAlertRequest.username
                telegram_message += "Time: %s\n\n"      % message.pubClosedAlertRequest.creationDate

                if message.pubClosedAlertRequest.HasField('uri'):
                    pending_contributions_url = message.pubClosedAlertRequest.uri + "/pending_contributions/"
                else:
                    pending_contributions_url = "http://guindex.ie/pending_contributions/"

                telegram_message += "Please visit %s to approve the submission." % pending_contributions_url

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleApprovedPubNotServingGuinnessAlertRequest(self, message, userProfileToIgnore = None):

        self.logger.info("Handling Approved Pub Not Serving Guinness Alert Request")

        for user_profile in UserProfile.objects.all():

            # In case of reecently approved submission, don't alert that contributor
            if user_profile == userProfileToIgnore:
                self.logger.debug("Skipping creator of not serving Guinness Pub: UserProfile %s", user_profile)
                continue

            self.logger.debug("Processing Approved Pub Not Serving Guinness Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Approved Pub Not Serving Guinness email to UserProfile %s", user_profile)

                pub_dict = {}

                pub_dict['name']         = message.pubNotServingGuinnessAlertRequest.pub
                pub_dict['creator']      = message.pubNotServingGuinnessAlertRequest.username
                pub_dict['creationDate'] = message.pubNotServingGuinnessAlertRequest.creationDate

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['pub']                     = pub_dict

                try:
                    html_content = render_to_string('approved_pub_not_serving_guinness_alert_email.html', data)
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

                self.logger.debug("Sending Pub Not Serving Guinness Alert telegram to UserProfile %s", user_profile)

                telegram_message = "The following Pub has been marked as not serving Guinness:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.pubNotServingGuinnessAlertRequest.pub
                telegram_message += "Contributor: %s\n" % message.pubNotServingGuinnessAlertRequest.username
                telegram_message += "Time: %s\n"        % message.pubNotServingGuinnessAlertRequest.creationDate

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleUnapprovedPubNotServingGuinnessAlertRequest(self, message):

        self.logger.info("Handling Unapproved Pub Not SErving Guinness Alert Request")

        for user_profile in UserProfile.objects.all():

            if not user_profile.user.is_staff:
                continue

            self.logger.debug("Processing Unapproved Pub Not Serving Guinness Alerts for UserProfile %s", user_profile)

            if user_profile.usingEmailAlerts:

                self.logger.debug("Sending Unapproved Pub Not Serving Guinness Alert email to UserProfile %s", user_profile)

                pub_dict = {}

                pub_dict['name']         = message.pubNotServingGuinnessAlertRequest.pub
                pub_dict['creator']      = message.pubNotServingGuinnessAlertRequest.username
                pub_dict['creationDate'] = message.pubNotServingGuinnessAlertRequest.creationDate

                if message.pubNotServingGuinnessAlertRequest.HasField('uri'):
                    pub_dict['pendingContributionsUrl'] = message.pubNotServingGuinnessAlertRequest.uri + "/pending_contributions/"
                else:
                    pub_dict['pendingContributionsUrl'] = "http://guindex.ie/pending_contributions/"

                data = {}

                data['user_profile']            = user_profile
                data['user_profile_parameters'] = UserProfileParameters.getParameters()
                data['pub']                     = pub_dict

                try:
                    html_content = render_to_string('unapproved_pub_not_serving_guinness_alert_email.html', data)
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

                self.logger.debug("Sending Unapproved Pub Not Serving Guinness Alert Telegram to UserProfile %s", user_profile)

                telegram_message = "The following Pub has been marked as not serving Guinness by a non-staff member:\n\n"

                telegram_message += "Pub Name: %s\n"    % message.pubNotServingGuinnessAlertRequest.pub
                telegram_message += "Contributor: %s\n" % message.pubNotServingGuinnessAlertRequest.username
                telegram_message += "Time: %s\n\n"      % message.pubNotServingGuinnessAlertRequest.creationDate

                if message.pubNotServingGuinnessAlertRequest.HasField('uri'):
                    pending_contributions_url = message.pubNotServingGuinnessAlertRequest.uri + "/pending_contributions/"
                else:
                    pending_contributions_url = "http://guindex.ie/pending_contributions/"

                telegram_message += "Please visit %s to approve the submission." % pending_contributions_url

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

    def _handleNewGuinnessDecisionAlertRequest(self, message):

        self.logger.info("Received New Guinness Decision Alert Request")

        try:
            user_profile = UserProfile.objects.get(id = int(message.newGuinnessDecisionAlertRequest.creatorId))
        except:
            self.logger.error("Failed to find UserProfile with id %s", message.newGuinnessDecisionAlertRequest.creatorId)
            return

        if user_profile.usingEmailAlerts:

            self.logger.debug("Sending New Guinness Decision Alert email to UserProfile %s", user_profile)

            new_guinness_dict = {}

            new_guinness_dict['name']         = message.newGuinnessDecisionAlertRequest.pub
            new_guinness_dict['price']        = message.newGuinnessDecisionAlertRequest.price
            new_guinness_dict['creationDate'] = message.newGuinnessDecisionAlertRequest.creationDate
            new_guinness_dict['approved']     = "approved" if message.newGuinnessDecisionAlertRequest.approved else "rejected"

            if message.newGuinnessDecisionAlertRequest.HasField('reason'):
                new_guinness_dict['reason'] = message.newGuinnessDecisionAlertRequest.reason

            data = {}

            data['user_profile']            = user_profile
            data['user_profile_parameters'] = UserProfileParameters.getParameters()
            data['new_guinness']            = new_guinness_dict

            try:
                html_content = render_to_string('new_guinness_decision_alert_email.html', data)
                user_profile.user.email_user('Guindex Submission Decision Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to %s", user_profile)

        if user_profile.telegramuser:

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending New Guinness Decision Alert Telegram to UserProfile %s", user_profile)

                decision = "approved" if message.newGuinnessDecisionAlertRequest.approved else "rejected"

                telegram_message = "Your below Guinness price submission has been %s:\n\n" % decision

                telegram_message += "Pub Name: %s\n" % message.newGuinnessDecisionAlertRequest.pub
                telegram_message += "Price: %s\n"    % message.newGuinnessDecisionAlertRequest.price[1:]
                telegram_message += "Time: %s\n"     % message.newGuinnessDecisionAlertRequest.creationDate

                if message.newGuinnessDecisionAlertRequest.HasField('reason'):
                    telegram_message += "Reason: %s\n" % message.newGuinnessDecisionAlertRequest.reason

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

        else:
            self.logger.info("UserProfile %s has not created telegramuser yet", user_profile)

        # Send new approved Guinness alert request if approved
        if message.newGuinnessDecisionAlertRequest.approved:

            guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

            guindex_alerts_msg.newGuinnessAlertRequest.pub          = message.newGuinnessDecisionAlertRequest.pub
            guindex_alerts_msg.newGuinnessAlertRequest.price        = message.newGuinnessDecisionAlertRequest.price
            guindex_alerts_msg.newGuinnessAlertRequest.username     = user_profile.user.username
            guindex_alerts_msg.newGuinnessAlertRequest.approved     = True
            guindex_alerts_msg.newGuinnessAlertRequest.creationDate = '%s' % message.newGuinnessDecisionAlertRequest.creationDate

            try:
                self._handleApprovedNewGuinnessAlertRequest(guindex_alerts_msg, user_profile)
            except:
                self.logger.error("An error occured informing other users of approval decision")

    def _handleNewPubDecisionAlertRequest(self, message):

        self.logger.info("Received New Pub Decision Alert Request")

        try:
            user_profile = UserProfile.objects.get(id = int(message.newPubDecisionAlertRequest.creatorId))
        except:
            self.logger.error("Failed to find UserProfile with id %s", message.newPubDecisionAlertRequest.creatorId)
            return

        if user_profile.usingEmailAlerts:

            self.logger.debug("Sending New Pub Decision Alert email to UserProfile %s", user_profile)

            new_pub_dict = {}

            new_pub_dict['name']         = message.newPubDecisionAlertRequest.pub
            new_pub_dict['latitude']     = message.newPubDecisionAlertRequest.latitude
            new_pub_dict['longitude']    = message.newPubDecisionAlertRequest.longitude
            new_pub_dict['creationDate'] = message.newPubDecisionAlertRequest.creationDate
            new_pub_dict['approved']     = "approved" if message.newPubDecisionAlertRequest.approved else "rejected"

            if message.newPubDecisionAlertRequest.HasField('reason'):
                new_pub_dict['reason'] = message.newPubDecisionAlertRequest.reason

            data = {}

            data['user_profile']            = user_profile
            data['user_profile_parameters'] = UserProfileParameters.getParameters()
            data['new_pub']                 = new_pub_dict

            try:
                html_content = render_to_string('new_pub_decision_alert_email.html', data)
                user_profile.user.email_user('Guindex Submission Decision Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to %s", user_profile)

        if user_profile.telegramuser:

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending New Pub Decision Alert Telegram to UserProfile %s", user_profile)

                decision = "approved" if message.newPubDecisionAlertRequest.approved else "rejected"

                telegram_message = "Your below new Pub submission has been %s:\n\n" % decision

                telegram_message += "Pub Name: %s\n"  % message.newPubDecisionAlertRequest.pub
                telegram_message += "Latitude: %s\n"  % message.newPubDecisionAlertRequest.latitude
                telegram_message += "Longitude: %s\n" % message.newPubDecisionAlertRequest.longitude
                telegram_message += "Time: %s\n"      % message.newPubDecisionAlertRequest.creationDate

                if message.newPubDecisionAlertRequest.HasField('reason'):
                    telegram_message += "Reason: %s\n" % message.newPubDecisionAlertRequest.reason

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

        else:
            self.logger.info("UserProfile %s has not created telegramuser yet", user_profile)

        # Send new approved Pub alert request if approved
        if message.newPubDecisionAlertRequest.approved:

            guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

            guindex_alerts_msg.newPubAlertRequest.pub          = message.newPubDecisionAlertRequest.pub
            guindex_alerts_msg.newPubAlertRequest.username     = user_profile.user.username
            guindex_alerts_msg.newPubAlertRequest.latitude     = message.newPubDecisionAlertRequest.latitude
            guindex_alerts_msg.newPubAlertRequest.longitude    = message.newPubDecisionAlertRequest.longitude
            guindex_alerts_msg.newPubAlertRequest.approved     = True
            guindex_alerts_msg.newPubAlertRequest.creationDate = '%s' % message.newPubDecisionAlertRequest.creationDate

            try:
                self._handleApprovedNewPubAlertRequest(guindex_alerts_msg, user_profile)
            except:
                self.logger.error("An error occured informing other users of approval decision")

    def _handlePubClosedDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Closed Decision Alert Request")

        try:
            user_profile = UserProfile.objects.get(id = int(message.pubClosedDecisionAlertRequest.creatorId))
        except:
            self.logger.error("Failed to find UserProfile with id %s", message.pubClosedDecisionAlertRequest.creatorId)
            return

        if user_profile.usingEmailAlerts:

            self.logger.debug("Sending Pub Closed Decision Alert email to UserProfile %s", user_profile)

            closed_pub_dict = {}

            closed_pub_dict['name']         = message.pubClosedDecisionAlertRequest.pub
            closed_pub_dict['creationDate'] = message.pubClosedDecisionAlertRequest.creationDate
            closed_pub_dict['approved']     = "approved" if message.pubClosedDecisionAlertRequest.approved else "rejected"

            if message.pubClosedDecisionAlertRequest.HasField('reason'):
                closed_pub_dict['reason'] = message.pubClosedDecisionAlertRequest.reason

            data = {}

            data['user_profile']            = user_profile
            data['user_profile_parameters'] = UserProfileParameters.getParameters()
            data['closed_pub']              = closed_pub_dict

            try:
                html_content = render_to_string('pub_closed_decision_alert_email.html', data)
                user_profile.user.email_user('Guindex Submission Decision Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to %s", user_profile)

        if user_profile.telegramuser:

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending Pub Closed Decision Alert Telegram to UserProfile %s", user_profile)

                decision = "approved" if message.pubClosedDecisionAlertRequest.approved else "rejected"

                telegram_message = "Your below closed pub submission has been %s:\n\n" % decision

                telegram_message += "Pub Name: %s\n" % message.pubClosedDecisionAlertRequest.pub
                telegram_message += "Time: %s\n"     % message.pubClosedDecisionAlertRequest.creationDate

                if message.pubClosedDecisionAlertRequest.HasField('reason'):
                    telegram_message += "Reason: %s\n" % message.pubClosedDecisionAlertRequest.reason

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

        else:
            self.logger.info("UserProfile %s has not created telegramuser yet", user_profile)

        # Send new approved Pub closed alert request if approved
        if message.pubClosedDecisionAlertRequest.approved:

            guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

            guindex_alerts_msg.pubClosedAlertRequest.pub          = message.pubClosedDecisionAlertRequest.pub
            guindex_alerts_msg.pubClosedAlertRequest.username     = user_profile.user.username
            guindex_alerts_msg.pubClosedAlertRequest.approved     = True
            guindex_alerts_msg.pubClosedAlertRequest.creationDate = '%s' % message.pubClosedDecisionAlertRequest.creationDate

            try:
                self._handleApprovedPubCloseAlertRequest(guindex_alerts_msg, user_profile)
            except:
                self.logger.error("An error occured informing other users of approval decision")

    def _handlePubNotServingGuinnessDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Not Serving Guinness Decision Alert Request")

        try:
            user_profile = UserProfile.objects.get(id = int(message.pubNotServingGuinnessDecisionAlertRequest.creatorId))
        except:
            self.logger.error("Failed to find UserProfile with id %s", message.pubNotServingGuinnessDecisionAlertRequest.creatorId)
            return

        if user_profile.usingEmailAlerts:

            self.logger.debug("Sending Pub Not Serving Guinness Decision Alert email to UserProfile %s", user_profile)

            pub_dict = {}

            pub_dict['name']         = message.pubNotServingGuinnessDecisionAlertRequest.pub
            pub_dict['creationDate'] = message.pubNotServingGuinnessDecisionAlertRequest.creationDate
            pub_dict['approved']     = "approved" if message.pubNotServingGuinnessDecisionAlertRequest.approved else "rejected"

            if message.pubNotServingGuinnessDecisionAlertRequest.HasField('reason'):
                pub_dict['reason'] = message.pubNotServingGuinnessDecisionAlertRequest.reason

            data = {}

            data['user_profile']            = user_profile
            data['user_profile_parameters'] = UserProfileParameters.getParameters()
            data['pub']                     = pub_dict

            try:
                html_content = render_to_string('pub_not_serving_guinness_decision_alert_email.html', data)
                user_profile.user.email_user('Guindex Submission Decision Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to %s", user_profile)

        if user_profile.telegramuser:

            if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:

                self.logger.debug("Sending Pub Not Serving Guinness Decision Alert Telegram to UserProfile %s", user_profile)

                decision = "approved" if message.pubNotServingGuinnessDecisionAlertRequest.approved else "rejected"

                telegram_message = "Your below pub not serving Guinness submission has been %s:\n\n" % decision

                telegram_message += "Pub Name: %s\n" % message.pubNotServingGuinnessDecisionAlertRequest.pub
                telegram_message += "Time: %s\n"     % message.pubNotServingGuinnessDecisionAlertRequest.creationDate

                if message.pubNotServingGuinnessDecisionAlertRequest.HasField('reason'):
                    telegram_message += "Reason: %s\n" % message.pubNotServingGuinnessDecisionAlertRequest.reason

                try:
                    GuindexBot.sendMessage(telegram_message, user_profile.telegramuser.chatId)
                except:
                    self.logger.error("Failed to send Telegram to %s", user_profile)

        else:
            self.logger.info("UserProfile %s has not created telegramuser yet", user_profile)

        # Send new approved Pub closed alert request if approved
        if message.pubNotServingGuinnessDecisionAlertRequest.approved:

            guindex_alerts_msg = GuindexAlertsIf.GuindexAlertsIfMessage()

            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.pub          = message.pubNotServingGuinnessDecisionAlertRequest.pub
            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.username     = user_profile.user.username
            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.approved     = True
            guindex_alerts_msg.pubNotServingGuinnessAlertRequest.creationDate = '%s' % message.pubNotServingGuinnessDecisionAlertRequest.creationDate

            try:
                self._handleApprovedPubNotServingGuinnessAlertRequest(guindex_alerts_msg, user_profile)
            except:
                self.logger.error("An error occured informing other users of approval decision")
