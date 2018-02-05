from rest_framework import serializers

from Guindex.models import Pub, Guinness, StatisticsSingleton
from Guindex.GuindexParameters import GuindexParameters

from UserProfile.models import UserProfile


class GuinnessSerializer(serializers.ModelSerializer):

    pubId               = serializers.PrimaryKeyRelatedField(source = 'pub.id', read_only = True)
    pubName             = serializers.CharField(source = 'pub.name', read_only = True)
    contributorId       = serializers.PrimaryKeyRelatedField(source = 'creator.id', read_only = True)
    contributorUsername = serializers.CharField(source = 'creator.user.username', read_only = True)

    class Meta:
        model = Guinness
        fields = ['id', 'price', 'creationDate', 'pubId', 'pubName', 'contributorId', 'contributorUsername']


class ReducedGuinnessSerializer(serializers.ModelSerializer):
    """
        Guinness object serializer that omits pub info
    """

    contributorId   = serializers.PrimaryKeyRelatedField(source = 'creator.id', read_only = True)
    contributorName = serializers.CharField(source = 'creator.user.username', read_only = True)

    class Meta:
        model = Guinness
        fields = ['id', 'price', 'creationDate', 'contributorId', 'contributorName']


class PubSerializer(serializers.ModelSerializer):

    # Returns approved Guinness prices associated with this pub
    priceList = ReducedGuinnessSerializer(source = 'getApprovedPrices', many = True)

    class Meta:
        model = Pub
        fields = ['id', 'name', 'longitude', 'latitude', 'closed', 'servingGuinness', 'priceList']


class ReducedPubSerializer(serializers.ModelSerializer):
    """
        Pub object serializer that only returns id, name and most recent price.
        Only applied to pubs in pubsWithPrices list.
    """

    # Return last verified price
    price = serializers.DecimalField(decimal_places = 2,
                                     max_digits = GuindexParameters.MAX_GUINNESS_PRICE_DIGITS,
                                     source = 'getLastVerifiedGuinness.price')

    class Meta:
        model = Pub
        fields = ['id', 'name', 'price']


class StatisticsSerializer(serializers.ModelSerializer):

    # Return this list and let javascript sort it
    pubsWithPrices = ReducedPubSerializer(many = True)

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
