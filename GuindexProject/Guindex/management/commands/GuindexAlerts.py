import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        logger.info("Creating Guindex alerts server")

        reactor.listenTCP(GuindexParameters.ALERTS_LISTEN_PORT,
                          GuindexAlertsServerFactory(logger),
                          GuindexParameters.ALERTS_BACKLOG,
                          GuindexParameters.ALERTS_LISTEN_IP)

        logger.info("Created TCP server listening on %s:%d. Waiting for alerts ...",
                    GuindexParameters.ALERTS_LISTEN_IP, GuindexParameters.ALERTS_LISTEN_PORT)

        reactor.run()
