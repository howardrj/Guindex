import inspect


class GuindexParameters:

    MAX_PUB_NAME_LEN = 40

    # Guinness price parameters
    MAX_GUINNESS_PRICE_DIGITS     = 4
    MIN_GUINNESS_PRICE            = '0.01'
    GUINNESS_PRICE_DECIMAL_PLACES = 2

    # Background script run periods (in seconds)
    DB_BACKUP_PERIOD         = 84600
    STATS_CALCULATION_PERIOD = 3600

    # Alerts Server Parameters
    ALERTS_LISTEN_IP   = '127.0.0.1'
    ALERTS_LISTEN_PORT = 8088
    ALERTS_BACKLOG     = 50

    # GPS Parameters
    GPS_COORD_DECIMAL_PLACES     = 20
    GPS_COORD_MAX_DIGITS         = 23
    GPS_DUBLIN_MIN_LATITUDE      = '53.185403'
    GPS_DUBLIN_MAX_LATITUDE      = '53.635552'
    GPS_DUBLIN_MIN_LONGITUDE     = '-6.547498'
    GPS_DUBLIN_MAX_LONGITUDE     = '-6.042723'
    MAP_LINK_STRING              = "https://www.google.ie/maps/place/%f,%f"

    REJECT_REASON_MAX_LEN = 100

    # Contact Form Parameters
    MAX_CONTACT_FORM_NAME_LEN    = 30
    MAX_CONTACT_FORM_EMAIL_LEN   = 50
    MAX_CONTACT_FORM_SUBJECT_LEN = 30
    MAX_CONTACT_FORM_MESSAGE_LEN = 500

    # County Parameters
    MAX_COUNTY_NAME_LEN = 15
    SUPPORTED_COUNTIES  = [
        'Cavan',
	    'Carlow',
        'Clare',
        'Cork',
		'Donegal',
	    'Dublin',
		'Galway',
		'Kerry',
		'Kildare',
		'Kilkenny',
		'Laois',
		'Leitrim',
		'Limerick',
		'Longford',
		'Louth',
		'Mayo',
		'Meath',
		'Monaghan',
		'Offaly',
		'Roscommon',
	    'Sligo',
		'Tipperary',
		'Waterford',
		'Westmeath',
		'Wexford',
		'Wicklow',
    ]

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
