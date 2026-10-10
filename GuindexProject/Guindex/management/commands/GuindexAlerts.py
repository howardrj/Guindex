import fcntl
import logging
import os
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from Guindex.models import Guinness, GuinnessPendingCreate
from Guindex.models import Pub, PubPendingCreate, PubPendingPatch
from Guindex.models import AlertsSingleton
from Guindex.models import GuindexUser

from Guindex.GuindexBot import GuindexBot

from Guindex.GuindexParameters import GuindexParameters

from TelegramUser import TelegramUserUtils

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        lock_path = os.path.join(settings.BASE_DIR, 'guindex_alerts.lock')
        lock_fd = open(lock_path, 'w')

        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            logger.error(
                "Another GuindexAlerts instance already holds %s; exiting to avoid duplicate alerts",
                lock_path,
            )
            lock_fd.close()
            return

        logger.info("Acquired alerts lock at %s", lock_path)

        try:
            self._run_alerts_loop()
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

    def _run_alerts_loop(self):

        while True:

            logger.info("Checking alerts")

            alerts, created = AlertsSingleton.load()

            if created:
                # Get lastCheckTime in order
                # for first run
                alerts.save()

            last_check_time = alerts.lastCheckTime
            now = timezone.now()
            elapsed = (now - last_check_time).total_seconds()

            # Only process alerts if sufficent time has passed
            if elapsed > GuindexParameters.ALERTS_CHECK_PERIOD:

                # Claim this check window BEFORE sending. If the process crashes
                # mid-send, systemd must not restart into the same window and
                # redeliver the same digests (that caused 10x duplicate alerts).
                claimed = AlertsSingleton.objects.filter(
                    pk=1,
                    lastCheckTime=last_check_time,
                ).update(lastCheckTime=now)

                if not claimed:
                    logger.info(
                        "Another alerts worker already claimed this check window; skipping send"
                    )
                    sleep_time = 60
                    logger.info("Sleeping for %d seconds", sleep_time)
                    time.sleep(sleep_time)
                    continue

                logger.info(
                    "Claimed alerts window %s -> %s",
                    last_check_time,
                    now,
                )

                alerts_context = {}

                alerts_context['new_prices'] = Guinness.objects.filter(
                                                   creationDate__range = (last_check_time, now)
                                               )

                alerts_context['new_pubs'] = Pub.objects.filter(
                                                 creationDate__range = (last_check_time, now)
                                             )

                alerts_context['new_pending_price_creates'] = GuinnessPendingCreate.objects.filter(
                                                                  creationDate__range = (last_check_time, now)
                                                              )

                alerts_context['new_pending_pub_creates'] = PubPendingCreate.objects.filter(
                                                                creationDate__range = (last_check_time, now)
                                                            )

                alerts_context['new_pending_pub_patches'] = PubPendingPatch.objects.filter(
                                                                creationDate__range = (last_check_time, now)
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
                        setattr(price, 'pubName', pub.name)
                        setattr(price, 'pubCounty', pub.county)

                    for price in alerts_context['new_pending_price_creates']:
                        pub = price.pub
                        setattr(price, 'pubName', pub.name)
                        setattr(price, 'pubCounty', pub.county)
                        setattr(price, 'contributorName', price.creator.username)

                    for pub in alerts_context['new_pending_pub_creates']:
                        setattr(pub, 'contributorName', pub.creator.username)

                    for pub in alerts_context['new_pending_pub_patches']:
                        cloned_from = pub.clonedFrom
                        setattr(pub, 'nameOrig', cloned_from.name)
                        setattr(pub, 'countyOrig', cloned_from.county)
                        setattr(pub, 'contributorName', pub.creator.username)
                        setattr(pub, 'changedFields', [])

                        # Set changed fields
                        for key in ['name', 'county', 'latitude', 'longitude', 'closed', 'servingGuinness']:
                            if getattr(pub, key) != getattr(cloned_from, key):
                                getattr(pub, 'changedFields').append((key, (getattr(cloned_from, key), getattr(pub, key))))

                    for user in User.objects.all():

                        try:
                            self._send_alerts_for_user(
                                user,
                                alerts_context,
                                normal_user_alerts_pending,
                            )
                        except Exception:
                            logger.exception(
                                "Failed while processing alerts for user %d; continuing",
                                user.id,
                            )

                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD

            else:
                logger.info("Not enough time has passed since last alerts check")

                # Sleep until next check time
                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD - elapsed

            logger.info("Sleeping for %d seconds", sleep_time)

            time.sleep(sleep_time)

    def _send_alerts_for_user(self, user, alerts_context, normal_user_alerts_pending):

        self.validateAlertsSettings(user)

        logger.debug("Checking alerts for user %d", user.id)

        if not user.is_staff and not normal_user_alerts_pending:
            logger.debug("User %d is a normal user and there are no pending normal alerts", user.id)
            return

        # Send alerts to relevant users

        alerts_context['user'] = user

        if hasattr(user, 'guindexuser') and user.guindexuser.usingEmailAlerts:

            logger.debug("Sending email alert for user %d", user.id)

            try:
                html_content = render_to_string('alert_email_template.html', alerts_context)
            except Exception:
                logger.exception(
                    "Failed to render email for user %d (email=%s)",
                    user.id,
                    getattr(user, 'email', None),
                )
                html_content = None

            if html_content is not None:
                try:
                    user.email_user('Guindex Alert', html_content, None, html_message = html_content)
                except Exception:
                    logger.exception(
                        "Failed to send email to user %d (email=%s)",
                        user.id,
                        getattr(user, 'email', None),
                    )

        if hasattr(user, 'telegramuser') and user.telegramuser.usingTelegramAlerts:

            logger.debug("Sending telegram alert for user %d", user.id)

            self.sendTelegramAlert(alerts_context)

    def sendTelegramAlert(self, context):

        message = "Hello %s,\n\n" % (context['user'].username)

        message += "Here is your weekly Guindex activity update:\n\n"

        if len(context['new_prices']):

            message += "*** New Price Submissions ***\n\n"

            for price in context['new_prices']:
                message += "Pub: %s\n" % getattr(price, 'pubName')
                message += "County: %s\n" % getattr(price, 'pubCounty')
                message += "Price: %.2f\n" % getattr(price, 'price')
                message += "Rating: %d/5\n" % getattr(price, 'starRating')
                message += "Time: %s\n" % getattr(price, 'creationDate').strftime('%Y-%b-%d %H:%M:%S')
                message += "\n"

        if len(context['new_pubs']):

            message += "*** New Pub Submissions ***\n\n"

            for pub in context['new_pubs']:
                message += "Pub Name: %s\n" % getattr(pub, 'name')
                message += "County: %s\n" % getattr(pub, 'county')
                message += "Latitude: %f\n" % getattr(pub, 'latitude')
                message += "Longitude: %f\n" % getattr(pub, 'longitude')
                message += "Time: %s\n" % getattr(pub, 'creationDate').strftime('%Y-%b-%d %H:%M:%S')
                message += "\n"

        if context['user'].is_staff and len(context['new_pending_price_creates']):

            message += "*** New Pending Price Submissions ***\n\n"

            for price in context['new_pending_price_creates']:
                message += "ID: %d\n" % getattr(price, 'id')
                message += "Pub: %s\n" % getattr(price, 'pubName')
                message += "County: %s\n" % getattr(price, 'pubCounty')
                message += "Price: %.2f\n" % getattr(price, 'price')
                message += "Rating: %d/5\n" % getattr(price, 'starRating')
                message += "Contributor: %s\n" % getattr(price, 'contributorName')
                message += "Time: %s\n" % getattr(price, 'creationDate').strftime('%Y-%b-%d %H:%M:%S')
                message += "\n"

        if context['user'].is_staff and len(context['new_pending_pub_creates']):

            message += "*** New Pending Pub Submissions ***\n\n"

            for pub in context['new_pending_pub_creates']:
                message += "ID: %d\n" % getattr(pub, 'id')
                message += "Pub: %s\n" % getattr(pub, 'name')
                message += "County: %s\n" % getattr(pub, 'county')
                message += "Latitude: %f\n" % getattr(pub, 'latitude')
                message += "Longitude: %f\n" % getattr(pub, 'longitude')
                message += "Contributor: %s\n" % getattr(pub, 'contributorName')
                message += "Time: %s\n" % getattr(pub, 'creationDate').strftime('%Y-%b-%d %H:%M:%S')
                message += "\n"

        if context['user'].is_staff and len(context['new_pending_pub_patches']):

            message += "*** New Pending Pub Changes ***\n\n"

            for pub in context['new_pending_pub_patches']:
                message += "ID: %d\n" % getattr(pub, 'id')
                message += "Pub: %s\n" % getattr(pub, 'name')
                message += "County: %s\n" % getattr(pub, 'county')
                message += "Contributor: %s\n" % getattr(pub, 'contributorName')
                message += "Time: %s\n" % getattr(pub, 'creationDate').strftime('%Y-%b-%d %H:%M:%S')

                changes = ""

                for changed_field in getattr(pub, 'changedFields'):
                    changes += "    " + changed_field[0] + ": " + str(changed_field[1][0]) + " --> " + \
                               str(changed_field[1][1]) + "\n"

                message += "Updates:\n %s" % changes
                message += "\n"

        message += "Kind regards,\n"
        message += "The Guindex Team"

        try:
            GuindexBot.sendMessage(message, context['user'].telegramuser.chatId)
        except Exception:
            logger.exception(
                "Failed to send Telegram to user %d (chatId=%s)",
                context['user'].id,
                getattr(context['user'].telegramuser, 'chatId', None),
            )

    def validateAlertsSettings(self, user):

        logger.debug("Validating alerts settings for user %d", user.id)

        if not hasattr(user, 'guindexuser'):

            logger.info("User %d does not have a GuindexUser. Creating one", user.id)

            try:
                guindexuser = GuindexUser()

                guindexuser.user = user
                guindexuser.save()
            except Exception:
                logger.exception(
                    "Failed to create GuindexUser for user %d; skipping for this alerts pass",
                    user.id,
                )

        if not hasattr(user, 'telegramuser'):

            logger.info("User %d does not have a TelegramUser. Creating one", user.id)

            try:
                TelegramUserUtils.createNewTelegramUser(user)
            except Exception:
                logger.exception(
                    "Failed to create TelegramUser for user %d; skipping for this alerts pass",
                    user.id,
                )
