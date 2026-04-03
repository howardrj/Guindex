from django.shortcuts import render
from dj_rest_auth.views import PasswordResetConfirmView


class GuindexPasswordResetConfirmView(PasswordResetConfirmView):
    def get(self, request, *args, **kwargs):
        context = {
            "uidb64": kwargs["uidb64"],
            "token": kwargs["token"],
        }
        return render(request, "account/password_reset_confirm.html", context)
