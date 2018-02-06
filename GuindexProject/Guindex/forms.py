import logging

from django import forms
from django.forms import ModelForm

from Guindex.models import Pub, Guinness

logger = logging.getLogger(__name__)


class NewPubForm(ModelForm):

    class Meta:
        model = Pub
        fields = ['name', 'latitude', 'longitude']


class NewGuinnessForm(ModelForm):

    class Meta:
        model = Guinness
        fields = ['pub', 'price']
