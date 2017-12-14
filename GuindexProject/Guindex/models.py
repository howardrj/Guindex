import logging

from django.db import models

from GuindexParameters import GuindexParameters

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


class Pub(models.Model):

    creator      = models.OneToOneField(UserProfile)
    creationDate = models.DateTimeField(auto_now_add = True)
    name         = models.CharField(max_length = GuindexParameters.MAX_PUB_NAME_LEN, default = "")

    def __unicode__(self):

        return "'%s(%d)'" % (self.name, self.id)

    def getGuini(self):
        """
            Returns list of Guinness objects belonging to this pub
            sorted by creation date
        """
        guini_list = []

        guini = Guinness.objects.filter(pub = self)

        for guin in guini:

            guin_dict = {}

            guin_dict['id']           = str(guin.id)
            guin_dict['creator']      = guin.creator.user.username
            guin_dict['creationDate'] = guin.creationDate
            guin_dict['price']        = guin.price

            guini_list.append(guin_dict.copy())

        return sorted(guini_list, key = lambda k: k['creationDate'], reverse = False)


class Guinness(models.Model):

    creator      = models.OneToOneField(UserProfile)
    creationDate = models.DateTimeField(auto_now_add = True)
    price        = models.DecimalField(decimal_places = 2, max_digits = 6)
    pub          = models.ForeignKey(Pub)

    def __unicode__(self):

        return "'%s(%d) - Price: %f'" % (self.pub, self.id, self.price)
