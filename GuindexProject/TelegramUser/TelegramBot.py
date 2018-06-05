import logging
import urllib
import requests
import argparse

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from TelegramUser.models import TelegramUser
from TelegramUser.TelegramUserParameters import TelegramUserParameters

logger = logging.getLogger(TelegramUserParameters.BOT_NAME)


class TelegramBot(Updater):
    """
        A class that defines minimal Telegram bot functionality.
    """

    def __init__(self, apiKey):

        self._apiKey = apiKey
        self._commandDict = {} # For getting descriptions

        super(TelegramBot, self).__init__(token = self._apiKey)

        # Add commands required according to Telegram docs

        # Add /activate command handler
        self.addCommand('activate', self.ActivateCommandHandler)

        # Add /start command handler
        self.addCommand('start', self.StartCommandHandler)

        # Add /help command handler
        # self.addCommand('help', self.HelpCommandHandler)

        # Add /settings command handler
        # self.addCommand('settings', self.SettingsCommandHandler)

        # Add unknown command handler for unknown commands
        self.dispatcher.add_handler(MessageHandler(Filters.command, self.unknownCommand))

        # Add unknown command handler for plain text messages
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.unknownCommand))

    @staticmethod
    def sendMessage(text, chatId, apiKey = settings.BOT_HTTP_API_TOKEN):
        """
            Server initiated message (i.e. not a response)
            Used by ProcessAlerts.py script.
            Make it static so we don't need TelegramBot object.
        """
        message = urllib.quote_plus(text)

        url = "https://api.telegram.org/bot{}/".format(apiKey) + "sendMessage?text={}&chat_id={}".format(message, chatId)

        # Send request
        response = requests.get(url)

        if response.status_code != 200:
            logger.error("Failed to send message to chat ID %s: RC = %d", chatId, response.status_code)
            raise

    def addCommand(self, commandName, commandHandler):

        self._commandDict[commandName] = commandHandler(None, None, None)
        self.dispatcher.add_handler(CommandHandler(commandName, commandHandler, pass_args = True))

    def getCommandDescriptions(self):
        """
            Print description of each command.
            Useful for defining new commands with Bot Father.
        """

        for command_name, command in self._commandDict.items():

            # Only take first line of description for now.
            print(command_name + ' - ' + command.getCommandDescription().split('\n', 1)[0])

    def unknownCommand(self, bot, update):
        """
            Handler for when we receive unknown command.
        """
        logger.info("Received unknown command")

        bot.send_message(chat_id = update.message.chat_id, text = "Oops! I didn't understand that command.")

    class TelegramCommandHandler():
        """
            Abstract class for parsing telegram commands
            Any commands that want to be added to a bot,
            just inherit from this class and define
            createParser and onParseSuccess functions.
        """

        def __init__(self, bot, update, args):

            logger.debug("%s init", self)

            self.parser = None

            if not bot: # HACK for printing descriptions
                return

            logger.info("Received %s command", update.message['text'])

            self._bot              = bot
            self._chatId           = update.message.chat_id
            self._commandArguments = args

            # Default error message. Should be updated in functions
            # implemented by derived classes if an error occurs
            self.errorMessage = "An error occured."

            try:
                self._parseArgs()
            except:
                logger.error("Failed to parse arguments %s", self._commandArguments)
                self._sendResponse(self.errorMessage)
                return

            try:
                self.findUser()
            except:
                logger.error("Failed to find User")
                self._sendResponse(self.errorMessage)
                return

            try:
                self.onParseSuccess()
            except:
                logger.error("Failed to apply parsed arguments")
                self._sendResponse(self.errorMessage)
                return

            self._sendResponse(self.getSuccessMessage())

        def __repr__(self):

            return(self.__class__.__name__)

        def _sendResponse(self, message):

            try:
                logger.info("Sending message to chatId %s - %s", self._chatId, message)
                self._bot.send_message(chat_id = self._chatId, text = message)
            except:
                logger.error("Failed to send Telegram response message")

        def createParser(self):
            """
                Creates parser object which will be used to parse command.
                Also defines command syntax and generates usage description."
            """
            raise NotImplementedError

        def _parseArgs(self):
            """
                Use parser object to parse arguments
            """

            logger.debug("Attempting to parse args - %s", self._commandArguments)

            try:
                self.createParser()
            except:
                logger.error("Failed to create parse object")
                self.errorMessage = "Failed to parse command. Looks like it was our fault. Sorry :/"
                raise

            logger.debug("Successfully created parser object")

            try:
                self.parsedArgs = self.parser.parse_args(self._commandArguments)
            except:
                self.errorMessage = ("Failed to parse command arguments. Have you made a mistake?\n"
                                     "Here is the command description again:\n\n"
                                     "%s" % self.getCommandDescription())
                raise

            logger.debug("Successfully parsed arguments")

        def findUser(self):
            """
                Try find User corresponding to chat ID.
            """

            logger.debug("Attempting to find User with chat ID %s", self._chatId)

            try:
                self.user = User.objects.get(telegramChatId = self._chatId)
            except ObjectDoesNotExist:
                logger.error("No user exists with chat ID %s", self._chatId)
                self.errorMessage = "No user exists with chat ID %s. Have you activated your account yet?" % self._chatId
                raise

            logger.debug("Successfully found User with chat ID %s - %d", self._chatId, self.user.id)

        def onParseSuccess(self):
            """
                Function to call once we successfully parse Telegram message.
            """
            raise NotImplementedError

        def getCommandDescription(self):
            """
                Function to return description generated by parser object.
            """

            if not self.parser: # Create parser if we don't have one yet
                self.createParser()

            # Remove first two lines (contains usage)
            help_text = self.parser.format_help().split("\n", 2)[2]

            return help_text

        def getSuccessMessage(self):
            """
                Response message if command is a success.
            """

            return "Command was successful"

    class StartCommandHandler(TelegramCommandHandler):

        def createParser(self):

            logger.info("Creating StartCommandHandler parser")

            self.description = "Get started with Telegram Bot."

            self.parser = argparse.ArgumentParser(description = self.description, add_help = False)

            # No arguments supplied /start command

            logger.debug("Created parser %s", self.parser)

        def findUser(self):

            # Don't need to do anything here
            pass

        def onParseSuccess(self):

            # Don't need to do anything here
            pass

        def getSuccessMessage(self):

            # TODO Get this from config file
            start_message = ("Hello! I'm the %s. To begin receiving alerts and "
                             "contributing to the Guindex please activate your account.\n"
                             "To do this send the command '/activate <username> <telegram_activation_key>'. "
                             "Your Telegram activation key was sent to you in a previous email when you first logged in.\n"
                             "For a list of futher commands send /help. Happy Gargling!" % TelegramUserParameters.BOT_NAME)

            return start_message

    class ActivateCommandHandler(TelegramCommandHandler):

        def createParser(self):

            logger.info("Creating ActivateCommandHandler parser")

            self.description = "Activate Telegram alerts with Telegram Bot."

            self.parser = argparse.ArgumentParser(description = self.description, add_help = False)

            # Positional Arguments
            # Note: first argument becomes dest for positional arguments
            self.parser.add_argument('telegramActivationKey',
                                     metavar = '<Telegram Activation Key>',
                                     action = 'store',
                                     help = 'Your Telegram activation key (visible in User Settings Tab on Guindex website)')

            logger.debug("Created parser %s", self.parser)

        def findUser(self):
            """
                Find User using username parsed from /activate command.
                Only command that needs to overwrite this.
            """

            try:
                telegram_activation_key = self.parsedArgs.telegramActivationKey
            except:
                logger.error("Unable to get Telegram Activation Key from parsed arguments")
                self.errorMessage = "Unable to get Telegram Activation Key from parsed arguments"
                raise

            logger.debug("Attempting to find User with Telegram Activation Key %s", telegram_activation_key)

            try:
                telegram_user = TelegramUser.objects.get(activationKey = telegram_activation_key)
            except ObjectDoesNotExist:
                logger.error("No user existis with Telegram Activation Key %s", telegram_activation_key)
                self.errorMessage = "No user exists with Telegram Activation Key %s" % telegram_activation_key
                raise

            self.user = telegram_user.user

            logger.debug("Successfully found User with Telegram Activation Key %s - %d", telegram_activation_key, self.user.id)

        def onParseSuccess(self):

            logger.debug("User %d: Has Telegram account already been activated?", self.user.id)

            # Try get Telegram Chat ID
            try:
                telegram_activation_key = self.parsedArgs.telegramActivationKey
            except:
                logger.error("User %d: Failed to get activation key from parsed args", self.user.id)
                self.errorMessage = "Ooops! Problem on our end. Looking at it now. Apologies!"
                raise

            # Check activation keys match
            if not self.user.telegramuser.activationKey == telegram_activation_key:
                logger.error("User %d: Activation keys do not match, %s : %s",
                             self.user.id, self.usertelegramuser.activationKey, telegram_activation_key)
                self.errorMessage = "Incorrect activation key."
                raise

            # Save chat ID
            self.user.telegramuser.chatId = self._chatId
            self.user.telegramuser.activated = True
            self.user.telegramuser.save()

        def getSuccessMessage(self):

            return "Successfully activated Telegram account."
