import argparse
import asyncio
import logging
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from TelegramUser.models import TelegramUser
from TelegramUser.TelegramUserParameters import TelegramUserParameters

logger = logging.getLogger(TelegramUserParameters.BOT_NAME)


class TelegramBot:
    """
    Telegram bot using python-telegram-bot Application API (v21+).
    Command handlers run Django ORM in a thread pool via asyncio.to_thread.
    """

    def __init__(self, api_key):
        self._api_key = api_key
        self._command_dict = {}
        self._application = Application.builder().token(api_key).build()
        self.add_command("activate", self.ActivateCommandHandler)
        self.add_command("start", self.StartCommandHandler)
        self._application.add_handler(
            MessageHandler(filters.COMMAND | filters.TEXT, self._unknown_command)
        )

    def add_command(self, command_name, handler_cls):
        self._command_dict[command_name] = handler_cls(None, None)
        self._application.add_handler(
            CommandHandler(command_name, self._wrap_cmd(handler_cls))
        )

    def _wrap_cmd(self, handler_cls):
        async def _handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await asyncio.to_thread(handler_cls, update, context)

        return _handler

    async def _unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Received unknown command")
        chat = update.effective_chat
        if not chat:
            return
        await asyncio.to_thread(
            TelegramBot.sendMessage,
            "Oops! I didn't understand that command.",
            str(chat.id),
        )

    def run_polling(self):
        self._application.run_polling(allowed_updates=Update.ALL_TYPES)

    @staticmethod
    def sendMessage(text, chat_id, api_key=settings.BOT_HTTP_API_TOKEN):
        message = quote_plus(text)
        url = (
            f"https://api.telegram.org/bot{api_key}/sendMessage"
            f"?text={message}&chat_id={chat_id}"
        )
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logger.error(
                "Failed to send message to chat ID %s: RC = %d",
                chat_id,
                response.status_code,
            )
            raise RuntimeError("Telegram sendMessage failed")

    def getCommandDescriptions(self):
        for command_name, command in self._command_dict.items():
            print(
                command_name
                + " - "
                + command.getCommandDescription().split("\n", 1)[0]
            )

    class TelegramCommandHandler:
        def __init__(self, update, context):
            logger.debug("%s init", self)

            self.parser = None

            if update is None and context is None:
                return

            msg = update.effective_message
            logger.info("Received %s command", msg.text if msg else "")

            self._chat_id = update.effective_chat.id if update.effective_chat else None
            self._command_arguments = list(context.args) if context.args else []

            self.errorMessage = "An error occured."

            try:
                self._parseArgs()
            except Exception:
                logger.exception("Failed to parse arguments %s", self._command_arguments)
                self._sendResponse(self.errorMessage)
                return

            try:
                self.findUser()
            except Exception:
                logger.exception("Failed to find User")
                self._sendResponse(self.errorMessage)
                return

            try:
                self.onParseSuccess()
            except Exception:
                logger.exception("Failed to apply parsed arguments")
                self._sendResponse(self.errorMessage)
                return

            self._sendResponse(self.getSuccessMessage())

        def __repr__(self):
            return self.__class__.__name__

        def _sendResponse(self, message):
            try:
                logger.info("Sending message to chatId %s - %s", self._chat_id, message)
                TelegramBot.sendMessage(message, str(self._chat_id))
            except Exception:
                logger.exception("Failed to send Telegram response message")

        def createParser(self):
            raise NotImplementedError

        def _parseArgs(self):
            logger.debug("Attempting to parse args - %s", self._command_arguments)

            try:
                self.createParser()
            except Exception:
                logger.exception("Failed to create parse object")
                self.errorMessage = (
                    "Failed to parse command. Looks like it was our fault. Sorry :/"
                )
                raise

            logger.debug("Successfully created parser object")

            try:
                self.parsedArgs = self.parser.parse_args(self._command_arguments)
            except Exception:
                self.errorMessage = (
                    "Failed to parse command arguments. Have you made a mistake?\n"
                    "Here is the command description again:\n\n"
                    "%s" % self.getCommandDescription()
                )
                raise

            logger.debug("Successfully parsed arguments")

        def findUser(self):
            logger.debug("Attempting to find User with chat ID %s", self._chat_id)

            try:
                self.user = User.objects.get(telegramuser__chatId=str(self._chat_id))
            except ObjectDoesNotExist:
                logger.error("No user exists with chat ID %s", self._chat_id)
                self.errorMessage = (
                    "No user exists with chat ID %s. Have you activated your account yet?"
                    % self._chat_id
                )
                raise

            logger.debug(
                "Successfully found User with chat ID %s - %d",
                self._chat_id,
                self.user.id,
            )

        def onParseSuccess(self):
            raise NotImplementedError

        def getCommandDescription(self):
            if not self.parser:
                self.createParser()

            help_text = self.parser.format_help().split("\n", 2)[2]

            return help_text

        def getSuccessMessage(self):
            return "Command was successful"

    class StartCommandHandler(TelegramCommandHandler):
        def createParser(self):
            logger.info("Creating StartCommandHandler parser")

            self.description = "Get started with Telegram Bot."

            self.parser = argparse.ArgumentParser(
                description=self.description, add_help=False
            )

            logger.debug("Created parser %s", self.parser)

        def findUser(self):
            pass

        def onParseSuccess(self):
            pass

        def getSuccessMessage(self):
            start_message = (
                "Hello! I'm the %s. To begin receiving alerts and "
                "contributing to the Guindex please activate your account.\n"
                "To do this send the command '/activate <username> <telegram_activation_key>'. "
                "Your Telegram activation key was sent to you in a previous email when you first logged in.\n"
                "For a list of futher commands send /help. Happy Gargling!"
            ) % TelegramUserParameters.BOT_NAME

            return start_message

    class ActivateCommandHandler(TelegramCommandHandler):
        def createParser(self):
            logger.info("Creating ActivateCommandHandler parser")

            self.description = "Activate Telegram alerts with Telegram Bot."

            self.parser = argparse.ArgumentParser(
                description=self.description, add_help=False
            )

            self.parser.add_argument(
                "telegramActivationKey",
                metavar="<Telegram Activation Key>",
                action="store",
                help="Your Telegram activation key (visible in User Settings Tab on Guindex website)",
            )

            logger.debug("Created parser %s", self.parser)

        def findUser(self):
            try:
                telegram_activation_key = self.parsedArgs.telegramActivationKey
            except Exception:
                logger.error("Unable to get Telegram Activation Key from parsed arguments")
                self.errorMessage = (
                    "Unable to get Telegram Activation Key from parsed arguments"
                )
                raise

            logger.debug(
                "Attempting to find User with Telegram Activation Key %s",
                telegram_activation_key,
            )

            try:
                telegram_user = TelegramUser.objects.get(
                    activationKey=telegram_activation_key
                )
            except ObjectDoesNotExist:
                logger.error(
                    "No user existis with Telegram Activation Key %s",
                    telegram_activation_key,
                )
                self.errorMessage = (
                    "No user exists with Telegram Activation Key %s"
                    % telegram_activation_key
                )
                raise

            self.user = telegram_user.user

            logger.debug(
                "Successfully found User with Telegram Activation Key %s - %d",
                telegram_activation_key,
                self.user.id,
            )

        def onParseSuccess(self):
            logger.debug(
                "User %d: Has Telegram account already been activated?", self.user.id
            )

            try:
                telegram_activation_key = self.parsedArgs.telegramActivationKey
            except Exception:
                logger.error(
                    "User %d: Failed to get activation key from parsed args",
                    self.user.id,
                )
                self.errorMessage = "Ooops! Problem on our end. Looking at it now. Apologies!"
                raise

            if self.user.telegramuser.activationKey != telegram_activation_key:
                logger.error(
                    "User %d: Activation keys do not match, %s : %s",
                    self.user.id,
                    self.user.telegramuser.activationKey,
                    telegram_activation_key,
                )
                self.errorMessage = "Incorrect activation key."
                raise

            self.user.telegramuser.chatId = str(self._chat_id)
            self.user.telegramuser.activated = True
            self.user.telegramuser.save()

        def getSuccessMessage(self):
            return "Successfully activated Telegram account."
