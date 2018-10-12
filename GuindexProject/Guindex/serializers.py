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
from Guindex.models import Guinness, GuinnessPendingCreate
from Guindex.models import StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


########################
# Guinness Serializers #
########################


class GuinnessSerializer(serializers.ModelSerializer):
    """
        Serializer for creating and retrieving Guinness objects.
    """

    class Meta:
        model = Guinness
        fields = '__all__'

        # This is a nested resource so pub ID is taken from url
        read_only_fields = ('id', 'creator', 'creationDate', 'pub')

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data

    def save(self, **kwargs):

        # Add user to validated data
        self.validated_data['creator'] = self.context['request'].user

        # Add pub to validated data
        # TODO This needs to be more robust in case format of url changes
        pub_id = self.context['request'].path.split('/')[3]
        self.validated_data['pub'] = Pub.objects.get(id = int(pub_id))

        super(GuinnessSerializer, self).save(**kwargs)


#####################################
# GuinnessPendingCreate Serializers #
#####################################


class GuinnessPendingCreateSerializer(serializers.ModelSerializer):
    """
        Serializer for updating and retrieving GuinnessPendingCreate objects.
    """

    approved = serializers.BooleanField(help_text = 'Is contribution approved?',
                                        required = True,
                                        write_only = True)

    rejectReason = serializers.CharField(help_text = 'Reason for rejecting contribution',
                                         max_length = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required = False,
                                         write_only = True,
                                         allow_blank = True)

    creatorName = serializers.CharField(help_text = 'Username of creator',
                                        source = 'creator.username',
                                        read_only = True,
                                        max_length = 100)

    pubName = serializers.CharField(help_text = 'Name of the pub this price belongs to',
                                    source = 'pub.name',
                                    read_only = True,
                                    max_length = GuindexParameters.MAX_PUB_NAME_LEN)

    pubCounty = serializers.CharField(help_text = 'County of the pub this price belongs to',
                                      source = 'pub.county',
                                      read_only = True,
                                      max_length = 50)

    class Meta:
        model = GuinnessPendingCreate
        fields = '__all__'
        read_only_fields = ('id', 'creationDate', 'creator', 'creatorName', 
                            'price', 'pub', 'pubName', 'pubCounty', 'starRating')

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

            # Overwrite creation date so alerts will register change
            guinness.creationDate = timezone.now()

            guinness.pk = None
            guinness.save(createPendingCreate = False)

        else:
            logger.info("GuinnessPendingCreate object was not approved")

        logger.info("Deleting pending contribution")

        reject_reason = self._validated_data.get('rejectReason', "")

        self.instance.delete(approved = approved,
                             rejectReason = reject_reason)


###################
# Pub Serializers #
###################

