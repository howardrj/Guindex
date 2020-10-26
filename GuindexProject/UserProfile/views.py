from rest_auth.views import PasswordResetConfirmView
from django.shortcuts import render


class GuindexPasswordResetConfirmView(PasswordResetConfirmView):

    def get(self, request, *args, **kwargs):

        context = {
            'uidb64': kwargs['uidb64'],
            'token': kwargs['token'],
        }

        return render(request, 'account/password_reset_confirm.html', context)
