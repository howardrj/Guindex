import logging

from django.forms import ModelForm

from Guindex.models import Pub, Guinness

logger = logging.getLogger(__name__)


class NewPubForm(ModelForm):

    class Meta:
        model = Pub
        # Same as PubPostSerializer
        fields = ['name', 'latitude', 'longitude']


class NewGuinnessForm(ModelForm):

    class Meta:
        model = Guinness
        # Same as GuinnessPostSerializer
        fields = ['pub', 'price']
