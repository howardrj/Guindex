import logging

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from rest_framework import serializers

from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import Guinness, GuinnessPendingCreate, GuinnessPendingPatch
from Guindex.models import StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

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

        logger.info("Deleting pending contribution")
        self.instance.delete()


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
        fields = ['name', 'latitude', 'longitude']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        return data


class PubPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pub
        fields = ['name', 'latitude', 'longitude', 'closed', 'servingGuinness']

    def validate(self, data):
        """
            Raise validation error if unknown keys are present
        """
        unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

        if unknown_keys:
            raise ValidationError("Got unknown fields: {}".format(unknown_keys))

        # Check there are no pending contributions for this Pub
        if len(PubPendingPatch.objects.filter(clonedFrom = self.instance)):
            raise ValidationError('There are already pending contributions for this Pub')

        return data

    def save(self, **kwargs):

        user = kwargs['user']

        if user.is_staff:
            logger.debug("Contributor is a staff member. Saving changes")
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
            logger.info("PubPendingCreate object was approved")

        logger.info("Deleting pending contribution")
        self.instance.delete()


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

        if approved:

            logger.info("PubPendingPatch object was approved. Merging changes")

            pub = self.instance.clonedFrom

            for field in self.instance._meta.fields:

                # Don't merge these fields
                if field.name in ['id', 'clonedFrom', 'creator', 'creationDate']:
                    continue

                setattr(pub, field.name, getattr(self.instance, field.name))

            pub.save()

        else:
            logger.info("GuinnessPendingCreate object was not approved")

        logger.info("Deleting pending contribution")
        self.instance.delete()


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
                  'closedPubs', 'notServingGuinness', 'pubsWithPrices', 'lastCalculated']


###########################
# Contributor Serializers #
###########################


class ContributorGetSerializer(serializers.ModelSerializer):

    pubsVisited          = serializers.IntegerField(source = 'guindexuser.pubsVisited')
    originalPrices       = serializers.IntegerField(source = 'guindexuser.originalPrices')
    currentVerifications = serializers.IntegerField(source = 'guindexuser.currentVerifications')
    usingTelegramAlerts  = serializers.BooleanField(source = 'telegramuser.usingTelegramAlerts')

    class Meta:
        model = User
        fields = ['id', 'username', 'pubsVisited', 'originalPrices', 'currentVerifications',
                  'usingEmailAlerts', 'usingTelegramAlerts']


class ContributorPatchSerializer(serializers.ModelSerializer):

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
