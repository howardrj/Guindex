import inspect


class GuindexParameters:

    MAX_PUB_NAME_LEN = 40

    # Guinness price parameters
    MAX_GUINNESS_PRICE_DIGITS = 4
    MIN_GUINNESS_PRICE        = '0.01'

    # Background script parameters
    STATISTICS_CALCULATION_PERIOD         = 600 # In seconds
    USER_CONTRIBUTIONS_CALCULATION_PERIOD = 600 # In seconds
    DB_BACKUP_PERIOD                      = 84600 # In seconds

    # Alerts Server Parameters
    ALERTS_LISTEN_IP   = '127.0.0.1'
    ALERTS_LISTEN_PORT = 8080
    ALERTS_BACKLOG     = 50

    # Stats Server Parameters
    STATS_LISTEN_IP   = '127.0.0.1'
    STATS_LISTEN_PORT = 8081
    STATS_BACKLOG     = 50

    # GPS Parameters
    GPS_COORD_DECIMAL_PLACES     = 7
    GPS_COORD_MIN_DECIMAL_PLACES = 6
    GPS_DUBLIN_MIN_LATITUDE      = '53.185403'
    GPS_DUBLIN_MAX_LATITUDE      = '53.635552'
    GPS_DUBLIN_MIN_LONGITUDE     = '-6.547498'
    GPS_DUBLIN_MAX_LONGITUDE     = '-6.042723'

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
