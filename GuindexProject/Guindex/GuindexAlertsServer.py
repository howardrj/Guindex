import simplejson as json
from collections import OrderedDict
from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from django.template.loader import render_to_string
from django.contrib.auth.models import User

from Guindex import GuindexAlertsIf_pb2 as GuindexAlertsIf
from Guindex.GuindexBot import GuindexBot
from Guindex.models import GuindexUser

from TelegramUser import TelegramUserUtils


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

    def _validateAlertsSettings(self, user):

        self.logger.debug("Validating alerts settings for user %d", user.id)

        if not hasattr(user, 'guindexuser'):

            self.logger.info("User %d does not have a GuindexUser. Creating one", user.id)

            guindexuser = GuindexUser()

            guindexuser.user = user
            guindexuser.save()

        if not hasattr(user, 'telegramuser'):

            self.logger.info("User %d does not have a TelegramUser. Creating one", user.id)

            TelegramUserUtils.createNewTelegramUser(user)

    def _formatChangedFieldsTelegram(self, changedFields):

        updates        = json.loads(changedFields)
        updates_string = ""

        updates_string += "\n"

        for key in updates:
            updates_string += "    " + str(key) + ": " + str(updates[key][0]) + " --> " + str(updates[key][1]) + "\n"

        return updates_string

    def _formatChangedFieldsEmail(self, changedFields):

        updates        = json.loads(changedFields)
        updates_string = ""

        updates_string += "<br/>"

        for key in updates:
            updates_string += "    " + str(key) + ": " + str(updates[key][0]) + " --> " + str(updates[key][1]) + "<br/>"
        
        return updates_string

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

        for user in User.objects.all():

            self.logger.debug("Processing Guinness Create Alert Request for user %d", user.id)

            self._validateAlertsSettings(user)

            if user.guindexuser.usingEmailAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Guinness Create Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Guinness price was submitted to the Guindex by a non-staff member:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Price', message.price),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])

                    context['add_text'] = "Please visit https://guindex.ie to verify the submission."

                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

                elif message.approved:

                    self.logger.debug("Sending Approved Guinness Create Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Guinness price has been added to the Guindex:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Price', message.price),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])
                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

            if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Guinness Create Alert Telegram to user %d", user.id)

                    telegram_message = "The following Guinness price has been added to the Guindex by a non-staff member:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Price: %s\n"       % message.price[1:]
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n\n"      % message.creationDate

                    telegram_message += "Please visit https://guindex.ie to verify the submission."

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

                elif message.approved:

                    self.logger.debug("Sending Approved Guinness Create Alert Telegram to user %d", user.id)

                    telegram_message = "The following Guinness price has been added to the Guindex:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Price: %s\n"       % message.price[1:]
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n"        % message.creationDate

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

    def _handleGuinnessPendingCreateDecisionAlertRequest(self, message):

        self.logger.info("Received Guinness Pending Create Decision Alert Request message")

        try:
            user = User.objects.get(id = message.userId)
        except:
            self.logger.error("Failed to find user with id %d", message.userId)

        self.logger.debug("Found user with id %d", user.id)

        self._validateAlertsSettings(user)

        if user.guindexuser.usingEmailAlerts:

            self.logger.debug("Sending Guinness Pending Create Decision Alert Email to user %d", user.id)

            context = {}

            decision = "approved" if message.approved else "rejected"

            context['username'] = user.username
            context['summary']  = "Your below price submission has been %s:" % decision
            context['data']     = OrderedDict([('Pub', message.pub),
                                               ('County', message.county),
                                               ('Price', message.price),
                                               ('Time', message.creationDate),
                                              ])

            if message.HasField('reason'):
                context['data'].update({'Reason': message.reason})

            try:
                html_content = render_to_string('alert_email_template.html', context)
            except:
                self.logger.error("Failed to render email to string")

            try:
                user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to user %d", user.id)

        if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

            self.logger.debug("Sending Guinness Pending Create Decision Alert Telegram to user %d", user.id)

            decision = "approved" if message.approved else "rejected"

            telegram_message = "Your below Guinness price submission has been %s:\n\n" % decision

            telegram_message += "Pub: %s\n"    % message.pub
            telegram_message += "County: %s\n" % message.county
            telegram_message += "Price: %s\n"  % message.price[1:]
            telegram_message += "Time: %s\n"   % message.creationDate

            if message.HasField('reason'):
                telegram_message += "Reason: %s\n" % message.reason

            try:
                GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
            except:
                self.logger.error("Failed to send Telegram to user %d", user.id)

    def _handlePubCreateAlertRequest(self, message):

        self.logger.info("Received Pub Create Alert Request message")

        for user in User.objects.all():

            self.logger.debug("Processing Pub Create Alert Request for user %d", user.id)

            self._validateAlertsSettings(user)

            if user.guindexuser.usingEmailAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Pub Create Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Pub was submitted to the Guindex by a non-staff member:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Latitude', message.latitude),
                                                       ('Longitude', message.longitude),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])

                    context['add_text'] = "Please visit https://guindex.ie to verify the submission."

                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

                elif message.approved:

                    self.logger.debug("Sending Approved Pub Create Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Pub has been added to the Guindex:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Latitude', message.latitude),
                                                       ('Longitude', message.longitude),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])

                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

            if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Pub Create Alert Telegram to user %d", user.id)

                    telegram_message = "The following Pub has been added to the Guindex by a non-staff member:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Latitude: %s\n"    % message.latitude
                    telegram_message += "Longitude: %s\n"   % message.longitude
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n\n"      % message.creationDate

                    telegram_message += "Please visit https://guindex.ie to verify the submission."

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

                elif message.approved:

                    self.logger.debug("Sending Approved Pub Create Alert Telegram to user %d", user.id)

                    telegram_message = "The following Pub has been added to the Guindex:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Latitude: %s\n"    % message.latitude
                    telegram_message += "Longitude: %s\n"   % message.longitude
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n"        % message.creationDate

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

    def _handlePubPatchAlertRequest(self, message):

        self.logger.info("Received Pub Patch Alert Request message")

        for user in User.objects.all():

            self.logger.debug("Processing Pub Patch Alert Request for user %d", user.id)

            self._validateAlertsSettings(user)

            if user.guindexuser.usingEmailAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Pub Patch Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Pub updates have been submitted to the Guindex by a non-staff member:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Updates', self._formatChangedFieldsEmail(message.changedFields)),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])

                    context['add_text'] = "Please visit https://guindex.ie to verify the submission."

                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

                elif message.approved:

                    self.logger.debug("Sending Approved Pub Patch Alert Email to user %d", user.id)

                    context = {}

                    context['username'] = user.username
                    context['summary']  = "The following Pub updates have been applied:"
                    context['data']     = OrderedDict([('Pub', message.pub),
                                                       ('County', message.county),
                                                       ('Updates', self._formatChangedFieldsEmail(message.changedFields)),
                                                       ('Contributor', message.username),
                                                       ('Time', message.creationDate),
                                                      ])
                    try:
                        html_content = render_to_string('alert_email_template.html', context)
                    except:
                        self.logger.error("Failed to render email to string")
                        continue

                    try:
                        user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
                    except:
                        self.logger.error("Failed to send email to user %d", user.id)
                        continue

            if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

                if not message.approved and user.is_staff:

                    self.logger.debug("Sending Unapproved Pub Patch Alert Telegram to user %d", user.id)

                    telegram_message = "The following Pub updates have been submitted to the Guindex by a non-staff member:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Updates: %s\n"     % self._formatChangedFieldsTelegram(message.changedFields)
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n\n"      % message.creationDate

                    telegram_message += "Please visit https://guindex.ie to verify the submission."

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

                elif message.approved:

                    self.logger.debug("Sending Approved Pub Patch Alert Telegram to user %d", user.id)

                    telegram_message = "The following Pub updates have been applied:\n\n"

                    telegram_message += "Pub: %s\n"         % message.pub
                    telegram_message += "County: %s\n"      % message.county
                    telegram_message += "Updates: %s\n"     % self._formatChangedFieldsTelegram(message.changedFields)
                    telegram_message += "Contributor: %s\n" % message.username
                    telegram_message += "Time: %s\n"        % message.creationDate

                    try:
                        GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
                    except:
                        self.logger.error("Failed to send Telegram to user %d", user.id)

    def _handlePubPendingCreateDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Pending Create Decision Alert Request message")

        try:
            user = User.objects.get(id = message.userId)
        except:
            self.logger.error("Failed to find user with id %d", message.userId)

        self.logger.debug("Found user with id %d", user.id)

        self._validateAlertsSettings(user)

        if user.guindexuser.usingEmailAlerts:

            self.logger.debug("Sending Pub Pending Create Decision Alert Email to user %d", user.id)

            context = {}

            decision = "approved" if message.approved else "rejected"

            context['username'] = user.username
            context['summary']  = "Your below Pub submission has been %s:" % decision
            context['data']     = OrderedDict([('Pub', message.pub),
                                               ('County', message.county),
                                               ('Latitude', message.latitude),
                                               ('Longitude', message.longitude),
                                               ('Time', message.creationDate),
                                              ])
            if message.HasField('reason'):
                context['data'].update({'Reason': message.reason})

            try:
                html_content = render_to_string('alert_email_template.html', context)
            except:
                self.logger.error("Failed to render email to string")

            try:
                user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to user %d", user.id)

        if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

            self.logger.debug("Sending Pub Pending Create Decision Alert Telegram to user %d", user.id)

            decision = "approved" if message.approved else "rejected"

            telegram_message = "Your below Pub submission has been %s:\n\n" % decision

            telegram_message += "Pub: %s\n"       % message.pub
            telegram_message += "County: %s\n"    % message.county
            telegram_message += "Latitude: %s\n"  % message.latitude
            telegram_message += "Longitude: %s\n" % message.longitude
            telegram_message += "Time: %s\n"      % message.creationDate

            if message.HasField('reason'):
                telegram_message += "Reason: %s\n" % message.reason

            try:
                GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
            except:
                self.logger.error("Failed to send Telegram to user %d", user.id)

    def _handlePubPendingPatchDecisionAlertRequest(self, message):

        self.logger.info("Received Pub Pending Patch Decision Alert Request message")

        try:
            user = User.objects.get(id = message.userId)
        except:
            self.logger.error("Failed to find user with id %d", message.userId)

        self.logger.debug("Found user with id %d", user.id)

        self._validateAlertsSettings(user)

        if user.guindexuser.usingEmailAlerts:

            self.logger.debug("Sending Pub Pending Patch Decision Alert Email to user %d", user.id)

            context = {}

            decision = "approved" if message.approved else "rejected"

            context['username'] = user.username
            context['summary']  = "Your below Pub update submission has been %s:" % decision
            context['data']     = OrderedDict([('Pub', message.pub),
                                               ('County', message.county),
                                               ('Updates', self._formatChangedFieldsEmail(message.changedFields)),
                                               ('Time', message.creationDate),
                                              ])

            if message.HasField('reason'):
                context['data'].update({'Reason': message.reason})

            try:
                html_content = render_to_string('alert_email_template.html', context)
            except:
                self.logger.error("Failed to render email to string")

            try:
                user.email_user('Guindex Submission Alert', html_content, None, html_message = html_content)
            except:
                self.logger.error("Failed to send email to user %d", user.id)

        if user.telegramuser.activated and user.telegramuser.usingTelegramAlerts:

            self.logger.debug("Sending Pub Pending Patch Decision Alert Telegram to user %d", user.id)

            decision = "approved" if message.approved else "rejected"

            telegram_message = "Your below Pub update submission has been %s:\n\n" % decision

            telegram_message += "Pub: %s\n"     % message.pub
            telegram_message += "County: %s\n"  % message.county
            telegram_message += "Updates: %s\n" % self._formatChangedFieldsTelegram(message.changedFields)
            telegram_message += "Time: %s\n"    % message.creationDate

            if message.HasField('reason'):
                telegram_message += "Reason: %s\n" % message.reason

            try:
                GuindexBot.sendMessage(telegram_message, user.telegramuser.chatId)
            except:
                self.logger.error("Failed to send Telegram to user %d", user.id)
