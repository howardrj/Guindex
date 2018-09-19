import logging
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


##############
# Pub Models #
##############

class PubBase(models.Model):

    creator = models.ForeignKey(User,
                                help_text = 'ID of user who created this pub',
                                null = True,
                                blank = True,
                                default = None)

    creationDate = models.DateTimeField(help_text = 'UTC timestamp of when pub was created',
                                        default = timezone.now)

    name = models.CharField(help_text = 'Pub name',
                            max_length = GuindexParameters.MAX_PUB_NAME_LEN)

    county = models.CharField(help_text = 'County pub is located in',
                              max_length = GuindexParameters.MAX_COUNTY_NAME_LEN,
                              choices = [(x, x) for x in GuindexParameters.SUPPORTED_COUNTIES],
                              default = 'Dublin')

    longitude = models.DecimalField(help_text = 'Longitude of pub location',
                                    decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                    max_digits = GuindexParameters.GPS_COORD_MAX_DIGITS)

    latitude = models.DecimalField(help_text = 'Latitude of pub location',
                                   decimal_places = GuindexParameters.GPS_COORD_DECIMAL_PLACES,
                                   max_digits = GuindexParameters.GPS_COORD_MAX_DIGITS)

    mapLink = models.TextField(help_text = 'Link to pub location in google maps',
                               default = "")  # Set this in save method

    closed = models.BooleanField(help_text = 'Is pub permanently closed?',
                                 default = False)

    servingGuinness = models.BooleanField(help_text = 'Is pub serving Guinness?',
                                          default = True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "'%s(%s)'" % (self.name, str(self.id) if self.id else "No DB ID")


class Pub(PubBase):
    """
        Table that stores list of all approved pubs
    """

    averageRating = models.DecimalField(help_text = 'Average star rating of pints submitted for this pub',
                                        decimal_places = GuindexParameters.STAR_RATING_DECIMAL_PLACES,
                                        max_digits = 3,
                                        validators = [MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
                                        null = True,
                                        blank = True,
                                        default = None)

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
                logger.debug("Creator is not a staff member. Creating PubPendingCreate object instead")
                self.createPendingCreate()
                return

        super(Pub, self).save(*args, **kwargs)

    def createPendingCreate(self):

        pub_pending_create = PubPendingCreate()

        for field in self._meta.fields:
            setattr(pub_pending_create, field.name, getattr(self, field.name))

        pub_pending_create.pk = None
        pub_pending_create.save()


class PubPendingCreate(PubBase):
    """
        Table that stores list of pending pub creations
    """


class PubPendingPatch(PubBase):
    """
        Table that stores list of pending pub patches
    """

    clonedFrom = models.ForeignKey(Pub,
                                   help_text = 'Pub this patch was applied to')


###################
# Guinness Models #
###################

class GuinnessBase(models.Model):

    creator = models.ForeignKey(User,
                                help_text = 'ID of user who submitted this price',
                                null = True,
                                blank = True,
                                default = None)

    creationDate = models.DateTimeField(help_text = 'UTC timestamp of when price was submitted',
                                        default = timezone.now)

    price = models.DecimalField(help_text = 'Price',
                                decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                max_digits = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                validators = [MinValueValidator(Decimal(GuindexParameters.MIN_GUINNESS_PRICE))])

    pub = models.ForeignKey(Pub,
                            help_text = 'ID of pub this price belongs to')

    starRating   = models.IntegerField(help_text = 'Star rating (i.e. quality of pint)',
                                       validators = [MinValueValidator(0), MaxValueValidator(5)],
                                       null = True,
                                       default = None)

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
                logger.debug("Creator is not a staff member. Creating GuinnessPendingCreate object instead")
                self.createPendingCreate()
                return

        super(Guinness, self).save(*args, **kwargs)

    def createPendingCreate(self):

        guinness_pending_create = GuinnessPendingCreate()

        for field in self._meta.fields:
            setattr(guinness_pending_create, field.name, getattr(self, field.name))

        guinness_pending_create.pk = None
        guinness_pending_create.save()


class GuinnessPendingCreate(GuinnessBase):
    """
        Table that stores list of pending Guinness creations
    """


#####################
# Statistics Models #
#####################

class StatisticsSingleton(models.Model):
    """
        This is a singleton class to store statistics.
    """

    pubsInDb = models.IntegerField(help_text = 'Number of pubs in database',
                                   default = 0)

    averagePrice = models.DecimalField(help_text = 'Average price from all pubs with registered prices',
                                       decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                       max_digits = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                       default = Decimal('0.0'))

    standardDeviation = models.DecimalField(help_text = 'Standard deviation',
                                            decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES + 1,
                                            max_digits = 12,
                                            default = Decimal('0.0'))

    percentageVisited = models.DecimalField(help_text = 'Percentage of pubs in database visited by one or more users',
                                            decimal_places = 2,
                                            max_digits = 5,
                                            default = Decimal('0.0'))

    closedPubs = models.IntegerField(help_text = 'Number of pubs marked as closed',
                                     default = 0)

    notServingGuinness = models.IntegerField(help_text = 'Number of pubs marked as not serving Guinness',
                                             default = 0)

    lastCalculated = models.DateTimeField(help_text = 'UTC timestamp of when statistics were last calculated',
                                          auto_now = True)

    numUsers = models.IntegerField(help_text = 'Number of user accounts',
                                   default = 0)

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

    user = models.OneToOneField(User,
                                help_text = 'User ID associated with this contributor',
                                null = True,
                                blank = True,
                                default = None,
                                related_name = 'guindexuser')

    pubsVisited = models.IntegerField(help_text = 'Number of pubs visited by this contributor',
                                      default = 0)

    originalPrices = models.IntegerField(help_text = 'Number of first prices for a pub submitted by this contributor',
                                         default = 0)

    currentVerifications = models.IntegerField(help_text = 'Number of current verifactions for this contributor',
                                               default = 0)

    lastCalculated = models.DateTimeField(help_text = 'UTC timestamp of when statistics were last calculated for this contributor',
                                          auto_now = True)

    usingEmailAlerts = models.BooleanField(help_text = 'Does this contributor have email alerts enabled?',
                                           default = False)

    isDeveloper = models.BooleanField(help_text = 'Is this contributor a developer of the Guindex website?',
                                      default = False)
