from rest_framework import serializers

from GuindexUser.models import GuindexUser


class GuindexUserSerializer(serializers.ModelSerializer):

    userProfileId = serializers.PrimaryKeyRelatedField(source = 'userprofile.id', read_only = True)
    username      = serializers.CharField(source = 'userprofile.user.username', read_only = True)

    class Meta:
        model = GuindexUser
        fields = ['userProfileId', 'username', 'pubsVisited', 'originalPrices', 'currenVerifications', 'lastCalculated']
