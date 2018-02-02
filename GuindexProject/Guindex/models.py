import logging
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from GuindexParameters import GuindexParameters

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


class Pub(models.Model):

    name                                 = models.CharField(max_length = GuindexParameters.MAX_PUB_NAME_LEN, default = "")
    longitude                            = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES, max_digits = 12, default = 0.0)
    latitude                             = models.DecimalField(decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES, max_digits = 12, default = 0.0)
    mapLink                              = models.TextField(default = "")
    closed                               = models.BooleanField(default = False)
    servingGuinness                      = models.BooleanField(default = True)
    pendingApproval                      = models.BooleanField(default = False) # In case non-staff member wants to add a pub
    pendingApprovalRejected              = models.BooleanField(default = False)
    pendingApprovalContributor           = models.ForeignKey(UserProfile, null = True, blank = True, related_name = 'pendingAdder', default = None)
    pendingApprovalTime                  = models.DateTimeField(default = timezone.now)
    pendingClosed                        = models.BooleanField(default = False) # In case non-staff member closes pub
    pendingClosedContributor             = models.ForeignKey(UserProfile, null = True, blank = True, related_name = 'pendingCloser', default = None)
    pendingClosedTime                    = models.DateTimeField(default = timezone.now)
    pendingNotServingGuinness            = models.BooleanField(default = False) # In case non-staff member marks pub as not serving Guinness
    pendingNotServingGuinnessContributor = models.ForeignKey(UserProfile, null = True, blank = True, related_name = 'pendingNotServingGuinnessMarker', default = None)
    pendingNotServingGuinnessTime        = models.DateTimeField(default = timezone.now)
    prices                               = models.ManyToManyField('Guinness', related_name = 'prices')

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

class Guinness(models.Model):

    creator      = models.ForeignKey(UserProfile)
    creationDate = models.DateTimeField(default = timezone.now)
    price        = models.DecimalField(decimal_places = 2,
                                       max_digits     = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                       validators     = [MinValueValidator(Decimal(GuindexParameters.MIN_GUINNESS_PRICE))])
    pub          = models.ForeignKey(Pub)
    approved     = models.BooleanField(default = True)
    rejected     = models.BooleanField(default = False)

    def __unicode__(self):

        return "'%s(%d) - Price: %.2f'" % (self.pub, self.id, self.price)


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
