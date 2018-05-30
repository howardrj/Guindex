import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import validate_email as validateEmail
from django.core.mail import send_mail as sendMail
from django.utils import timezone

from rest_framework import serializers

from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import Guinness, GuinnessPendingCreate, GuinnessPendingPatch
from Guindex.models import StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters
from Guindex.GuindexAlertsClient import GuindexAlertsClient

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


class GuinnessPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Guinness
        fields = ['pub', 'price']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        # Check there are no pending contributions for this Guinness
        if len(GuinnessPendingPatch.objects.filter(clonedFrom = self.instance)):
            raise ValidationError('There are already pending contributions for this Guinness')

        return data

    def save(self, **kwargs):

        user = kwargs['user']

        if user.is_staff:
            logger.debug("Contributor is a staff member. Saving changes")
            super(GuinnessPatchSerializer, self).save(**kwargs)
            return

        logger.debug("Contributor is not a staff member. Creating GuinnessPendingPatch object")

        guinness_pending_patch = GuinnessPendingPatch()

        # Copy over original values of instance
        for field in self.instance._meta.fields:
            setattr(guinness_pending_patch, field.name, getattr(self.instance, field.name))

        # Now put validated values on top
        for value in self.validated_data.items():
            setattr(guinness_pending_patch, value[0], value[1])

        # Update relevant fields
        guinness_pending_patch.pk         = None
        guinness_pending_patch.creator    = user
        guinness_pending_patch.clonedFrom = self.instance
        guinness_pending_patch.save()


#####################################
# GuinnessPendingCreate Serializers #
#####################################


class GuinnessPendingCreateGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuinnessPendingCreate
        fields = '__all__'


class GuinnessPendingCreatePatchSerializer(serializers.ModelSerializer):

    approved     = serializers.BooleanField(required   = True,
                                            write_only = True)
    rejectReason = serializers.CharField(max_length  = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required    = False,
                                         write_only  = True,
                                         allow_blank = True)

    class Meta:
        model = GuinnessPendingCreate
        fields = ['approved', 'rejectReason']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        try:
            approved = self._validated_data['approved']
        except:
            logger.error("No approved value included in request")
            return

        if approved:

            logger.info("GuinnessPendingCreate object was approved. Creating new Guinness object")

            guinness = Guinness()

            for field in self.instance._meta.fields:
                setattr(guinness, field.name, getattr(self.instance, field.name))

            # Update relevant fields
            guinness.pk = None
            guinness.save(createPendingCreate = False)

        else:
            logger.info("GuinnessPendingCreate object was not approved")

        try:
            reason = self._validated_data['rejectReason']
        except:
            reason = ""

        logger.info("Deleting pending contribution")
        self.instance.delete()

        # Send accept/reject alert to contributor here
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendGuinnessPendingCreateDecisionAlertRequest(self.instance, approved, reason)
        except:
            logger.error("Failed to send Guinness Pending Create Decision Alert Request")


####################################
# GuinnessPendingPatch Serializers #
####################################


class GuinnessPendingPatchGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuinnessPendingPatch
        fields = '__all__'


class GuinnessPendingPatchPatchSerializer(serializers.ModelSerializer):

    approved     = serializers.BooleanField(required   = True,
                                            write_only = True)
    rejectReason = serializers.CharField(max_length  = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required    = False,
                                         write_only  = True,
                                         allow_blank = True)

    class Meta:
        model = GuinnessPendingPatch
        fields = ['approved', 'rejectReason']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        try:
            approved = self._validated_data['approved']
        except:
            logger.error("No approved value included in request")
            return

        if approved:

            logger.info("GuinnessPendingPatch object was approved. Merging changes")

            guinness = self.instance.clonedFrom

            for field in self.instance._meta.fields:

                # Don't merge these fields
                if field.name in ['id', 'clonedFrom', 'creator', 'creationDate']:
                    continue

                setattr(guinness, field.name, getattr(self.instance, field.name))

            guinness.save()

        else:
            logger.info("GuinnessPendingPatch object was not approved")

        logger.info("Deleting pending contribution")
        self.instance.delete()


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

        # We want both id and username to make populating table more efficient
        creatorId   = serializers.PrimaryKeyRelatedField(source = 'creator.id', read_only = True)
        creatorName = serializers.CharField(source = 'creator.username', read_only = True)

        class Meta:
            model = Guinness
            fields = ['id', 'price', 'creationDate', 'creatorId', 'creatorName']

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
        fields = ['name', 'latitude', 'longitude', 'county']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        # Check latitude, longitude and county combination is valid
        county = data['county']

        min_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LATITUDE"))
        max_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LATITUDE"))
        min_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LONGITUDE"))
        max_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LONGITUDE"))

        if data['latitude'] < min_latitude or data['latitude'] > max_latitude:
            raise ValidationError("Latitude must be between %s - %s for this county." % (min_latitude, max_latitude))

        if data['longitude'] < min_longitude or data['longitude'] > max_longitude:
            raise ValidationError("Longitude must be between %s - %s for this county." % (min_longitude, max_longitude))

        return data


class PubPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pub
        fields = ['name', 'latitude', 'longitude', 'county', 'closed', 'servingGuinness']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        # Check there are no pending contributions for this Pub
        if len(PubPendingPatch.objects.filter(clonedFrom = self.instance)):
            raise ValidationError('There are already pending contributions for this Pub.')

        # Check fields have actually changed, don't want to send alerts for no reason
        changed_fields = False
        for field in data.keys():

            if getattr(self.instance, field) != data[field]:
                changed_fields = True
                break

        if not changed_fields:
            raise ValidationError('You have not altered any fields.')

        # Check latitude, longitude and county combination is valid
        county    = self.instance.county if not 'county' in data else data['county']
        latitude  = self.instance.latitude if not 'latitude' in data else data['latitude']
        longitude = self.instance.longitude if not 'longitude' in data else data['longitude']

        min_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LATITUDE"))
        max_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LATITUDE"))
        min_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LONGITUDE"))
        max_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LONGITUDE"))

        if latitude < min_latitude or latitude > max_latitude:
            raise ValidationError("Latitude must be between %s - %s for this county." % (min_latitude, max_latitude))

        if longitude < min_longitude or longitude > max_longitude:
            raise ValidationError("Longitude must be between %s - %s for this county." % (min_longitude, max_longitude))

        return data

    def save(self, **kwargs):

        user = kwargs['user']

        # Get changed fields and add to JSONizable object
        changed_fields = {}
        for value in self.validated_data.items():
            if value[1] != getattr(self.instance, value[0]):
                changed_fields[value[0]] = [getattr(self.instance, value[0]), value[1]]

        if user.is_staff:
            logger.debug("Contributor is a staff member. Saving changes")

            # Send pub patch alert
            try:
                guindex_alerts_client = GuindexAlertsClient()
            except:
                logger.error("Failed to create GuindexAlertsClient object")

            try:
                guindex_alerts_client.sendPubPatchAlertRequest(self.instance,
                                                               user,
                                                               changed_fields,
                                                               timezone.now(),
                                                               True)
            except:
                logger.error("Failed to send Pub Patch Alert Request")

            # Bit of a risk saving after sending request but it makes tracking diffs easier
            super(PubPatchSerializer, self).save(**kwargs)

            return

        logger.debug("Contributor is not a staff member. Creating PubPendingPatch object")

        pub_pending_patch = PubPendingPatch()

        # Copy over original values of instance
        for field in self.instance._meta.fields:
            setattr(pub_pending_patch, field.name, getattr(self.instance, field.name))

        # Now put validated values on top
        for value in self.validated_data.items():
            setattr(pub_pending_patch, value[0], value[1])

        # Update relevant fields
        pub_pending_patch.pk         = None
        pub_pending_patch.creator    = user
        pub_pending_patch.clonedFrom = self.instance
        pub_pending_patch.save()

        # Send pending pub patch alert
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendPubPatchAlertRequest(self.instance,
                                                           user,
                                                           changed_fields,
                                                           timezone.now(),
                                                           False)
        except:
            logger.error("Failed to send Pub Patch Alert Request")


################################
# PubPendingCreate Serializers #
################################


class PubPendingCreateGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PubPendingCreate
        fields = '__all__'


