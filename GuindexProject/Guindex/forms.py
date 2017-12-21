import logging

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist

from Guindex.models import Pub, Guinness

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
        """
            Note that if a required field is blank in form,
            it will be not be found in cleaned_data.
            If it is not required an empty string will be placed
            in cleaned_data.
            Some browsers won't let us get this far!
        """

        logger.debug("Cleaning data - %s", self.cleaned_data)

        pub_name = self.cleaned_data.get('name')
        latitude = self.cleaned_data.get('latitude')
        latitude = self.cleaned_data.get('longitude')

        if not self.userProfile.user.is_staff:
            logger.error("Only staff members can create a new pub")
            msg = "Only staff members can create a new pub"
            self.add_error('name', msg)
            return self.cleaned_data

        if not pub_name or not latitude or not longitude:

            if not pub_name:
                logger.debug("No pub name was provided in form")

            if not latitude:
                logger.debug("No latitude was provided in form")

            if not longitude:
                logger.debug("No longitude was provided in form")

            return self.cleaned_data

        try:
            pub = Pub.objects.get(name = pub_name)
            logger.error("A pub with the name %s already exists - %s", pub_name, pub)

            msg = "A pub with the name %s already exists" % pub_name
            self.add_error('name', msg)

            return self.cleaned_data

        except ObjectDoesNotExist:
            logger.info("No pub with the name %s exists yet. Creating a new pub object", pub_name)

        if not (latitude >= -90 and latitude <= 90):
            logger.error("Latitude %f not in range", latitude)

            msg = "Latitude must be in range %d - %d" % (-90, 90)
            self.add_error('latitude', msg)

        if not (longitude >= -180 and longitude <= 180):
            logger.error("Longitude %f not in range", longitude)

            msg = "Latitude must be in range %d - %d" % (-180, 180)
            self.add_error('longitude', msg)

        return self.cleaned_data

    def save(self):

        logger.info("Creating new pub using data - %s", self.cleaned_data)

        pub = Pub()

        pub.creator   = self.userProfile
        pub.name      = self.cleaned_data.get('name')
        pub.latitude  = self.cleaned_data.get('latitude')
        pub.longitude = self.cleaned_data.get('longitude')
        pub.mapLink   = "https://www.google.ie/maps/@%f,%f" % (pub.latitude, pub.longitude)

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


class RenamePubForm(ModelForm):

    pub = forms.CharField(label = "", widget = forms.HiddenInput())

    class Meta:
        model = Pub
        fields = ['name']

    def __init__(self, *args, **kwargs):

        logger.debug("RenamePubForm constructor called")

        # RenamePubForm has user as member variable
        self.userProfile = kwargs.pop('userProfile', None)
        self.pub         = kwargs.pop('pub', None)

        # Access base class constructor
        super(RenamePubForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
            Note that if a required field is blank in form,
            it will be not be found in cleaned_data.
            If it is not required an empty string will be placed
            in cleaned_data.
            Some browsers won't let us get this far!
        """

        logger.debug("Cleaning data - %s", self.cleaned_data)

        pub_id   = self.cleaned_data.get('pub')
        new_name = self.cleaned_data.get('name')

        if not self.userProfile.user.is_staff:
            logger.error("Only staff members can rename a pub")
            msg = "Only staff members can rename a pub"
            self.add_error('name', msg)
            return self.cleaned_data

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

        try:
            Pub.objects.get(name = new_name)
            logger.error("Pub with name %s already exists. Can't use this name", new_name)
            msg = "A pub already exists with this name."
            self.add_error('name', msg)
        except ObjectDoesNotExist:
            logger.debug("Pub name %s has not been taken yet", new_name)

        return self.cleaned_data

    def save(self):

        logger.info("Renaming pub using data - %s", self.cleaned_data)

        self.pub.name = self.cleaned_data.get('name')

        try:
            self.pub.full_clean()
        except:
            logger.error("Pub object data could not be validated")
            raise

        try:
            self.pub.save()
        except:
            logger.error("Pub object could not be saved")
            raise


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
        """
            Note that if a required field is blank in form,
            it will be not be found in cleaned_data.
            If it is not required an empty string will be placed
            in cleaned_data.
            Some browsers won't let us get this far!
        """

        logger.debug("Cleaning data - %s", self.cleaned_data)

        pub_id = self.cleaned_data.get('pub')
        price  = self.cleaned_data.get('price')

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

        guinness.creator = self.userProfile
        guinness.price = self.cleaned_data.get('price')
        guinness.pub = self.pub

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
