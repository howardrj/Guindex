import logging
from decimal import Decimal

from django import forms
from django.utils import timezone
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub, Guinness

from GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__)


class NewPubForm(ModelForm):

    class Meta:
        model = Pub
        fields = ['name', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):

        logger.debug("NewPubForm constructor called")

        # NewPubForm has user as member variable
        self.userProfile = kwargs.pop('userProfile', None)

        # Access base class constructor
        super(NewPubForm, self).__init__(*args, **kwargs)

    def clean(self):

        logger.debug("Cleaning data - %s", self.cleaned_data)

        pub_name  = self.cleaned_data.get('name')
        latitude  = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')

        if not pub_name or latitude is None or longitude is None:

            if not pub_name:
                logger.debug("No pub name was provided in form")

                msg = "Valid pub name required"
                self.add_error('name', msg)

            if not latitude:
                logger.debug("No latitude was provided in form")

                msg = "Valid latitude required"
                self.add_error('latitude', msg)

            if not longitude:
                logger.debug("No longitude was provided in form")

                msg = "Valid longitude required"
                self.add_error('longitude', msg)

            return self.cleaned_data

        try:
            pub = Pub.objects.get(name = pub_name)
            logger.error("A pub with the name %s already exists - %s", pub_name, pub)

            msg = "A pub with the name %s already exists" % pub_name
            self.add_error('name', msg)

            return self.cleaned_data

        except ObjectDoesNotExist:
            logger.info("No pub with the name %s exists yet. Creating a new pub object", pub_name)

        if -1 * latitude.as_tuple().exponent < GuindexParameters.GPS_COORD_MIN_DECIMAL_PLACES:

            logger.error("Latitude is not specific enough - %s", latitude)

            msg = "Latitude is not specific enough. Please use 7 decimal places"
            self.add_error('latitude', msg)

            return self.cleaned_data

        if -1 * longitude.as_tuple().exponent < GuindexParameters.GPS_COORD_MIN_DECIMAL_PLACES:

            logger.error("Longitude is not specific enough - %s", longitude)

            msg = "Longitude is not specific enough. Please use 7 decimal places"
            self.add_error('longitude', msg)

            return self.cleaned_data

        if latitude < Decimal(GuindexParameters.GPS_DUBLIN_MIN_LATITUDE) or \
           latitude > Decimal(GuindexParameters.GPS_DUBLIN_MAX_LATITUDE):

            logger.error("Latitude %f not in range", latitude)

            msg = "Latitude must be in range %s:%s" % (GuindexParameters.GPS_DUBLIN_MIN_LATITUDE,   
                                                       GuindexParameters.GPS_DUBLIN_MAX_LATITUDE)
            self.add_error('latitude', msg)

        if longitude < Decimal(GuindexParameters.GPS_DUBLIN_MIN_LONGITUDE) or \
           longitude > Decimal(GuindexParameters.GPS_DUBLIN_MAX_LONGITUDE):

            logger.error("Longitude %f not in range", longitude)

            msg = "Longitude must be in range %s:%s" % (GuindexParameters.GPS_DUBLIN_MIN_LONGITUDE,
                                                        GuindexParameters.GPS_DUBLIN_MAX_LONGITUDE)

            self.add_error('longitude', msg)

        return self.cleaned_data

    def save(self):

        logger.info("Creating new pub using data - %s", self.cleaned_data)

        pub = Pub()

        pub.name                       = self.cleaned_data.get('name')
        pub.latitude                   = self.cleaned_data.get('latitude')
        pub.longitude                  = self.cleaned_data.get('longitude')
        pub.mapLink                    = "https://www.google.ie/maps/place/%f,%f" % (pub.latitude, pub.longitude)
        pub.pendingApproval            = not self.userProfile.user.is_staff
        pub.pendingApprovalContributor = self.userProfile # Means we know who added pub
        pub.pendingApprovalTime        = timezone.now()

        try:
            pub.full_clean()
        except:
            logger.error("Pub object data could not be validated")
            raise

        try:
            pub.save()
        except:
            logger.error("Pub object could not be saved")
            raise

        return pub


class NewGuinnessForm(ModelForm):

    pub = forms.CharField(label = "", widget = forms.HiddenInput())

    class Meta:
        model = Guinness
        fields = ['price']

    def __init__(self, *args, **kwargs):

        logger.debug("NewGuinnessForm constructor called")

        # NewGuinnessForm has user as member variable
        self.userProfile = kwargs.pop('userProfile', None)
        self.pub = kwargs.pop('pub', None)

        # Access base class constructor
        super(NewGuinnessForm, self).__init__(*args, **kwargs)

    def clean(self):

        logger.debug("Cleaning data - %s", self.cleaned_data)

        pub_id = self.cleaned_data.get('pub')

        try:
            pub_id = int(pub_id)
        except:
            logger.error("Pub id %s is not an integer", pub_id)
            msg = "Pub id %s is invalid" % pub_id
            self.add_error('pub', msg)
            return self.cleaned_data

        try:
            pub = Pub.objects.get(id = pub_id)
            self.pub = pub
        except ObjectDoesNotExist:
            logger.error("No pub with id %d exists", pub_id)
            msg = "No pub with id %d exists" % pub_id
            self.add_error('pub', msg)
            return self.cleaned_data

        return self.cleaned_data

    def save(self):

        logger.info("Creating new Guinness using data - %s", self.cleaned_data)

        guinness = Guinness()

        guinness.creator  = self.userProfile
        guinness.price    = self.cleaned_data.get('price')
        guinness.pub      = self.pub
        guinness.approved = self.userProfile.user.is_staff

        try:
            guinness.full_clean()
        except:
            logger.error("Guinness object data could not be validated")
            raise

        try:
            guinness.save()
        except:
            logger.error("Guinness object could not be saved")
            raise

        return guinness
