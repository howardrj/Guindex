from rest_framework import serializers

from Guindex.models import Pub, Guinness


class PubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pub
        fields = ['id', 'name', 'longitude', 'latitude', 'closed', 'servingGuinness']


class GuinnessSerializer(serializers.ModelSerializer):

    contributor = serializers.PrimaryKeyRelatedField(source = 'creator.user.username', read_only = True)

    class Meta:
        model = Guinness
        fields = ['id', 'price', 'pub', 'creationDate', 'contributor']
