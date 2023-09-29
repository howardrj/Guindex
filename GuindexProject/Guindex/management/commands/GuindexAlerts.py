import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from Guindex.models import Guinness, GuinnessPendingCreate
from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import AlertsSingleton
from Guindex.models import GuindexUser

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("Checking alerts")

            alerts, created = AlertsSingleton.load()

            if created:
                # Get lastCheckTime in order
                # for first run
                alerts.save()

            last_check_time = alerts.last_check_time

            # Only process alerts if sufficent time has passed
            if (timezone.now() - last_check_time).total_seconds() > GuindexParameters.ALERTS_CHECK_PERIOD:

                alerts_context = {}

                alerts_context['new_prices'] = Guinness.objects.filter(
                                                   creation_date__range = (last_check_time, timezone.now())
                                               )

                alerts_context['new_pubs'] = Pub.objects.filter(
                                                 creation_date__range = (last_check_time, timezone.now())
                                             )

                alerts_context['new_pending_price_creates'] = GuinnessPendingCreate.objects.filter(
                                                                  creation_date__range = (last_check_time, timezone.now())
                                                              )

                alerts_context['new_pending_pub_creates'] = PubPendingCreate.objects.filter(
                                                                creation_date__range = (last_check_time, timezone.now())
                                                            )

                alerts_context['new_pending_pub_patches'] = PubPendingPatch.objects.filter(
                                                                creation_date__range = (last_check_time, timezone.now())
                                                            )

                normal_user_alerts_pending = len(alerts_context['new_prices']) or \
                                             len(alerts_context['new_pubs'])

                staff_user_alerts_pending = len(alerts_context['new_pending_price_creates']) or \
                                            len(alerts_context['new_pending_pub_creates']) or \
                                            len(alerts_context['new_pending_pub_patches'])

                if not normal_user_alerts_pending and not staff_user_alerts_pending:
                    logger.debug("There are no alerts to process since last check time")

                else:

                    # Add extra fields to objects needed in alert message
                    for price in alerts_context['new_prices']:
                        pub = price.pub
                        setattr(price, 'pub_name', pub.name)
                        setattr(price, 'pub_county', pub.county)

                    for price in alerts_context['new_pending_price_creates']:
                        pub = price.pub
                        setattr(price, 'pub_name', pub.name)
                        setattr(price, 'pub_county', pub.county)
                        setattr(price, 'contributor_name', price.creator.username)

                    for pub in alerts_context['new_pending_pub_creates']:
                        setattr(pub, 'contributor_name', pub.creator.username)

                    for pub in alerts_context['new_pending_pub_patches']:
                        cloned_from = pub.cloned_from
                        setattr(pub, 'name_orig', cloned_from.name)
                        setattr(pub, 'county_orig', cloned_from.county)
                        setattr(pub, 'contributor_name', pub.creator.username)
                        setattr(pub, 'changed_fields', [])

                        # Set changed fields
                        for key in ['name', 'county', 'latitude', 'longitude', 'closed', 'serving_guinness']:
                            if getattr(pub, key) != getattr(cloned_from, key):
                                getattr(pub, 'changed_fields').append((key, (getattr(cloned_from, key), getattr(pub, key))))

                    for user in User.objects.all():

                        self.validate_alert_settings(user)

                        logger.debug("Checking alerts for user %d", user.id)

                        if not user.is_staff and not normal_user_alerts_pending:
                            logger.debug("User %d is a normal user and there are no pending normal alerts", user.id)
                            continue

                        # Send alerts to relevant users

                        alerts_context['user'] = user

                        if getattr(user, 'guindexuser') and user.guindexuser.using_email_alerts:

                            logger.debug("Sending email alert for user %d", user.id)

                            try:
                                html_content = render_to_string('alert_email_template.html', alerts_context)
                            except:
                                logger.error("Failed to render email to string")
                                continue

                            try:
                                user.email_user('Guindex Alert', html_content, None, html_message = html_content)
                            except:
                                logger.error("Failed to send email to user %d", user.id)
                                continue

                alerts.save()

                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD

            else:
                logger.info("Not enough time has passed since last alerts check")

                # Sleep until next check time
                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD - (timezone.now() - last_check_time).total_seconds()

            logger.info("Sleeping for %d seconds", sleep_time)

            time.sleep(sleep_time)

    def validate_alert_settings(self, user):

        logger.debug("Validating alerts settings for user %d", user.id)

        if not hasattr(user, 'guindexuser'):

            logger.info("User %d does not have a GuindexUser. Creating one", user.id)

            guindexuser = GuindexUser()

            guindexuser.user = user
            guindexuser.save()
