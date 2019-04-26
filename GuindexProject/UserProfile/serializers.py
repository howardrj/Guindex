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


class GuindexSocialLoginSerializer(SocialLoginSerializer):

    def validate(self, attr):

        try:

            parent_validate = super(GuindexSocialLoginSerializer, self).validate
            return parent_validate(attr)

        except ValidationError as e1:
            
            try:
                error_details = e1.get_full_details()

                error_message = error_details[0]['message']

                if error_message.startswith('User is already registered with this e-mail address.'):

                    # Get user object from email

                    parent_local_variables = inspect.trace()[-1][0].f_locals

                    email = parent_local_variables['login'].user.email

                    user = User.objects.get(email = email)
                    user_id = int(user.id)

                    # Determine types of account owned by this user
                    has_password_login = False
                    has_fb_login       = False
                    has_google_login   = False

                    if user.has_usable_password():
                        has_password_login = True

                    if SocialAccount.objects.filter(provider = 'facebook', user_id = user_id): 
                        has_fb_login = True

                    if SocialAccount.objects.filter(provider = 'google', user_id = user_id):
                        has_google_login = True

                    login_account_state = {
                        'email'                          : user.email,
                        'has_password_login'             : has_password_login,
                        'has_fb_login'                   : has_fb_login,
                        'has_google_login'               : has_google_login,
                        'account_to_connect_access_token': attr['access_token'],
                    }

                    new_error_message = "User is already registered with this email address.";
                    new_error_message += " - ";
                    new_error_message += json.dumps(login_account_state);

                    raise ValidationError(ugettext_lazy(new_error_message))

                else:
                    raise Exception("This error does not need to be handled at Guindex layer")

            except ValidationError:
                raise
            except Exception as e2:
                raise e1
