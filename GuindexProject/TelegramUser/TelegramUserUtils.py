import logging

from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from TelegramUser.models import TelegramUser
from TelegramUserParameters import TelegramUserParameters

logger = logging.getLogger(__name__)


def createNewTelegramUser(user):

    logger.info("Creating new TelegramUser for User %s", user)

    telegram_user = TelegramUser()

    telegram_user.activationKey = generateActivationKey()
    telegram_user.chatId        = generateChatId()
    telegram_user.user          = user

    telegram_user.save()

    # sendActivationEmail(telegram_user, user)

    logger.info("Successfully created new TelegramUser %s for User %s", telegram_user, user)


def sendActivationEmail(telegramUser, user):
    """
        Send email informing TelegramUser how to activate
        Telegram account.
    """

    logger.info("Sending Telegram activation email to User %s", user)

    data = {}

    data['username']                 = user.username
    data['telegram_activation_key']  = telegramUser.activationKey
    data['project_title']            = settings.PROJECT_TITLE
    data['telegram_user_parameters'] = TelegramUserParameters.getParameters()

    try:
        html_content = render_to_string('telegram_activation_email.html', data)
        user.email_user("%s - Telegram Activation" % settings.PROJECT_TITLE, html_content, None, html_message = html_content)
    except:
        logger.error("Failed to send Telegram activation email to %s", user.email)

    logger.error("Successfully sent Telegram activation email to %s", user.email)


def generateActivationKey():

    key_is_free = False

    activation_key = get_random_string(length = TelegramUserParameters.ACTIVATION_KEY_LENGTH)

    while not key_is_free:

        try:
            TelegramUser.objects.get(activationKey = activation_key)
            activation_key = get_random_string(length = TelegramUserParameters.ACTIVATION_KEY_LENGTH)
        except ObjectDoesNotExist:
            key_is_free = True

    logger.info("Generated activation key %s", activation_key)

    return activation_key


def generateChatId():
    """
        This is a dummy chat ID created to deal with unique constraint
        Actual chat ID will be stored during activation process.
    """

    chat_id_is_free = False

    chat_id = get_random_string(length = TelegramUserParameters.CHAT_ID_LENGTH)

    while not chat_id_is_free:

        try:
            TelegramUser.objects.get(chatId = chat_id)
            chat_id = get_random_string(length = TelegramUserParameters.CHAT_ID_LENGTH)
        except ObjectDoesNotExist:
            chat_id_is_free = True

    logger.info("Generated chat ID %s", chat_id)

    return chat_id
