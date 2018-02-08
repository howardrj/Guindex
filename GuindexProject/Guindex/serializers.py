import logging

from django.core.exceptions import ValidationError

from rest_framework import serializers

from Guindex.models import Pub, Guinness, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters
from Guindex.GuindexAlertsClient import GuindexAlertsClient
from Guindex.GuindexStatsClient import GuindexStatsClient

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


########################
# Guinness Serializers #
########################

class GuinnessGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guinness
        fields = '__all__'


class GuinnessPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guinness
        # Note: Creator is extracted from request object,
        # not message payload so don't include it in fields
        fields = ['pub', 'price']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def onCreateSuccess(self, guinness, request, userProfile):

        logger.info("Successfully created new Guinness object")

        # Fields have been correctly set in firstSave at this point

        # Send alerts
        try:
            alerts_client = GuindexAlertsClient(logger,
                                                GuindexParameters.ALERTS_LISTEN_IP,
                                                GuindexParameters.ALERTS_LISTEN_PORT)

            alerts_client.sendNewGuinnessAlertRequest(guinness, request)
        except:
            logger.error("Failed to send New Guinness Alert Request")

        if not userProfile.user.is_staff:
            logger.info("Not updating stats until contribution is approved")
            return

        # Update statistics
        try:
            stats_client = GuindexStatsClient(logger,
                                              GuindexParameters.STATS_LISTEN_IP,
                                              GuindexParameters.STATS_LISTEN_PORT)

            stats_client.sendNewGuinnessStatsRequest(guinness)
        except:
            logger.error("Failed to send New Guinness Stats Request")


class GuinnessPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guinness
        fields = ['approved', 'rejectReason']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def validate_approved(self, approved):

        logger.debug("Validating approved %s", approved)

        if self.instance.approved: # Previous approve value
            raise ValidationError("Cannot update an already approved Guinness")

        if self.instance.rejected:
            raise ValidationError("Cannot update a rejected Guinness")

        # Sending approved = False updates Guinness to rejected
        # and vice versa
        self.instance.rejected = not approved

        # Store approved value so we can use it in validate_rejectReason
        self.approved = approved

        return approved

    def validate_rejectReason(self, rejectReason):

        logger.debug("Validating rejectReason %s", rejectReason)

        if not hasattr(self, 'approved'):
            raise ValidationError("Cannot have rejectReason without approved field")

        if self.approved:
            raise ValidationError("Cannot include reject reason if Guinness submission is approved")

        return rejectReason

    def onPatchSuccess(self, guinness, request, userProfile):

        logger.info("Successfully created new Guinness object")

        # Fields have been correctly set in validate functions at this point

        # Send alerts
        try:
            alerts_client = GuindexAlertsClient(logger,
                                                GuindexParameters.ALERTS_LISTEN_IP,
                                                GuindexParameters.ALERTS_LISTEN_PORT)

            alerts_client.sendNewGuinnessDecisionAlertRequest(guinness, guinness.rejectReason)
        except:
            logger.error("Failed to send New Guinness Alert Request")

        if not guinness.approved:
            logger.info("Guinness was not approved. Not updating stats")
            return

        # Update statistics
        try:
            stats_client = GuindexStatsClient(logger,
                                              GuindexParameters.STATS_LISTEN_IP,
                                              GuindexParameters.STATS_LISTEN_PORT)

            stats_client.sendNewGuinnessStatsRequest(guinness)
        except:
            logger.error("Failed to send New Guinness Stats Request")


###################
# Pub Serializers #
###################

class PubGetSerializer(serializers.ModelSerializer):
    """
        Serializer for retrieving pub objects
    """

    class ReducedGuinnessSerializer(serializers.ModelSerializer):
        """
            Guinness object serializer that omits pub info
        """

        class Meta:
            model = Guinness
            fields = ['id', 'price', 'creationDate', 'creator']

    # Returns approved Guinness prices associated with this pub
    prices = ReducedGuinnessSerializer(source = 'getApprovedPrices', many = True, read_only = True)

    class Meta:
        model = Pub
        fields = '__all__'


