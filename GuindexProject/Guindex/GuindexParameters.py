import logging
import inspect

logger = logging.getLogger(__name__)


class GuindexParameters:

    MAX_PUB_NAME_LEN = 40

    MAX_GUINNESS_PRICE = 100.00
    MIN_GUINNESS_PRICE = 0.00

    @staticmethod
    def getParameters():

        parameter_dict = {}

        class_attributes = GuindexParameters.__dict__

        # Get this function's name
        frame = inspect.currentframe()
        function_name = inspect.getframeinfo(frame).function

        for key, attribute in class_attributes.iteritems():

            if not key.startswith("__") and key != function_name:

                parameter_dict[key] = attribute

        logger.debug("Returning Guindex parameters - %s", parameter_dict)

        return parameter_dict
