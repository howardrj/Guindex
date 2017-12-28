import logging
import time

from django.core.management.base import BaseCommand

from Guindex.GuindexParameters import GuindexParameters
from Guindex.models import Pub, Guinness, UserContributionsSingleton

from GuindexUser import GuindexUserUtils

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:
        
            logger.info("Calculating User Contributions")

            most_pubs_visited          = None
            most_first_verifications   = None
            most_current_verifications = None

            for loop_index, user_profile in enumerate(UserProfile.objects.all()):

                logger.debug("Calculating contrbutions for UserProfile %s", user_profile)

                if not user_profile.guindexuser:
                   logger.debug("Need to create GuindexUser for UserProfile %s", user_profile) 

                   GuindexUserUtils.createNewGuindexUser(user_profile)
                    
                logger.debug("Calculating number of current and first verifications")

                number_of_current_verifications = 0
                number_of_first_verifications   = 0 
                number_of_pubs_visited          = 0

                for pub in Pub.objects.all():
                   
                    if pub.getLastVerifiedGuinness(): 
                        if pub.getLastVerifiedGuinness()['creator'] == user_profile.user.username:
                            number_of_current_verifications = number_of_current_verifications + 1

                    if pub.getFirstVerifiedGuinness(): 
                        if pub.getFirstVerifiedGuinness()['creator'] == user_profile.user.username:
                            number_of_first_verifications = number_of_first_verifications + 1

                    # TODO Test this
                    if len(Guinness.objects.filter(pub = pub, creator = user_profile)):
                        number_of_pubs_visited = number_of_pubs_visited + 1

                user_profile.guindexuser.originalPrices       = number_of_first_verifications
                user_profile.guindexuser.currentVerifications = number_of_current_verifications
                user_profile.guindexuser.pubsVisited          = number_of_pubs_visited

                user_profile.guindexuser.save()
                user_profile.save() # Pedantic

                if loop_index == 0:
                    most_first_verifications   = user_profile
                    most_current_verifications = user_profile
                    most_pubs_visited          = user_profile

                elif user_profile.guindexuser.originalPrices > most_first_verifications.guindexuser.originalPrices:
                    most_first_verifications = user_profile
                elif user_profile.guindexuser.currentVerifications > most_current_verifications.guindexuser.currentVerifications:
                    most_current_verifications = user_profile
                elif user_profile.guindexuser.pubsVisited > most_first_verifications.guindexuser.pubsVisited:
                    most_pubs_visited = user_profile

            user_contributions_singleton = UserContributionsSingleton.load()

            user_contributions_singleton.mostVisited       = most_pubs_visited
            user_contributions_singleton.mostLastVerified  = most_current_verifications
            user_contributions_singleton.mostFirstVerified = most_first_verifications

            logger.info("Saving User Contributions %s", user_contributions_singleton)

            user_contributions_singleton.save()

            logger.info("Sleeping for %d seconds", GuindexParameters.USER_CONTRIBUTIONS_CALCULATION_PERIOD)
            time.sleep(GuindexParameters.USER_CONTRIBUTIONS_CALCULATION_PERIOD)