class PubPostSerializer(serializers.ModelSerializer):
    """
        Serializer for creating pub objects.
        Can only set name, latitude and longitude in this operation
        (these are all required fields).
        Leave out closed and servingGuinness fields so that their
        defaults are used.
    """

    class Meta:
        model = Pub

        # Note: Creator is extracted from request object,
        # not message payload so don't include it in fields
        fields = ['name', 'latitude', 'longitude']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def onCreateSuccess(self, pub, request, userProfile):

        logger.info("Successfully created new Pub object")

        # Fields have been correctly set in firstSave at this point

        # Send alerts and updated statistics
        try:
            alerts_client = GuindexAlertsClient(logger,
                                                GuindexParameters.ALERTS_LISTEN_IP,
                                                GuindexParameters.ALERTS_LISTEN_PORT)

            alerts_client.sendNewPubAlertRequest(pub, request)
        except:
            logger.error("Failed to send New Pub Alert Request")

        if not userProfile.user.is_staff:
            logger.info("Not updating stats until contribution is approved")
            return

        # Update statistics
        try:
            stats_client = GuindexStatsClient(logger,
                                              GuindexParameters.STATS_LISTEN_IP,
                                              GuindexParameters.STATS_LISTEN_PORT)

            stats_client.sendNewPubStatsRequest(pub)
        except:
            logger.error("Failed to send New Pub Stats Request")


class PubPatchSerializer:

    class StaffMemberSerializer(serializers.ModelSerializer):

        class Meta:
            model = Pub
            # Below are the 'editable' fields for staff members
            # 'Hidden' fields will be updated accordingly based on contributor permissions
            fields = ['name', 'latitude', 'longitude', 'closed', 'servingGuinness', 
                      'pendingApproval', 'pendingClosed', 'pendingNotServingGuinness', 'pendingApprovalRejectReason']

        def validate(self, data):
            """
                Raise validation error if unknown keys are present
            """
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError("Got unknown fields: {}".format(unknown_keys))

            return data

        def onPatchSuccess(self, pub, request, userProfile):

            logger.info("Successfully patched Pub object")

            # TODO
            # Send alerts and updated statistics

    class NormalUserSerializer(serializers.ModelSerializer):

        class Meta:
            model = Pub
            # Below are the 'editable' fields for normal users
            # 'Hidden' fields will be updated accordingly based on contributor permissions
            fields = ['closed', 'servingGuinness']

        def validate(self, data):
            """
                Raise validation error if unknown keys are present
            """
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError("Got unknown fields: {}".format(unknown_keys))

            return data

        def onPatchSuccess(self, pub, request, userProfile):

            logger.info("Successfully patched Pub object")

            # TODO
            # Send alerts and updated statistics


##########################
# Statistics Serializers #
##########################

class StatisticsSerializer(serializers.ModelSerializer):

    class ReducedPubSerializer(serializers.ModelSerializer):
        """
            Pub object serializer that only returns id, name and most recent price.
            Only applied to pubs in pubsWithPrices list.
        """

        # Return last verified price
        price = serializers.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                         max_digits = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                         source = 'getLastVerifiedGuinness.price')

        class Meta:
            model = Pub
            fields = ['id', 'name', 'price']

    # Return this list and let javascript sort it
    pubsWithPrices = ReducedPubSerializer(many = True, read_only = True)

    class Meta:
        model = StatisticsSingleton
        fields = ['pubsInDb', 'percentageVisited', 'averagePrice', 'standardDeviation',
                  'closedPubs', 'notServingGuinness', 'pubsWithPrices']


###########################
# Contributor Serializers #
###########################

class ContributorGetSerializer(serializers.ModelSerializer):

    username             = serializers.CharField(source = 'user.username')
    pubsVisited          = serializers.IntegerField(source = 'guindexuser.pubsVisited')
    originalPrices       = serializers.IntegerField(source = 'guindexuser.originalPrices')
    currentVerifications = serializers.IntegerField(source = 'guindexuser.currentVerifications')
    usingTelegramAlerts  = serializers.BooleanField(source = 'telegramuser.usingTelegramAlerts')

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'pubsVisited', 'originalPrices', 'currentVerifications',
                  'usingEmailAlerts', 'usingTelegramAlerts']


class ContributorPatchSerializer(serializers.ModelSerializer):

    usingTelegramAlerts = serializers.BooleanField(source = 'telegramuser.usingTelegramAlerts')

    class Meta:
        model = UserProfile
        # Can only patch alert settings
        fields = ['usingEmailAlerts', 'usingTelegramAlerts']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        if 'telegramuser' in self.validated_data:

            # This is a horrible but necessary hack
            # Needed to update telegram alert settings via API
            # since source field does not seem to work when deserializing

            logger.debug("Attempting to update Telegram alerts setting")

            # Update instance field here instead
            self.instance.telegramuser.usingTelegramAlerts = self.validated_data['telegramuser']['usingTelegramAlerts']
            del self.validated_data['telegramuser']

        super(ContributorPatchSerializer, self).save(**kwargs)
