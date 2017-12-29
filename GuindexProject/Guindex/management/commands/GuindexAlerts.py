import logging
import time

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from UserProfile.models import UserProfile

from Guindex.models import Pub, AlertsSingleton
from Guindex.GuindexParameters import GuindexParameters
from Guindex.GuindexBot import GuindexBot

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
            Note: This could be more sophisticated.
            As of now, it only checks the most last verified Guinness
            and not all.
        """
        
        while True:

            logger.info("Checking Alerts")

            alerts_singleton = AlertsSingleton.load()
            pub_list = []

            for pub in Pub.objects.all():

                pub_dict = {}

                if pub.getLastVerifiedGuinness():

                    if pub.getLastVerifiedGuinness()['creationDate'] > alerts_singleton.lastAlertCheck:
                        logger.info("Pub %s received a new price", pub) 

                        pub_dict['name']         = pub.name
                        pub_dict['price']        = pub.getLastVerifiedGuinness()['price']
                        pub_dict['creationDate'] = pub.getLastVerifiedGuinness()['creationDate']
                        pub_dict['creator']      = pub.getLastVerifiedGuinness()['creator']

                        pub_list.append(pub_dict.copy())
                        
                else:
                    continue

            if len(pub_list):

                for user_profile in UserProfile.objects.all():

                    if user_profile.usingEmailAlerts:
                        self.sendEmailAlert(user_profile, pub_list)

                    if user_profile.telegramuser:

                        if user_profile.telegramuser.activated and user_profile.telegramuser.usingTelegramAlerts:
                            self.sendTelegramAlert(user_profile, pub_list)

                    else:
                        logger.info("UserProfile %s has not created telegramuser yet", user_profile)
                
                try:
                    logger.info("Saving Alerts state")
                    alerts_singleton.save()
                except:
                    logger.error("Failed to save Alerts state")

            else:
                logger.info("No events to report")

            logger.info("Sleeping for %d seconds", GuindexParameters.ALERTS_CHECK_PERIOD)
            time.sleep(GuindexParameters.ALERTS_CHECK_PERIOD)

    def sendEmailAlert(self, userProfile, pubList):

        logger.info("Sending email alert to UserProfile %s", userProfile)
        
        data = {}
        data['pub_list'] = pubList
        
        try:
            html_content = render_to_string('guindex_alerts_email.html', data)

            userProfile.user.email_user('Guindex Alerts', html_content, None, html_message = html_content)
        except:
            logger.error("Failed to send alert email to %s with email %s", userProfile, userProfile.user.email)

    def sendTelegramAlert(self, userProfile, pubList):

        logger.info("Sending telegram alert to UserProfile %s", userProfile)

        message = "The following event(s) have occured in the Guindex:\n\n"

        for pub in pubList:
            event_string = ""

            event_string += "Pub: %s\n" % pub['name']
            event_string += "Price: %s\n" % pub['price']
            event_string += "Contributor: %s\n" % pub['creator']
            event_string += "Time: %s\n" % pub['creationDate']

            message += event_string + "\n\n"

        try:
            GuindexBot.sendMessage(message, userProfile.telegramuser.chatId)
        except:
            logger.error("Failed to send telegram alerts")