class PubPendingCreatePatchSerializer(serializers.ModelSerializer):

    approved     = serializers.BooleanField(required   = True,
                                            write_only = True)
    rejectReason = serializers.CharField(max_length  = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required    = False,
                                         write_only  = True,
                                         allow_blank = True)

    class Meta:
        model = PubPendingCreate
        fields = ['approved', 'rejectReason']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        try:
            approved = self._validated_data['approved']
        except:
            logger.error("No approved value included in request")
            return

        if approved:

            logger.info("PubPendingCreate object was approved. Creating new Pub object")

            pub = Pub()

            for field in self.instance._meta.fields:
                setattr(pub, field.name, getattr(self.instance, field.name))

            # Update relevant fields
            pub.pk = None
            pub.save(createPendingCreate = False)

        else:
            logger.info("PubPendingCreate object was not approved")

        try:
            reason = self._validated_data['rejectReason']
        except:
            reason = ""

        logger.info("Deleting pending contribution")
        self.instance.delete()

        # Send accept/reject alert to contributor here
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendPubPendingCreateDecisionAlertRequest(self.instance, approved, reason)
        except:
            logger.error("Failed to send Pub Pending Create Decision Alert Request")


###############################
# PubPendingPatch Serializers #
###############################


class PubPendingPatchGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PubPendingPatch
        fields = '__all__'


class PubPendingPatchPatchSerializer(serializers.ModelSerializer):

    approved     = serializers.BooleanField(required   = True,
                                            write_only = True)
    rejectReason = serializers.CharField(max_length  = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required    = False,
                                         write_only  = True,
                                         allow_blank = True)

    class Meta:
        model = PubPendingPatch
        fields = ['approved', 'rejectReason']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        try:
            approved = self._validated_data['approved']
        except:
            logger.error("No approved value included in request")
            return

        pub = self.instance.clonedFrom
        pub_name   = pub.name
        pub_county = pub.county

        # Get changed fields and add to JSONizable object
        changed_fields = {}
        for field in self.instance._meta.fields:

            # Don't merge these fields
            if field.name in ['id', 'clonedFrom', 'creator', 'creationDate']:
                continue

            if getattr(self.instance, field.name) != getattr(pub, field.name):
                changed_fields[field.name] = [getattr(pub, field.name), getattr(self.instance, field.name)]

        if approved:

            logger.info("PubPendingPatch object was approved. Merging changes")

            # Send pub change update
            try:
                guindex_alerts_client = GuindexAlertsClient()
            except:
                logger.error("Failed to create GuindexAlertsClient object")

            try:
                guindex_alerts_client.sendPubPatchAlertRequest(pub, 
                                                               self.instance.creator,
                                                               changed_fields,
                                                               self.instance.creationDate,
                                                               True)
            except:
                logger.error("Failed to send Pub Patch Alert Request")

            # Bit of a risk saving after sending request but it makes tracking diffs easier
            for field in self.instance._meta.fields:

                # Don't merge these fields
                if field.name in ['id', 'clonedFrom', 'creator', 'creationDate']:
                    continue

                # Merge new fields
                setattr(pub, field.name, getattr(self.instance, field.name))

            pub.save()

        else:
            logger.info("PubPendingPatch object was not approved")

        try:
            reason = self._validated_data['rejectReason']
        except:
            reason = ""

        logger.info("Deleting pending contribution")
        self.instance.delete()

        # Send pub change accept/reject to contributor
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendPubPendingPatchDecisionAlertRequest(pub_name,
                                                                          pub_county,
                                                                          self.instance.creator.id,
                                                                          changed_fields,
                                                                          timezone.now(),
                                                                          approved,
                                                                          reason)
        except:
            logger.error("Failed to send Pub Pending Patch Decision Alert Request")


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
            fields = ['id', 'name', 'county', 'price']

    # Return this list and let javascript sort it
    pubsWithPrices = ReducedPubSerializer(many = True, read_only = True)

    class Meta:
        model = StatisticsSingleton
        fields = ['pubsInDb', 'percentageVisited', 'averagePrice', 'standardDeviation',
                  'closedPubs', 'notServingGuinness', 'pubsWithPrices', 'lastCalculated']


###########################
# Contributor Serializers #
###########################


class ContributorGetSerializer(serializers.ModelSerializer):

    pubsVisited          = serializers.IntegerField(source = 'guindexuser.pubsVisited')
    originalPrices       = serializers.IntegerField(source = 'guindexuser.originalPrices')
    currentVerifications = serializers.IntegerField(source = 'guindexuser.currentVerifications')

    class Meta:
        model = User
        fields = ['id', 'username', 'pubsVisited', 'originalPrices', 'currentVerifications']


