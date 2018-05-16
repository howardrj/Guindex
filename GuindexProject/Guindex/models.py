import logging
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from Guindex.GuindexParameters import GuindexParameters
from Guindex.GuindexAlertsClient import GuindexAlertsClient

logger = logging.getLogger(__name__)


##############
# Pub Models #
##############

class PubBase(models.Model):

    creator         = models.ForeignKey(User,
                                        null    = True,
                                        blank   = True,
                                        default = None)
    creationDate    = models.DateTimeField(auto_now_add = True)
    name            = models.CharField(max_length = GuindexParameters.MAX_PUB_NAME_LEN)
    county          = models.CharField(max_length = GuindexParameters.MAX_COUNTY_NAME_LEN, 
                                       choices    = [(x, x) for x in GuindexParameters.SUPPORTED_COUNTIES],
                                       default    = 'Dublin')
    longitude       = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                          max_digits     = GuindexParameters.GPS_COORD_MAX_DIGITS)
    latitude        = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                          max_digits     = GuindexParameters.GPS_COORD_MAX_DIGITS)
    mapLink         = models.TextField(default = "") # Set this in save method
    closed          = models.BooleanField(default = False)
    servingGuinness = models.BooleanField(default = True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "'%s(%s)'" % (self.name, str(self.id) if self.id else "No DB ID")


class Pub(PubBase):
    """
        Table that stores list of all approved pubs
    """

    # Only in this state can we start adding prices to the Pub object
    prices = models.ManyToManyField('Guinness', related_name = 'prices')

    def getApprovedPrices(self):
        """
            Return list of prices that have been approved
        """

        return self.prices.all()

    def getFirstVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        for price in self.prices.all():
            return price

        return None

    def getLastVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        for price in self.prices.all()[::-1]:
            return price

        return None

    def save(self, *args, **kwargs):

        logger.debug("Saving Pub")

        if self.pk is None:

            logger.debug("First save of Pub object")

            # Set map link
            self.mapLink = GuindexParameters.MAP_LINK_STRING % (self.latitude, self.longitude)

            create_pending_create = True

            try:
                create_pending_create = kwargs['createPendingCreate']
                kwargs.pop('createPendingCreate')
            except:
                logger.debug("createPendingCreate not in kwargs")

            # If not a staff member, save it to PubPendingCreates table instead
            if not self.creator.is_staff and create_pending_create:
                self.createPendingCreate()
                return

            super(Pub, self).save(*args, **kwargs)

            # Send new pub alert here (Make sure save works first)
            try:
                guindex_alerts_client = GuindexAlertsClient()
            except:
                logger.error("Failed to create GuindexAlertsClient object")

            try:
                guindex_alerts_client.sendPubCreateAlertRequest(self, True)
            except:
                logger.error("Failed to send Pub Create Alert Request")
        else:
            super(Pub, self).save(*args, **kwargs)

    def createPendingCreate(self):

        logger.debug("Creator is not a staff member. Creating PubPendingCreate object instead")

        pub_pending_create = PubPendingCreate()

        for field in self._meta.fields:
            setattr(pub_pending_create, field.name, getattr(self, field.name))

        pub_pending_create.pk = None
        pub_pending_create.save()

        # Send new pub alert here (Make sure save works first)
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendPubCreateAlertRequest(pub_pending_create, False)
        except:
            logger.error("Failed to send Pub Create Alert Request")


class PubPendingCreate(PubBase):
    """
        Table that stores list of pending pub creations
    """


class PubPendingPatch(PubBase):
    """
        Table that stores list of pending pub patches
    """

    clonedFrom = models.ForeignKey(Pub)


###################
# Guinness Models #
###################

class GuinnessBase(models.Model):

    creator      = models.ForeignKey(User,
                                     null    = True,
                                     blank   = True,
                                     default = None)
    creationDate = models.DateTimeField(auto_now_add = True)
    price        = models.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                       max_digits     = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                       validators     = [MinValueValidator(Decimal(GuindexParameters.MIN_GUINNESS_PRICE))])
    pub          = models.ForeignKey(Pub)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "'%s(%s) - Price: %.2f'" % (self.pub, str(self.id) if self.id else "No DB ID", self.price)


