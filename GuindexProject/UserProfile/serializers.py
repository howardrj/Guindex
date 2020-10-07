import inspect
import simplejson as json

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from rest_auth.registration.serializers import SocialLoginSerializer

from allauth.socialaccount.models import SocialAccount


class TokenSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(source = 'user.username', read_only = True)
    isStaff  = serializers.CharField(source = 'user.is_staff', read_only = True)

    class Meta:
        model = Token
        fields = ('key', 'user', 'username', 'isStaff')
