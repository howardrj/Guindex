import logging
import inspect

logger = logging.getLogger(__name__)


class GuindexParameters:

    MAX_PUB_NAME_LEN = 40

    MAX_GUINNESS_PRICE = 100.00
    MIN_GUINNESS_PRICE = 0.00

    STATISTICS_CALCULATION_PERIOD         = 600 # In seconds
    USER_CONTRIBUTIONS_CALCULATION_PERIOD = 600 # In seconds
    DB_BACKUP_PERIOD                      = 84600 # In seconds

    # Alerts Server Parameters
    ALERTS_LISTEN_IP   = '127.0.0.1'
    ALERTS_LISTEN_PORT = 8080
    ALERTS_BACKLOG     = 50

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

        return parameter_dict
