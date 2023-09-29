import logging
import time
import math
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from Guindex.models import Pub, Guinness, StatisticsSingleton, GuindexUser
from Guindex.GuindexParameters import GuindexParameters


logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        while True:

            logger.info("***** Calculating statistics and user contributions *****")

            stats = StatisticsSingleton.load()

            try:
                logger.info("Calculating number of pubs")
                stats.pubs_in_db = self.calculate_number_of_pubs()
            except:
                logger.error("Failed to calculate number of pubs")

            try:
                logger.info("Calculating average price")
                stats.average_price = self.calculate_average_price()
            except:
                logger.error("Failed to calculate average price")

            try:
                logger.info("Calculating standard deviation")
                stats.standard_deviation = self.calculate_standard_deviation()
            except:
                logger.error("Failed to calculate standard deviation")

            try:
                logger.info("Calculating closed pubs")
                stats.closed_pubs = self.calculate_closed_pubs()
            except:
                logger.error("Failed to calculate closed pubs")

            try:
                logger.info("Calculating pubs not serving Guinness")
                stats.not_serving_guinness = self.calculate_not_serving_guinness()
            except:
                logger.error("Failed to calculate not serving Guinness")

            try:
                logger.info("Calculating percentage visited")
                stats.percentage_visited = self.calculate_percentage_visited()
            except:
                logger.error("Failed to calculate percentage visited")

            try:
                logger.info("Calculating number of users")
                stats.num_users = self.calculate_number_of_users()
            except:
                logger.error("Failed to calculate number of users")

            try:
                logger.info("Saving statistics")
                stats.save()
            except:
                logger.error("Failed to save statistics")

            try:
                logger.info("Calculate average star ratings")
                self.calculate_average_star_ratings()
            except:
                logger.error("Failed to calculate average star ratings")

            try:
                logger.info("Calculating latest pub prices")
                self.calculate_latest_pub_prices()
            except:
                logger.error("Failed to calculate latest pub prices")

            try:
                logger.info("Calculating user contributions")
                self.calculate_user_contributions()
            except:
                logger.error("Failed to calculate user contributions")

            logger.info("Sleeping for %s seconds", GuindexParameters.STATS_CALCULATION_PERIOD)

            time.sleep(GuindexParameters.STATS_CALCULATION_PERIOD)

    def calculate_number_of_pubs(self):
        """
            Counts approved pubs.
        """
        return len(Pub.objects.all())

    def calculate_average_price(self):
        """
            Calculate average price from pubs with prices.
            Uses most recent price for each pub/
        """
        sum_total = 0
        pubs_with_prices_count = 0

        for pub in Pub.objects.all():

            if pub.closed or not pub.serving_guinness:
                continue

            if not len(Guinness.objects.filter(pub = pub)):
                continue

            sum_total += Guinness.objects.filter(pub = pub).order_by('-id')[0].price
            pubs_with_prices_count += 1

        average_price = sum_total / pubs_with_prices_count if pubs_with_prices_count else 0

        return average_price

    def calculate_standard_deviation(self):
        """
            Calculate standard deviation from pubs with prices.
            Uses most recent price for each pub.
        """
        average_price = self.calculate_average_price()

        if average_price == 0:
            return 0

        pubs_with_prices_count = 0
        variance_tmp = 0

        for pub in Pub.objects.all():

            if pub.closed or not pub.servingGuinness:
                continue

            if not len(Guinness.objects.filter(pub = pub)):
                continue

            price = Guinness.objects.filter(pub = pub).order_by('-id')[0].price
            pubs_with_prices_count += 1

            variance_tmp += math.pow(price - average_price, 2)

        variance = Decimal(variance_tmp) / pubs_with_prices_count

        standard_deviation = variance.sqrt()

        return standard_deviation

    def calculate_closed_pubs(self):

        return len(Pub.objects.filter(closed = True))

    def calculate_not_serving_guinness(self):

        return len(Pub.objects.filter(serving_guinness = False))

    def calculate_percentage_visited(self):
        """
            Includes pubs marked as not serving Guinness
            and closed pubs with registered prices.
        """

        pubs_in_db = self.calculate_number_of_pubs()

        if pubs_in_db == 0:
            return 0

        pubs_visited_count = 0

        for pub in Pub.objects.all():

            if len(Guinness.objects.filter(pub = pub)) or not pub.serving_guinness:
                pubs_visited_count += 1

        percentage_visited = 100 * pubs_visited_count / Decimal(pubs_in_db)

        return percentage_visited

    def calculate_number_of_users(self):

        return len(User.objects.all())

    def calculate_average_star_ratings(self):

        for pub in Pub.objects.all():

            pub_prices = Guinness.objects.filter(pub = pub)

            if not len(pub_prices):
                continue

            num_prices_with_rating = 0
            cumulative_rating = Decimal('0.00')

            for price in pub_prices:
                if price.star_rating:
                    num_prices_with_rating += 1
                    cumulative_rating += price.star_rating

            if num_prices_with_rating:
                pub.average_rating = cumulative_rating / num_prices_with_rating
            else:
                pub.average_rating = None

            pub.save()

    def calculate_latest_pub_prices(self):
        """
            Fill in last_price and last_submission_time
            for each pub.
        """
        for pub in Pub.objects.all():

            pub_prices = Guinness.objects.filter(pub = pub).order_by('-id')

            if not len(pub_prices):
                pub.last_price = None
                pub.last_submission_time = None
            else:
                pub.last_price = pub_prices[0].price
                pub.last_submission_time = pub_prices[0].creation_date

            pub.save()

    def calculate_user_contributions(self):
        """
            Populate all GuindexUser fields for each User
        """

        logger.info("Calculating User Contributions")

        for user in User.objects.all():

            logger.debug("Calculating contributions for User %s", user)

            if not hasattr(user, 'guindexuser'):
                logger.debug("Need to create GuindexUser for User %s", user)

                guindexuser = GuindexUser()

                guindexuser.user = user
                guindexuser.save()

            number_of_current_verifications = 0
            number_of_first_verifications   = 0
            number_of_pubs_visited          = 0

            for pub in Pub.objects.all():

                price_list = Guinness.objects.filter(pub = pub).order_by('id')

                price_list_len = len(price_list)

                if not price_list_len:
                    continue

                if price_list[price_list_len - 1].creator == user:
                    number_of_current_verifications = number_of_current_verifications + 1

                if price_list[0].creator == user:
                    number_of_first_verifications = number_of_first_verifications + 1

                if len(Guinness.objects.filter(pub = pub, creator = user)):
                    number_of_pubs_visited = number_of_pubs_visited + 1

            user.guindexuser.original_prices       = number_of_first_verifications
            user.guindexuser.current_verifications = number_of_current_verifications
            user.guindexuser.pubs_visited          = number_of_pubs_visited

            """
                Note: pubs_visited may be a bad name. We count pubs marked as
                not serving_guinness as visited, yet we have no way of knowing who registered
                that mark. Maybe change name to pubsPriced?
            """

            user.guindexuser.save()
