import logging
import inspect

logger = logging.getLogger(__name__)


class TelegramUserParameters:

    ACTIVATION_KEY_LENGTH = 6
    CHAT_ID_LENGTH        = 32
    BOT_NAME              = "GuindexBot"

    @staticmethod
    def getParameters():

        parameter_dict = {}

        class_attributes = TelegramUserParameters.__dict__

        # Get this function's name
        frame = inspect.currentframe()
        function_name = inspect.getframeinfo(frame).function

        for key, attribute in class_attributes.iteritems():

            if not key.startswith("__") and key != function_name:

                parameter_dict[key] = attribute

        return parameter_dict