class PubSerializer(serializers.ModelSerializer):
    """
        Serializer for creating, updating and retrieving Pub objects.
    """

    class Meta:
        model = Pub
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'creationDate', 'mapLink', 'averageRating',
                            'lastPrice', 'lastSubmissionTime')

    def validate(self, data):
        """
            Raise validation error if unknown keys are present,
            invalid lat/long combination or attempting to edit
            pub with patches waiting approval.
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        if self.instance and self.instance.pk:  # If Pub already exists i.e. patch

            # Check there are no pending contributions for this Pub
            if len(PubPendingPatch.objects.filter(clonedFrom = self.instance)):
                raise ValidationError('There are already pending patches for this Pub.')

            # Check fields have actually changed
            changed_fields = False

            for field in data.keys():

                if getattr(self.instance, field) != data[field]:
                    changed_fields = True
                    break

            if not changed_fields:
                raise ValidationError('You have not altered any fields.')

            # Check latitude, longitude and county combination is valid
            county    = self.instance.county if 'county' not in data else data['county']
            latitude  = self.instance.latitude if 'latitude' not in data else data['latitude']
            longitude = self.instance.longitude if 'longitude' not in data else data['longitude']

            self._validateLatLongCountyCombo(county, latitude, longitude)

        else:  # If Pub does not already exist i.e. create
            self._validateLatLongCountyCombo(data['county'], data['latitude'], data['longitude'])

        return data

    def save(self, **kwargs):

        user = self.context['request'].user

        if self.instance and self.instance.pk and not user.is_staff:

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

        else:  # If Pub does not already exist i.e. create

            # Add user to validated data
            self.validated_data['creator'] = user

            super(PubSerializer, self).save(**kwargs)

    def _validateLatLongCountyCombo(self, county, latitude, longitude):

        min_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LATITUDE"))
        max_latitude  = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LATITUDE"))
        min_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MIN_LONGITUDE"))
        max_longitude = Decimal(getattr(GuindexParameters, "GPS_" + county.upper() + "_MAX_LONGITUDE"))

        if latitude < min_latitude or latitude > max_latitude:
            raise ValidationError("Latitude must be between %s - %s for this county." % (min_latitude, max_latitude))

        if longitude < min_longitude or longitude > max_longitude:
            raise ValidationError("Longitude must be between %s - %s for this county." % (min_longitude, max_longitude))

################################
# PubPendingCreate Serializers #
################################


class PubPendingCreateSerializer(serializers.ModelSerializer):
    """
        Serializer for updating and retrieving PubPendingCreate objects.
    """

    approved = serializers.BooleanField(help_text = 'Is contribution approved?',
                                        required = True,
                                        write_only = True)

    rejectReason = serializers.CharField(help_text = 'Reason for rejecting contribution',
                                         max_length = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required = False,
                                         write_only = True,
                                         allow_blank = True)

    creatorName = serializers.CharField(help_text = 'Username of creator',
                                        source = 'creator.username',
                                        read_only = True,
                                        max_length = 100)

    class Meta:
        model = PubPendingCreate
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'creatorName', 'creationDate', 'name', 'county',
                            'longitude', 'latitude', 'mapLink', 'closed', 'averageRating',
                            'servingGuinness')

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

            # Overwrite creation date so alerts will register change
            pub.creationDate = timezone.now()

            # Update relevant fields
            pub.pk = None
            pub.save(createPendingCreate = False)

        else:
            logger.info("PubPendingCreate object was not approved")

        logger.info("Deleting pending contribution")

        reject_reason = self._validated_data.get('rejectReason', "")

        self.instance.delete(approved = approved,
                             rejectReason = reject_reason)


###############################
# PubPendingPatch Serializers #
###############################


class PubPendingPatchSerializer(serializers.ModelSerializer):

    approved = serializers.BooleanField(help_text = 'Is contribution approved?',
                                        required = True,
                                        write_only = True)

    rejectReason = serializers.CharField(help_text = 'Reason for rejecting contribution',
                                         max_length = GuindexParameters.REJECT_REASON_MAX_LEN,
                                         required = False,
                                         write_only = True,
                                         allow_blank = True)

    creatorName = serializers.CharField(help_text = 'Username of patch contributor',
                                        source = 'creator.username',
                                        read_only = True,
                                        max_length = 100)

    pubNameOrig = serializers.CharField(help_text = 'Name of the pub this patch applies to',
                                        source = 'clonedFrom.name',
                                        read_only = True,
                                        max_length = GuindexParameters.MAX_PUB_NAME_LEN)

    pubCountyOrig = serializers.CharField(help_text = 'County of the pub this patch applies to',
                                          source = 'clonedFrom.county',
                                          read_only = True,
                                          max_length = 50)

    proposedPatches = serializers.JSONField(help_text = 'List of proposed changes (original value first)',
                                            read_only = True,
                                            source = 'getProposedPatches')
    

    class Meta:
        model = PubPendingPatch
        fields = '__all__'
        read_only_fields = ('id', 'name', 'latitude', 'longitude', 'creator', 'creationDate',
                            'servingGuinness', 'closed', 'averageRating', 'county', 'mapLink', 
                            'clonedFrom', 'creatorName', 'pubNameOrig', 'pubCountyOrig', 'proposedPatches')

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

        if approved:

            logger.info("PubPendingPatch object was approved. Merging changes")

            # Bit of a risk saving after sending request but it makes tracking diffs easier
            for field in self.instance._meta.fields:

                # Don't merge these fields
                if field.name in ['id', 'clonedFrom', 'creator', 'creationDate', 'mapLink']:
                    continue

                # Merge new fields
                setattr(pub, field.name, getattr(self.instance, field.name))

            pub.save()

        else:
            logger.info("PubPendingPatch object was not approved")

        logger.info("Deleting pending contribution")

        reject_reason = self._validated_data.get('rejectReason', "")

        self.instance.delete(approved = approved,
                             rejectReason = reject_reason)


##########################
# Statistics Serializers #
##########################


class StatisticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatisticsSingleton
        fields = '__all__'


###########################
# Contributor Serializers #
###########################

class ContributorSerializer(serializers.ModelSerializer):

    pubsVisited = serializers.IntegerField(help_text = 'Number of pubs visited by this contributor',
                                           read_only = True,
                                           source = 'guindexuser.pubsVisited')

    originalPrices = serializers.IntegerField(help_text = 'Number of first prices for a pub submitted by this contributor',
                                              read_only = True,
                                              source = 'guindexuser.originalPrices')

    currentVerifications = serializers.IntegerField(help_text = 'Number of current verifactions for this contributor',
                                                    read_only = True,
                                                    source = 'guindexuser.currentVerifications')

    isDeveloper = serializers.IntegerField(help_text = 'Is this contributor a developer of the Guindex website?',
                                           read_only = True,
                                           source = 'guindexuser.isDeveloper')

    usingEmailAlerts = serializers.BooleanField(help_text = 'Does this contributor have email alerts enabled?',
                                                source = 'guindexuser.usingEmailAlerts')

    usingTelegramAlerts = serializers.BooleanField(help_text = 'Does this contributor have Telegram alerts enabled?',
                                                   source = 'telegramuser.usingTelegramAlerts')

    telegramActivated = serializers.BooleanField(help_text = 'Does this contributor have their Telegram account activated?',
                                                 read_only = True,
                                                 source = 'telegramuser.activated')

    telegramActivationKey = serializers.CharField(help_text = 'Telegram activation key for this contributor.',
                                                  read_only = True,
                                                  source = 'telegramuser.activationKey')

    class Meta:
        model = User
        fields = ('id', 'username', 'is_staff', 'pubsVisited', 'originalPrices',
                  'currentVerifications', 'usingEmailAlerts', 'usingTelegramAlerts',
                  'telegramActivated', 'telegramActivationKey', 'isDeveloper')
        # Can only patch alert settings
        read_only_fields = ('id', 'username', 'is_staff', 'pubsVisited', 'originalPrices',
                            'currentVerifications', 'telegramActivated', 'telegramActivationKey')

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

        super(ContributorSerializer, self).save(**kwargs)


#######################
# Contact Serializers #
#######################

class ContactSerializer(serializers.Serializer):

    name = serializers.CharField(help_text = 'Name of message poster',
                                 max_length = GuindexParameters.MAX_CONTACT_FORM_NAME_LEN,
                                 required = True,
                                 write_only = True,
                                 allow_blank = False)

    email = serializers.CharField(help_text = 'Email of message poster (for sending replies)',
                                  max_length = GuindexParameters.MAX_CONTACT_FORM_EMAIL_LEN,
                                  required = True,
                                  write_only = True,
                                  allow_blank = False)

    subject = serializers.CharField(help_text = 'Subject of message',
                                    max_length = GuindexParameters.MAX_CONTACT_FORM_SUBJECT_LEN,
                                    required = True,
                                    write_only = True,
                                    allow_blank = False)

    message = serializers.CharField(help_text = 'Message body',
                                    max_length = GuindexParameters.MAX_CONTACT_FORM_MESSAGE_LEN,
                                    required = True,
                                    write_only = True,
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
        receivers = [sender, ]  # Only send to ourselves for now (prevents spamming someone else's inbox)
        subject   = "Guindex Contact Message from %s (%s) - %s" % (name, email, subject)

        try:
            sendMail(subject, message, sender, receivers)
        except:
            logger.error("Failed to send contact email")

        return self
