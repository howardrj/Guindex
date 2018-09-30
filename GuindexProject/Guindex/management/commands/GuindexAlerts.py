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

from Guindex.GuindexBot import GuindexBot

from Guindex.GuindexParameters import GuindexParameters

from TelegramUser import TelegramUserUtils

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

            last_check_time = alerts.lastCheckTime

            # Only process alerts if sufficent time has passed
            if (timezone.now() - last_check_time).total_seconds() > GuindexParameters.ALERTS_CHECK_PERIOD:

                alerts_context = {}

                alerts_context['new_prices'] = Guinness.objects.filter(
                                                   creationDate__range = (last_check_time, timezone.now())
                                               )

                alerts_context['new_pubs'] = Pub.objects.filter(
                                                 creationDate__range = (last_check_time, timezone.now())
                                             )

                alerts_context['new_pending_price_creates'] = GuinnessPendingCreate.objects.filter(
                                                                  creationDate__range = (last_check_time, timezone.now())
                                                              )

                alerts_context['new_pending_pub_creates'] = PubPendingCreate.objects.filter(
                                                                creationDate__range = (last_check_time, timezone.now())
                                                            )

                alerts_context['new_pending_pub_patches'] = PubPendingPatch.objects.filter(
                                                                creationDate__range = (last_check_time, timezone.now())
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
                        pub = Pub.objects.get(id = price.pub)
                        setattr(price, 'pubName', pub.name)
                        setattr(price, 'pubCounty', pub.county)

                    for price in alerts_context['new_pending_price_creates']:
                        pub = Pub.objects.get(id = price.pub)
                        setattr(price, 'pubName', pub.name)
                        setattr(price, 'pubCounty', pub.county)
                        setattr(price, 'contributorName', price.creator.username)

                    for pub in alerts_context['new_pending_pub_creates']:
                        setattr(pub, 'contributorName', pub.creator.username)

                    for pub in alerts_context['new_pending_pub_patches']:
                        cloned_from = Pub.objects.get(id = pub.clonedFrom)
                        setattr(pub, 'nameOrig', cloned_from.name)
                        setattr(pub, 'countyOrig', cloned_from.county)
                        setattr(pub, 'contributorName', pub.creator.username)
                        setattr(pub, 'changedFields', [])

                        # Set changed fields
                        for key in ['name', 'county', 'latitude', 'longitude', 'closed', 'servingGuinness']:
                            if pub[key] != cloned_from[key]:
                                pub['changedFields'].append((key, (cloned_from[key], pub[key])))

                    for user in User.objects.all():

                        self.validateAlertsSettings(user)

                        logger.debug("Checking alerts for user %d", user.id)

                        if not user.is_staff and not normal_user_alerts_pending:
                            logger.debug("User %d is a normal user and there are no pending normal alerts", user.id)
                            continue

                        # Send alerts to relevant users

                        alerts_context['user'] = user

                        if getattr(user, 'guindexuser') and user.guindexuser.usingEmailAlerts:

                            logger.debug("Sending email alert for user %d", user.id)

                            try:
                                html_content = render_to_string('alert_email_template.html', alerts_context)
                            except:
                                self.logger.error("Failed to render email to string")
                                continue

                        try:
                            user.email_user('Guindex Alert', html_content, None, html_message = html_content)
                        except:
                            self.logger.error("Failed to send email to user %d", user.id)
                            continue

                        if getattr(user, 'telegramuser') and user.telegramuser.usingTelegramAlerts:

                            logger.debug("Sending telegram alert for user %d", user.id)

                            self.sendTelegramAlert(alerts_context)

                alerts.save()

                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD

            else:
                logger.info("Not enough time has passed since last alerts check")

                # Sleep until next check time
                sleep_time = GuindexParameters.ALERTS_CHECK_PERIOD - (timezone.now() - last_check_time).total_seconds()

            logger.info("Sleeping for %d seconds", sleep_time)

            time.sleep(sleep_time)

        def sendTelegramAlert(self, context):

            message = "Hello %s,\n\n" % (context['user'].username)

            message += "Here is your weekly Guindex activity update\n\n"

            if len(context['new_prices']):

                message += "*** New Price Submissions ***\n\n"

                for price in context['new_prices']:
                    message += "Pub: %s\n" % price['pubName']
                    message += "County: %s\n" % price['pubCounty']
                    message += "Price: %f\n" % price['price']
                    message += "Rating: %d/5\n" % price['starRating']
                    message += "Time: %s\n" % price['creationDate'].strftime('%Y-%b-%d %H:%M:%S')
                    message += "\n"

            if len(context['new_pubs']):

                message += "*** New Pub Submissions ***\n\n"

                for pub in context['new_pubs']:
                    message += "Pub: %s\n" % pub['name']
                    message += "County: %s\n" % pub['county']
                    message += "Time: %s\n" % pub['creationDate'].strftime('%Y-%b-%d %H:%M:%S')
                    message += "\n"

            if context['user'].is_staff and len(context['new_pending_price_creates']):

                message += "*** New Pending Price Submissions ***\n\n"

                for price in context['new_pending_price_creates']:
                    message += "ID: %d\n" % price['id']
                    message += "Pub: %s\n" % price['pubName']
                    message += "County: %s\n" % price['pubCounty']
                    message += "Price: %f\n" % price['price']
                    message += "Rating: %d/5\n" % price['starRating']
                    message += "Contributor: %s\n" % price['contributorName']
                    message += "Time: %s\n" % price['creationDate'].strftime('%Y-%b-%d %H:%M:%S')
                    message += "\n"

            if context['user'].is_staff and len(context['new_pending_pub_creates']):

                message += "*** New Pending Pub Submissions ***\n\n"

                for pub in context['new_pending_pub_creates']:
                    message += "ID: %d\n" % pub['id']
                    message += "Pub: %s\n" % pub['name']
                    message += "County: %s\n" % pub['county']
                    message += "Latitude: %f\n" % pub['latitude']
                    message += "Longitude: %f\n" % pub['longitude']
                    message += "Contributor: %s\n" % pub['contributorName']
                    message += "Time: %s\n" % pub['creationDate'].strftime('%Y-%b-%d %H:%M:%S')
                    message += "\n"

            if context['user'].is_staff and len(context['new_pending_pub_patches']):

                message += "*** New Pending Pub Changes ***\n\n"

                for pub in context['new_pending_pub_patches']:
                    message += "ID: %d\n" % pub['id']
                    message += "Pub: %s\n" % pub['name']
                    message += "County: %s\n" % pub['county']
                    message += "Contributor: %s\n" % pub['contributorName']
                    message += "Time: %s\n" % pub['creationDate'].strftime('%Y-%b-%d %H:%M:%S')

                    changes = ""

                    for changed_field in pub['changedFields']:
                        changes += "    " + changed_field[0] + ": " + str(changed_field[1][0]) + " --> " + \
                                   str(changed_field[1][1]) + "\n"

                    message += "Updates: %s" % changes
                    message += "\n"

            message += "Kind regards,\n"
            message += "The Guindex Team"

            try:
                GuindexBot.sendMessage(message, user.telegramuser.chatId)
            except:
                logger.error("Failed to send Telegram to user %d", context['user'].id)

        def validateAlertsSettings(self, user):

            logger.debug("Validating alerts settings for user %d", user.id)

            if not hasattr(user, 'guindexuser'):

                logger.info("User %d does not have a GuindexUser. Creating one", user.id)

                guindexuser = GuindexUser()

                guindexuser.user = user
                guindexuser.save()

            if not hasattr(user, 'telegramuser'):

                logger.info("User %d does not have a TelegramUser. Creating one", user.id)

                TelegramUserUtils.createNewTelegramUser(user)
