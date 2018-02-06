import logging
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from GuindexParameters import GuindexParameters

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


class Pub(models.Model):

    name                                 = models.CharField(max_length = GuindexParameters.MAX_PUB_NAME_LEN,
                                                            unique     = True)
    longitude                            = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                                               max_digits     = GuindexParameters.GPS_COORD_MAX_DIGITS,
                                                               validators     = [MinValueValidator(Decimal(GuindexParameters.GPS_DUBLIN_MIN_LONGITUDE)),
                                                                                 MaxValueValidator(Decimal(GuindexParameters.GPS_DUBLIN_MAX_LONGITUDE))])
    latitude                             = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                                               max_digits     = GuindexParameters.GPS_COORD_MAX_DIGITS,
                                                               validators     = [MinValueValidator(Decimal(GuindexParameters.GPS_DUBLIN_MIN_LATITUDE)),
                                                                                 MaxValueValidator(Decimal(GuindexParameters.GPS_DUBLIN_MAX_LATITUDE))])
    mapLink                              = models.TextField(default = "") # Set this in save method
    closed                               = models.BooleanField(default = False)
    servingGuinness                      = models.BooleanField(default = True)
    pendingApproval                      = models.BooleanField(default = False) # In case non-staff member wants to add a pub
    pendingApprovalRejected              = models.BooleanField(default = False)
    pendingApprovalContributor           = models.ForeignKey(UserProfile,
                                                             null         = True,
                                                             blank        = True,
                                                             related_name = 'pendingAdder',
                                                             default      = None)
    pendingApprovalTime                  = models.DateTimeField(auto_now_add = True)
    pendingClosed                        = models.BooleanField(default = False) # In case non-staff member closes pub
    pendingClosedContributor             = models.ForeignKey(UserProfile,
                                                             null         = True,
                                                             blank        = True,
                                                             related_name = 'pendingCloser',
                                                             default      = None)
    pendingClosedTime                    = models.DateTimeField(auto_now_add = True)
    pendingNotServingGuinness            = models.BooleanField(default = False) # In case non-staff member marks pub as not serving Guinness
    pendingNotServingGuinnessContributor = models.ForeignKey(UserProfile,
                                                             null         = True,
                                                             blank        = True,
                                                             related_name = 'pendingNotServingGuinnessMarker',
                                                             default      = None)
    pendingNotServingGuinnessTime        = models.DateTimeField(auto_now_add = True)
    prices                               = models.ManyToManyField('Guinness',
                                                                  related_name = 'prices')

    def __unicode__(self):

        return "'%s(%d)'" % (self.name, self.id)

    def getFirstVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        for price in self.prices.all():

            if price.approved:
                return price

        return None

    def getLastVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        for price in self.prices.all()[::-1]:

            if price.approved:
                return price

        return None

    def getApprovedPrices(self):
        """
            Return list of prices that have been approved
        """

        return self.prices.filter(approved = True)

    def save(self, *args, **kwargs):

        logger.debug("Saving Pub")

        if self.pk is None:
            self.firstSave()
        else:
            logger.debug("Not first save of Pub object")

            # Check if we need to send events
            saved_pub = Pub.objects.get(id = self.pk)

            if not saved_pub.closed and self.closed:
                self.closedSave()

            if saved_pub.servingGuinness and not self.servingGuinness:
                self.notServingGuinnessSave()

        super(Pub, self).save(*args, **kwargs)

    def firstSave(self):

        logger.debug("First save of Pub object")

        # Set map link
        self.mapLink = GuindexParameters.MAP_LINK_STRING % (self.latitude, self.longitude)

        # Set servingGuinness field to true since
        # it is a BooleanField and rest framework sets it to false by default
        self.servingGuinness = True

        # Always set pub closed on creation
        self.closed = False

        # Set pendingApproval field to True if user is not a staff member
        self.pendingApproval = not self.pendingApprovalContributor.user.is_staff 

    def closedSave(self):

        logger.debug("Saving Pub after it has been marked as closed")

        # Send alerts
        try:
            alerts_client = GuindexAlertsClient(logger,
                                                GuindexParameters.ALERTS_LISTEN_IP,
                                                GuindexParameters.ALERTS_LISTEN_PORT)
            alerts_client.sendPubClosedAlertRequest(self)
        except:
            logger.error("Failed to send New Pub Alert Request")

        # Update stats if necessary
        if self.pendingApprovalContributor.user.is_staff:
            self.pendingApproval = False
            try:
                stats_client = GuindexStatsClient(logger,
                                                  GuindexParameters.STATS_LISTEN_IP,
                                                  GuindexParameters.STATS_LISTEN_PORT)
                stats_client.sendNewPubStatsRequest(self)
            except:
                logger.error("Failed to send New Pub Stats Request")
        else:
            logger.info("Not updating stats until contribution is approved")
            self.pendingApproval = True

    def notServingGuinnessSave(self):

        logger.debug("Saving Pub after it has been marked as not serving Guinness")

        # Send alerts
        try:
            alerts_client = GuindexAlertsClient(logger,
                                                GuindexParameters.ALERTS_LISTEN_IP,
                                                GuindexParameters.ALERTS_LISTEN_PORT)
            alerts_client.sendNewPubAlertRequest(self)
        except:
            logger.error("Failed to send New Pub Alert Request")

        # Update stats if necessary
        if self.pendingApprovalContributor.user.is_staff:
            self.pendingApproval = False
            try:
                stats_client = GuindexStatsClient(logger,
                                                  GuindexParameters.STATS_LISTEN_IP,
                                                  GuindexParameters.STATS_LISTEN_PORT)
                stats_client.sendNewPubStatsRequest(self)
            except:
                logger.error("Failed to send New Pub Stats Request")
        else:
            logger.info("Not updating stats until contribution is approved")
            self.pendingApproval = True


class Guinness(models.Model):

    # API guarantees creator field needs to be set
    # Make it nullable so we get it from request object
    # and not as required payload argument
    creator      = models.ForeignKey(UserProfile, 
                                     null    = True,
                                     blank   = True,
                                     default = None)
    creationDate = models.DateTimeField(auto_now_add = True)
    price        = models.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                       max_digits     = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                       validators     = [MinValueValidator(Decimal(GuindexParameters.MIN_GUINNESS_PRICE))])
    pub          = models.ForeignKey(Pub)
    approved     = models.BooleanField(default = True)
    rejected     = models.BooleanField(default = False)

    def __unicode__(self):

        return "'%s(%d) - Price: %.2f'" % (self.pub, self.id, self.price)

    def save(self, *args, **kwargs):

        logger.debug("Saving Guinness")

        if self.pk is None:
            self.firstSave()

        super(Guinness, self).save(*args, **kwargs)

    def firstSave(self):

        logger.debug("First save of Guinness object")

        # Append new Guinness object to Pub price list
        try:
            self.pub.prices.add(self)
            self.pub.save()
        except:
            logger.error("Failed to append Guinness to pub price list")

        # Set approved field to True if user is a staff member
        self.approved = self.creator.user.is_staff


class StatisticsSingleton(models.Model):
    """
        This is a singleton class to store statistics.
    """

    pubsInDb           = models.IntegerField(default = 0)
    pubsWithPrices     = models.ManyToManyField(Pub) # Use this to return cheapest/most expensive pubs
    averagePrice       = models.DecimalField(decimal_places = 2, max_digits = 6,  default = Decimal('0.0'))
    standardDeviation  = models.DecimalField(decimal_places = 3, max_digits = 12, default = Decimal('0.0'))
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
