import inspect


class GuindexParameters:

    # Pub Parameters
    MAX_PUB_NAME_LEN = 100
    MAP_LINK_STRING = "https://www.google.ie/maps/place/%f,%f"

    # Guinness price parameters
    MAX_GUINNESS_PRICE_DIGITS     = 4
    MIN_GUINNESS_PRICE            = '0.01'
    GUINNESS_PRICE_DECIMAL_PLACES = 2
    STAR_RATING_DECIMAL_PLACES    = 2

    # Pending Contribution Accept/Reject Parameters
    REJECT_REASON_MAX_LEN = 500

    # Background script run periods (in seconds)
    DB_BACKUP_PERIOD         = 86400
    STATS_CALCULATION_PERIOD = 86400
    ALERTS_CHECK_PERIOD      = 86400 * 7

    # Map generation parameters
    MAP_GENERATION_PERIOD   = 30
    DUBLIN_CENTER_LATITUDE  = 53.489969 
    DUBLIN_CENTER_LONGITUDE = -7.565688
    MAP_ZOOM_LEVEL          = 7
    MAX_MAP_LINK_LEN        = 2000

    # Alerts Server Parameters
    ALERTS_LISTEN_IP   = '127.0.0.1'
    ALERTS_LISTEN_PORT = 8088
    ALERTS_BACKLOG     = 50

    # GPS Parameters
    GPS_COORD_DECIMAL_PLACES = 20
    GPS_COORD_MAX_DIGITS     = 23

    GPS_ANTRIM_MIN_LATITUDE     = '54.4772774'
    GPS_ANTRIM_MAX_LATITUDE     = '55.3130865'
    GPS_ANTRIM_MIN_LONGITUDE    = '-6.6689888'
    GPS_ANTRIM_MAX_LONGITUDE    = '-5.6879629'
    GPS_ARMAGH_MIN_LATITUDE     = '54.0364597'
    GPS_ARMAGH_MAX_LATITUDE     = '54.5675362'
    GPS_ARMAGH_MIN_LONGITUDE    = '-6.8780377'
    GPS_ARMAGH_MAX_LONGITUDE    = '-6.290864'
    GPS_CARLOW_MIN_LATITUDE     = '52.4633869052'
    GPS_CARLOW_MAX_LATITUDE     = '52.9176936493'
    GPS_CARLOW_MIN_LONGITUDE    = '-7.1072067086'
    GPS_CARLOW_MAX_LONGITUDE    = '-6.5042672209'
    GPS_CAVAN_MIN_LATITUDE      = '53.7653604371'
    GPS_CAVAN_MAX_LATITUDE      = '54.3043619338'
    GPS_CAVAN_MIN_LONGITUDE     = '-8.0574872701'
    GPS_CAVAN_MAX_LONGITUDE     = '-6.761270843'
    GPS_CLARE_MIN_LATITUDE      = '52.5543298283509'
    GPS_CLARE_MAX_LATITUDE      = '53.1685613143'
    GPS_CLARE_MIN_LONGITUDE     = '-9.9378562853'
    GPS_CLARE_MAX_LONGITUDE     = '-8.2816886594'
    GPS_CORK_MIN_LATITUDE       = '51.4196887946'
    GPS_CORK_MAX_LATITUDE       = '52.3877509338'
    GPS_CORK_MIN_LONGITUDE      = '-10.2475415358'
    GPS_CORK_MAX_LONGITUDE      = '-7.8404021003'
    GPS_DERRY_MIN_LATITUDE      = '54.6282688'
    GPS_DERRY_MAX_LATITUDE      = '55.2002556'
    GPS_DERRY_MIN_LONGITUDE    = '-7.4074364'
    GPS_DERRY_MAX_LONGITUDE    = '-6.4570362'
    GPS_DONEGAL_MIN_LATITUDE    = '54.4588514997393'
    GPS_DONEGAL_MAX_LATITUDE    = '55.4463629142'
    GPS_DONEGAL_MIN_LONGITUDE   = '-8.834035422'
    GPS_DONEGAL_MAX_LONGITUDE   = '-6.921215597'
    GPS_DOWN_MIN_LATITUDE       = '54.0228909'
    GPS_DOWN_MAX_LATITUDE       = '54.6992448'
    GPS_DOWN_MIN_LONGITUDE      = '-6.4003727'
    GPS_DOWN_MAX_LONGITUDE      = '-5.4268157'
    GPS_DUBLIN_MIN_LATITUDE     = '53.1779929359909'
    GPS_DUBLIN_MAX_LATITUDE     = '53.6345095065'
    GPS_DUBLIN_MIN_LONGITUDE    = '-6.546150018'
    GPS_DUBLIN_MAX_LONGITUDE    = '-5.9955549997'
    GPS_FERMANAGH_MIN_LATITUDE  = '54.1132751'
    GPS_FERMANAGH_MAX_LATITUDE  = '54.6105377'
    GPS_FERMANAGH_MIN_LONGITUDE = '-8.1775098'
    GPS_FERMANAGH_MAX_LONGITUDE = '-7.1415157'
    GPS_GALWAY_MIN_LATITUDE     = '52.9679414729'
    GPS_GALWAY_MAX_LATITUDE     = '53.7187021311'
    GPS_GALWAY_MIN_LONGITUDE    = '-10.3015401125'
    GPS_GALWAY_MAX_LONGITUDE    = '-7.9665981229'
    GPS_KERRY_MIN_LATITUDE      = '51.6881155459'
    GPS_KERRY_MAX_LATITUDE      = '52.6022449392'
    GPS_KERRY_MIN_LONGITUDE     = '-10.6621120456'
    GPS_KERRY_MAX_LONGITUDE     = '-9.1180546314'
    GPS_KILDARE_MIN_LATITUDE    = '52.857364081'
    GPS_KILDARE_MAX_LATITUDE    = '53.4510231653'
    GPS_KILDARE_MIN_LONGITUDE   = '-7.168198596'
    GPS_KILDARE_MAX_LONGITUDE   = '-6.4592335347'
    GPS_KILKENNY_MIN_LATITUDE   = '52.2426343481'
    GPS_KILKENNY_MAX_LATITUDE   = '52.8937364434'
    GPS_KILKENNY_MIN_LONGITUDE  = '-7.6733496277'
    GPS_KILKENNY_MAX_LONGITUDE  = '-6.9139119497'
    GPS_LAOIS_MIN_LATITUDE      = '52.7810568801'
    GPS_LAOIS_MAX_LATITUDE      = '53.2154390471'
    GPS_LAOIS_MIN_LONGITUDE     = '-7.7339175094'
    GPS_LAOIS_MAX_LONGITUDE     = '-6.9312149086'
    GPS_LEITRIM_MIN_LATITUDE    = '53.8057557613'
    GPS_LEITRIM_MAX_LATITUDE    = '54.474133572'
    GPS_LEITRIM_MIN_LONGITUDE   = '-8.4269003828'
    GPS_LEITRIM_MAX_LONGITUDE   = '-7.5834482954'
    GPS_LIMERICK_MIN_LATITUDE   = '52.280022268'
    GPS_LIMERICK_MAX_LATITUDE   = '52.7571892027'
    GPS_LIMERICK_MIN_LONGITUDE  = '-9.3669079807'
    GPS_LIMERICK_MAX_LONGITUDE  = '-8.1556035022'
    GPS_LONGFORD_MIN_LATITUDE   = '53.5215192194'
    GPS_LONGFORD_MAX_LATITUDE   = '53.9418499684'
    GPS_LONGFORD_MIN_LONGITUDE  = '-8.0352367606'
    GPS_LONGFORD_MAX_LONGITUDE  = '-7.3741834068'
    GPS_LOUTH_MIN_LATITUDE      = '53.6982757227'
    GPS_LOUTH_MAX_LATITUDE      = '54.1137319949'
    GPS_LOUTH_MIN_LONGITUDE     = '-6.6946074621'
    GPS_LOUTH_MAX_LONGITUDE     = '-6.1022769026'
    GPS_MAYO_MIN_LATITUDE       = '53.4717186356'
    GPS_MAYO_MAX_LATITUDE       = '54.3685435178'
    GPS_MAYO_MIN_LONGITUDE      = '-10.2585793745'
    GPS_MAYO_MAX_LONGITUDE      = '-8.5823359107'
    GPS_MEATH_MIN_LATITUDE      = '53.3816525281'
    GPS_MEATH_MAX_LATITUDE      = '53.9174540753'
    GPS_MEATH_MIN_LONGITUDE     = '-7.3429262905'
    GPS_MEATH_MAX_LONGITUDE     = '-6.2119065211'
    GPS_MONAGHAN_MIN_LATITUDE   = '53.900465006'
    GPS_MONAGHAN_MAX_LATITUDE   = '54.4211771093'
    GPS_MONAGHAN_MIN_LONGITUDE  = '-7.3387649981'
    GPS_MONAGHAN_MAX_LONGITUDE  = '-6.5489921472'
    GPS_OFFALY_MIN_LATITUDE     = '52.8479602726'
    GPS_OFFALY_MAX_LATITUDE     = '53.4239722099'
    GPS_OFFALY_MIN_LONGITUDE    = '-8.0831361544'
    GPS_OFFALY_MAX_LONGITUDE    = '-6.9769754239'
    GPS_ROSCOMMON_MIN_LATITUDE  = '53.2711600414'
    GPS_ROSCOMMON_MAX_LATITUDE  = '54.1250286336'
    GPS_ROSCOMMON_MIN_LONGITUDE = '-8.822972469'
    GPS_ROSCOMMON_MAX_LONGITUDE = '-7.8751042398'
    GPS_SLIGO_MIN_LATITUDE      = '53.9127997962'
    GPS_SLIGO_MAX_LATITUDE      = '54.4728137722'
    GPS_SLIGO_MIN_LONGITUDE     = '-9.1358012487'
    GPS_SLIGO_MAX_LONGITUDE     = '-8.1522618453'
    GPS_TIPPERARY_MIN_LATITUDE  = '52.2018038633'
    GPS_TIPPERARY_MAX_LATITUDE  = '53.1673712452'
    GPS_TIPPERARY_MIN_LONGITUDE = '-8.4793447933'
    GPS_TIPPERARY_MAX_LONGITUDE = '-7.371335621'
    GPS_TYRONE_MIN_LATITUDE     = '54.3253027'
    GPS_TYRONE_MAX_LATITUDE     = '54.9453614'
    GPS_TYRONE_MIN_LONGITUDE    = '-7.9208903'
    GPS_TYRONE_MAX_LONGITUDE    = '-6.4065901'
    GPS_WATERFORD_MIN_LATITUDE  = '51.937785831'
    GPS_WATERFORD_MAX_LATITUDE  = '52.3636788119'
    GPS_WATERFORD_MIN_LONGITUDE = '-8.1619704153'
    GPS_WATERFORD_MAX_LONGITUDE = '-6.9492978979'
    GPS_WESTMEATH_MIN_LATITUDE  = '53.3177496573'
    GPS_WESTMEATH_MAX_LATITUDE  = '53.7988392098'
    GPS_WESTMEATH_MIN_LONGITUDE = '-7.972215475'
    GPS_WESTMEATH_MAX_LONGITUDE = '-6.9540492953'
    GPS_WEXFORD_MIN_LATITUDE    = '52.1089957299'
    GPS_WEXFORD_MAX_LATITUDE    = '52.7972538216'
    GPS_WEXFORD_MIN_LONGITUDE   = '-7.0174875018'
    GPS_WEXFORD_MAX_LONGITUDE   = '-6.1400555355'
    GPS_WICKLOW_MIN_LATITUDE    = '52.681744803'
    GPS_WICKLOW_MAX_LATITUDE    = '53.2341938912'
    GPS_WICKLOW_MIN_LONGITUDE   = '-6.7913182579'
    GPS_WICKLOW_MAX_LONGITUDE   = '-5.9973359842'
    
    MAX_COUNTY_NAME_LEN = 15

    # County badge images: static/images/{CountyName}_{tier}_pubs.png (name as in DB, spaces to underscores).
    # Per county, only the highest tier where unique_pub_count >= tier is shown.
    BADGE_UNIQUE_PUB_TIERS = (50, 20, 10, 1)

    SUPPORTED_COUNTIES  = [
        'Antrim',
        'Armagh',
        'Carlow',        
        'Cavan',
        'Clare',
        'Cork',
        'Derry',
        'Donegal',
        'Down',
        'Dublin',
        'Fermanagh',
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
        'Tyrone',
        'Waterford',
        'Westmeath',
        'Wexford',
        'Wicklow',
    ]

    COUNTY_CURRENCIES = {
        c: u"\u20ac" for c in SUPPORTED_COUNTIES if c not in ["Antrim", "Armagh", "Derry", "Down", "Fermanagh", "Tyrone"]
    }
    COUNTY_CURRENCIES.update({
        "Antrim": u"\u00a3",
        "Armagh": u"\u00a3",
        "Derry": u"\u00a3",
        "Down": u"\u00a3",
        "Fermanagh": u"\u00a3",
        "Tyrone": u"\u00a3",
    })

    @staticmethod
    def get_county_map_viewport(county):
        """
            Center and bounding box for map view of a supported county.
        """
        county_key = county.upper()
        min_lat = float(getattr(GuindexParameters, 'GPS_%s_MIN_LATITUDE' % county_key))
        max_lat = float(getattr(GuindexParameters, 'GPS_%s_MAX_LATITUDE' % county_key))
        min_lng = float(getattr(GuindexParameters, 'GPS_%s_MIN_LONGITUDE' % county_key))
        max_lng = float(getattr(GuindexParameters, 'GPS_%s_MAX_LONGITUDE' % county_key))

        return {
            'centerLat': (min_lat + max_lat) / 2.0,
            'centerLng': (min_lng + max_lng) / 2.0,
            'minLat': min_lat,
            'maxLat': max_lat,
            'minLng': min_lng,
            'maxLng': max_lng,
        }

    # Contact Form Parameters
    MAX_CONTACT_FORM_NAME_LEN    = 30
    MAX_CONTACT_FORM_EMAIL_LEN   = 50
    MAX_CONTACT_FORM_SUBJECT_LEN = 30
    MAX_CONTACT_FORM_MESSAGE_LEN = 500

    def getParameters():

        parameter_dict = {}

        class_attributes = GuindexParameters.__dict__

        # Get this function's name
        frame = inspect.currentframe()
        function_name = inspect.getframeinfo(frame).function

        for key, attribute in class_attributes.items():

            if not key.startswith("__") and key != function_name:

                parameter_dict[key] = attribute

        return parameter_dict
