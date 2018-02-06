import logging

from rest_framework import serializers

from Guindex.models import Pub, Guinness, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


class GuinnessSerializer(serializers.ModelSerializer):

    creator      = serializers.PrimaryKeyRelatedField(read_only = True)
    creationDate = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Guinness
        fields = '__all__'

    def onCreateSuccess(self, guinness, request):

        logger.info("Successfully created new Guinness object")

    def onUpdateSuccess(self, guinness):

        logger.info("Successfully updated Guinness object")


class PubSerializer(serializers.ModelSerializer):

    class ReducedGuinnessSerializer(serializers.ModelSerializer):
        """
            Guinness object serializer that omits pub info
        """

        class Meta:
            model = Guinness
            fields = ['id', 'price', 'creationDate', 'creator']

    # Returns approved Guinness prices associated with this pub
    priceList = ReducedGuinnessSerializer(source = 'getApprovedPrices', many = True, read_only = True)

    class Meta:
        model = Pub
        fields = '__all__'

    def onCreateSuccess(self, pub, request):

        logger.info("Successfully created new Pub object")

    def onUpdateSuccess(self, pub):

        logger.info("Successfully updated Pub object")

class StatisticsSerializer(serializers.ModelSerializer):

    class ReducedPubSerializer(serializers.ModelSerializer):
        """
            Pub object serializer that only returns id, name and most recent price.
            Only applied to pubs in pubsWithPrices list.
        """

        # Return last verified price
        price = serializers.DecimalField(decimal_places = GuindexParameters.GUINNESS_PRICE_DECIMAL_PLACES,
                                         max_digits = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                         source = 'getLastVerifiedGuinness.price')

        class Meta:
            model = Pub
            fields = ['id', 'name', 'price']

    # Return this list and let javascript sort it
    pubsWithPrices = ReducedPubSerializer(many = True, read_only = True)

    class Meta:
        model = StatisticsSingleton
        fields = ['pubsInDb', 'percentageVisited', 'averagePrice', 'standardDeviation',
                  'closedPubs', 'notServingGuinness', 'pubsWithPrices']


class ContributorSerializer(serializers.ModelSerializer):

    username             = serializers.CharField(source = 'user.username', read_only = True)
    pubsVisited          = serializers.IntegerField(source = 'guindexuser.pubsVisited', read_only = True)
    originalPrices       = serializers.IntegerField(source = 'guindexuser.originalPrices', read_only = True)
    currentVerifications = serializers.IntegerField(source = 'guindexuser.currentVerifications', read_only = True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'pubsVisited', 'originalPrices', 'currentVerifications']
