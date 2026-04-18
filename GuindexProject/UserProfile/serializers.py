from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    isStaff = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user', 'username', 'email', 'isStaff')
