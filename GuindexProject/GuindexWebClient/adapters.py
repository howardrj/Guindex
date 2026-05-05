from allauth.account.adapter import DefaultAccountAdapter


class GuindexAccountAdapter(DefaultAccountAdapter):
    """Keep browser auth flows on the Guindex home shell."""

    def get_login_url(self, request, **kwargs):
        return '/'