class ContributorDetailedGetSerializer(serializers.ModelSerializer):

    pubsVisited           = serializers.IntegerField(source = 'guindexuser.pubsVisited')
    originalPrices        = serializers.IntegerField(source = 'guindexuser.originalPrices')
    currentVerifications  = serializers.IntegerField(source = 'guindexuser.currentVerifications')
    usingEmailAlerts      = serializers.BooleanField(source = 'guindexuser.usingEmailAlerts')
    usingTelegramAlerts   = serializers.BooleanField(source = 'telegramuser.usingTelegramAlerts')
    telegramActivated     = serializers.BooleanField(source = 'telegramuser.activated')
    telegramActivationKey = serializers.CharField(source = 'telegramuser.activationKey')

    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'pubsVisited', 'originalPrices', 'currentVerifications',
                  'usingEmailAlerts', 'usingTelegramAlerts', 'telegramActivated', 'telegramActivationKey']

class ContributorPatchSerializer(serializers.ModelSerializer):

    usingEmailAlerts    = serializers.BooleanField(source = 'guindexuser.usingEmailAlerts')
    usingTelegramAlerts = serializers.BooleanField(source = 'telegramuser.usingTelegramAlerts')

    class Meta:
        model = User
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

    def validate_usingTelegramAlerts(self, usingTelegramAlerts):

        if not self.instance.telegramuser.activated:
            logger.error("User has not activated Telegram account yet")
            raise ValidationError("You must activate your Telegram account before Telegram alerts can be enabled.")

        return usingTelegramAlerts

    def save(self, **kwargs):

        if 'telegramuser' in self.validated_data:

            # This is a horrible but necessary hack
            # Needed to update telegram alert settings via API
            # since source field does not seem to work when deserializing

            logger.debug("Attempting to update Telegram alerts setting")

            # Update and save instance field here instead
            self.instance.telegramuser.usingTelegramAlerts = self.validated_data['telegramuser']['usingTelegramAlerts']
            self.instance.telegramuser.save()
            del self.validated_data['telegramuser']

        if 'guindexuser' in self.validated_data:

            # This is a horrible but necessary hack
            # Needed to update email alert settings via API
            # since source field does not seem to work when deserializing

            logger.debug("Attempting to update Email alerts setting")

            # Update and save instance field here instead
            self.instance.guindexuser.usingEmailAlerts = self.validated_data['guindexuser']['usingEmailAlerts']
            self.instance.guindexuser.save()
            del self.validated_data['guindexuser']

        super(ContributorPatchSerializer, self).save(**kwargs)


#######################
# Contact Serializers #
#######################

class ContactSerializer(serializers.Serializer):

    name    = serializers.CharField(max_length  = GuindexParameters.MAX_CONTACT_FORM_NAME_LEN,
                                    required    = True,
                                    write_only  = True,
                                    allow_blank = False)

    email   = serializers.CharField(max_length  = GuindexParameters.MAX_CONTACT_FORM_EMAIL_LEN,
                                    required    = True,
                                    write_only  = True,
                                    allow_blank = False)

    subject = serializers.CharField(max_length  = GuindexParameters.MAX_CONTACT_FORM_SUBJECT_LEN,
                                    required    = True,
                                    write_only  = True,
                                    allow_blank = False)

    message = serializers.CharField(max_length  = GuindexParameters.MAX_CONTACT_FORM_MESSAGE_LEN,
                                    required    = True,
                                    write_only  = True,
                                    allow_blank = False)

    def validate_email(self, email):

        try:
            validateEmail(email)
        except:
            raise ValidationError("Please use valid email.")

        return email

    def create(self, validated_data):
        """
            Sends contact form message to Guindex email
            and sender.
        """

        name    = validated_data['name']
        email   = validated_data['email']
        subject = validated_data['subject']
        message = validated_data['message']

        sender    = settings.EMAIL_HOST_USER
        receivers = [sender, ] # Only send to ourselves for now (prevents spamming someone else's inbox)
        subject   = "Guindex Contact Message from %s (%s) - %s" % (name, email, subject)

        try:
            sendMail(subject, message, sender, receivers)
        except:
            logger.error("Failed to send contact email")

        return self
