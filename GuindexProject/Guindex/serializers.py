from rest_framework import serializers

from Guindex.models import Pub, Guinness, StatisticsSingleton

from GuindexUser.models import GuindexUser


class PubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pub
        fields = ['id', 'name', 'longitude', 'latitude', 'closed', 'servingGuinness']


class GuinnessSerializer(serializers.ModelSerializer):

    contributor = serializers.PrimaryKeyRelatedField(source = 'creator.user.username', read_only = True)

    class Meta:
        model = Guinness
        fields = ['id', 'price', 'pub', 'creationDate', 'contributor', 'approved']


class StatisticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatisticsSingleton
        fields = ['pubsInDb', 'cheapestPub', 'dearestPub', 'averagePrice', 'standardDevation',
                  'percentageVisited', 'closedPubs', 'notServingGuinness', 'lastCalculated']

class GuindexUserSerializer(serializers.ModelSerializer):

    userProfileId = serializers.PrimaryKeyRelatedField(source = 'userprofile.id', read_only = True)
    username      = serializers.CharField(source = 'userprofile.user.username', read_only = True)

    class Meta:
        model = GuindexUser
        fields = ['userProfileId', 'username', 'pubsVisited', 'originalPrices', 'currenVerifications', 'lastCalculated']
