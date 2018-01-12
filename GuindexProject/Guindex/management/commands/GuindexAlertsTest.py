import logging
import sys
from decimal import Decimal

from django.utils import timezone
from django.core.management.base import BaseCommand

from Guindex.GuindexAlertsClient import GuindexAlertsClient
from Guindex.models import Guinness, Pub

from UserProfile.models import UserProfile

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        alerts_client = GuindexAlertsClient(logger)

        # Get useful objects
        staff_member     = UserProfile.objects.get(id = 1)
        non_staff_member = UserProfile.objects.get(id = 3)

        pub = Pub.objects.get(id = 1)

        guinness = Guinness()

        guinness.creator      = non_staff_member
        guinness.creationDate = timezone.now()
        guinness.pub          = pub
        guinness.price        = Decimal('3.55')
        guinness.approved     = True

        alerts_client.sendApprovalDecisionAlertRequest(guinness)