class Guinness(GuinnessBase):
    """
        Table that stores list of all approved Guinness prices
    """

    def save(self, *args, **kwargs):

        logger.debug("Saving Guinness")

        if self.pk is None:

            logger.debug("First save of Guinness object")

            create_pending_create = True

            try:
                create_pending_create = kwargs['createPendingCreate']
                kwargs.pop('createPendingCreate')
            except:
                logger.debug("createPendingCreate not in kwargs")

            # If not a staff member, save it to GuinnessPendingCreates table instead
            if not self.creator.is_staff and create_pending_create:
                self.createPendingCreate()
                return

            super(Guinness, self).save(*args, **kwargs)

            # Append to pub prices list (must have DB ID at this point)
            self.pub.prices.add(self)

            # Send new price alert here (Make sure save works first)
            try:
                guindex_alerts_client = GuindexAlertsClient()
            except:
                logger.error("Failed to create GuindexAlertsClient object")

            try:
                guindex_alerts_client.sendGuinnessCreateAlertRequest(self, True)
            except:
                logger.error("Failed to send Guinness Create Alert Request")

        else:
            super(Guinness, self).save(*args, **kwargs)

    def createPendingCreate(self):

        logger.debug("Creator is not a staff member. Creating GuinnessPendingCreate object instead")

        guinness_pending_create = GuinnessPendingCreate()

        for field in self._meta.fields:
            setattr(guinness_pending_create, field.name, getattr(self, field.name))

        guinness_pending_create.pk = None
        guinness_pending_create.save()

        # Send new price alert here (Make sure save works first)
        try:
            guindex_alerts_client = GuindexAlertsClient()
        except:
            logger.error("Failed to create GuindexAlertsClient object")

        try:
            guindex_alerts_client.sendGuinnessCreateAlertRequest(guinness_pending_create, False)
        except:
            logger.error("Failed to send Guinness Create Alert Request")


class GuinnessPendingCreate(GuinnessBase):
    """
        Table that stores list of pending Guinness creations
    """


class GuinnessPendingPatch(GuinnessBase):
    """
        Table that stores list of pending Guinness patches
    """

    clonedFrom = models.ForeignKey(Guinness)


#####################
# Statistics Models #
#####################

class StatisticsSingleton(models.Model):
    """
        This is a singleton class to store statistics.
    """

    pubsInDb           = models.IntegerField(default = 0)
    pubsWithPrices     = models.ManyToManyField(Pub) # Use this to return cheapest/most expensive pubs
    averagePrice       = models.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                             max_digits     = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                             default        = Decimal('0.0'))
    standardDeviation  = models.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES + 1,
                                             max_digits     = 12,
                                             default        = Decimal('0.0'))
    percentageVisited  = models.DecimalField(decimal_places = 2, max_digits = 5,  default = Decimal('0.0'))
    closedPubs         = models.IntegerField(default = 0)
    notServingGuinness = models.IntegerField(default = 0)
    lastCalculated     = models.DateTimeField(auto_now = True)

    def __unicode__(self):

        return "'StatisticsSingleton'"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(StatisticsSingleton, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk = 1)
        return obj


######################
# GuindexUser Models #
######################

class GuindexUser(models.Model):
    """
        Class to keep track of user contributions.
    """

    user                 = models.OneToOneField(User,
                                                null         = True,
                                                blank        = True,
                                                default      = None,
                                                related_name = 'guindexuser')
    pubsVisited          = models.IntegerField(default = 0)
    originalPrices       = models.IntegerField(default = 0)
    currentVerifications = models.IntegerField(default = 0)
    lastCalculated       = models.DateTimeField(auto_now = True)
    usingEmailAlerts     = models.BooleanField(default = False)
