from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = "Guindex"

    def ready(self):
        import Guindex.signals.handlers
