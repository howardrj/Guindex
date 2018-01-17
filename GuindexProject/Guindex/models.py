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
    pendingClosedRejected                = models.BooleanField(default = False)
    pendingClosedContributor             = models.ForeignKey(UserProfile, null = True, blank = True, related_name = 'pendingCloser', default = None)
    pendingClosedTime                    = models.DateTimeField(default = timezone.now)
    pendingNotServingGuinness            = models.BooleanField(default = False) # In case non-staff member marks pub as not serving Guinness
    pendingNotServingGuinnessRejected    = models.BooleanField(default = False)
    pendingNotServingGuinnessContributor = models.ForeignKey(UserProfile, null = True, blank = True, related_name = 'pendingNotServingGuinnessMarker', default = None)
    pendingNotServingGuinnessTime        = models.DateTimeField(default = timezone.now)

    def __unicode__(self):

        return "'%s(%d)'" % (self.name, self.id)

    def getGuini(self, newestFirst):
        """
            Returns list of Guinness objects belonging to this pub
            sorted by creation date
        """
        guini_list = []

        guini = Guinness.objects.filter(pub = self)

        for guin in guini:

            if guin.approved:

                guin_dict = {}

                guin_dict['id']           = str(guin.id)
                guin_dict['creator']      = guin.creator.user.username
                guin_dict['creationDate'] = guin.creationDate
                guin_dict['price']        = guin.price

                guini_list.append(guin_dict.copy())

        return sorted(guini_list, key = lambda k: k['creationDate'], reverse = newestFirst)

    def getFirstVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        guini = self.getGuini(False)

        return guini[0] if len(guini) else None

    def getLastVerifiedGuinness(self):
        """
            Return most recently verified Guinness object.
        """

        guini = self.getGuini(True)

        return guini[0] if len(guini) else None


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

        return "'%s(%d) - Price: %f'" % (self.pub, self.id, self.price)


class StatisticsSingleton(models.Model):
    """
        This is a singleton class to store statistics.
    """

    pubsInDb           = models.IntegerField(default = 0)
    cheapestPub        = models.TextField(default = "") # Make Textfield instead of Pub key to avoid crashes on delete
    dearestPub         = models.TextField(default = "") # Make Textfield instead of Pub key to avoid crahes on delete
    averagePrice       = models.DecimalField(decimal_places = 2, max_digits = 6,  default = Decimal('0.0'))
    standardDevation   = models.DecimalField(decimal_places = 3, max_digits = 12, default = Decimal('0.0'))
    percentageVisited  = models.DecimalField(decimal_places = 2, max_digits = 5,  default = Decimal('0.0'))
    closedPubs         = models.IntegerField(default = 0)
    notServingGuinness = models.IntegerField(default = 0)
    lastCalculated     = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(StatisticsSingleton, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk = 1)
        return obj


class UserContributionsSingleton(models.Model):
    """
        Singleton class to keep track of best contributors
    """

    mostVisited       = models.ForeignKey(UserProfile, related_name = 'most_visited', null = True)
    mostLastVerified  = models.ForeignKey(UserProfile, related_name = 'most_last_verifications', null = True)
    mostFirstVerified = models.ForeignKey(UserProfile, related_name = 'most_first_verifications', null = True)
    lastCalculated    = models.DateTimeField(auto_now = True)

    def __unicode__(self):

        return "'%s - %s - %s'" % (self.mostVisited, self.mostLastVerified, self.mostFirstVerified)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(UserContributionsSingleton, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk = 1)
        return obj
