import logging
import csv
import pytz
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from UserProfile.models import UserProfile

from Guindex.models import Pub, Guinness

logger = logging.getLogger(__name__)

# Hard coded names of columns
CLOSED             = 0
PUB_NAME           = 1
LATITUDE           = 2
LONGITUDE          = 3
PRICE              = 4
FIRST_ADDED_BY     = 5
FIRST_ADDED_DATE   = 6
LAST_VERIFIED_BY   = 7
LAST_VERIFIED_DATE = 8
FIRST_USER_INDEX   = 9


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        with open('Guindex/management/commands/guindex.csv') as csvfile:

            parsed_csv = csv.reader(csvfile, delimiter=',')

            first_row = next(parsed_csv)

            print("Creating UserProfiles ...")

            for username in first_row[FIRST_USER_INDEX:]:

                email = ""

                if username == "RMG":
                    email = "mcguinro@tcd.ie"
                elif username == "JB":
                    email = "jamesy.bingham@gmail.com"
                elif username == "DP":
                    email = "purdyd@tcd.ie"
                elif username == "COC":
                    email = "ocallaco@tcd.ie"
                elif username == "BOC":
                    email = "everythingoftheory10@gmail.com"  # TODO Change this
                elif username == "ES":
                    email = "esheeri@tcd.ie"
                elif username == "KON":
                    email = "oneillk3@tcd.ie"
                elif username == "SOS":
                    email = "osulls11@tcd.ie"
                elif username == "SH":
                    email = "sharding@tcd.ie"
                elif username == "MOS":
                    email = "marc.osullivan67@gmail.com"
                elif username == "SC":
                    email = "corbetsi@tcd.ie"
                elif username == "AD":
                    email = "drewcaravan@gmail.com"
                elif username == "SP":
                    email = "porters1@tcd.ie"
                elif username == "MK":
                    email = "kremerm@tcd.ie"

                if not email == "":

                    print("Creating user %s" % username)

                    user = User.objects.create_user(username, email, 'changemenow')
                    user.is_staff = True
                    user.is_active = True
                    user.save()

                    user_profile = UserProfile()
                    user_profile.user = user
                    user_profile.accountActivationKey = 'activated'
                    user_profile.save()

                else:
                    print("Blank email! Exiting!")
                    return

            # Create Other User
            print("Creating user %s" % username)

            user = User.objects.create_user('Other', 'everythingoftheory10@gmail.com', 'changemenow')
            user.is_staff = True
            user.is_active = True
            user.save()

            user_profile = UserProfile()
            user_profile.user = user
            user_profile.accountActivationKey = 'activated'
            user_profile.save()

            print("Creating Pubs ...")
            for row in parsed_csv:

                print("Creating pub %s" % row[PUB_NAME])

                pub = Pub()

                pub.name      = row[PUB_NAME]
                pub.latitude  = Decimal(row[LATITUDE])
                pub.longitude = Decimal(row[LONGITUDE])
                pub.closed    = len(row[CLOSED])
                pub.mapLink   = "https://www.google.ie/maps/@%f,%f" % (pub.latitude, pub.longitude)

                pub.save()

        with open('Guindex/management/commands/guindex.csv') as csvfile:

            print("Creating Guini ...")

            parsed_csv = csv.reader(csvfile, delimiter=',')

            first_row = next(parsed_csv)

            for row in parsed_csv:

                processed_pub_names = {}

                serving_guinness = True

                try:
                    price = Decimal(row[PRICE][3:])
                except:
                    print("Failed to make decimal from price %s" % row[PRICE][3:])

                    if row[PRICE]= "N.A."
                        serving_guinness = False
                    else:
                        return

                pub_name = row[PUB_NAME]

                print("Adding guini for pub %s" % pub_name)

                if pub_name in processed_pub_names:
                    processed_pub_names[pub_name] = processed_pub_names[pub_name] + 1
                else:
                    processed_pub_names[pub_name] = 0

                try:
                    pub = Pub.objects.filter(name = pub_name)[processed_pub_names[pub_name]]
                except:
                    print("Failed to find pub %d with name %s" % (processed_pub_names[pub_name], pub_name))
                    return

                if not serving_guinness:
                    pub.servingGuinness = False
                    pub.save()

                # Add last verified price
                last_verified_by = row[LAST_VERIFIED_BY]

                try:
                    user = User.objects.get(username = last_verified_by)
                except:
                    print("No user with username %s" % last_verified_by)
                    return

                try:
                    user_profile = UserProfile.objects.get(user = user)
                except:
                    print("No UserProfile with username %s" % last_verified_by)
                    return

                last_verified_date = row[LAST_VERIFIED_DATE].split('/')

                last_verified_datetime = pytz.utc.localize(datetime(int(last_verified_date[2]), int(last_verified_date[1]), int(last_verified_date[0])))

                # Create new Guinness object
                guinness = Guinness()

                guinness.creator = user_profile
                guinness.creationDate = last_verified_datetime
                guinness.price = price
                guinness.pub = pub

                guinness.save()

                # Add first verified if different
                first_verified_by = row[FIRST_ADDED_BY]

                try:
                    user = User.objects.get(username = first_verified_by)
                except:
                    print("No user with username %s" % first_verified_by)
                    return

                try:
                    user_profile = UserProfile.objects.get(user = user)
                except:
                    print("No UserProfile with username %s" % first_verified_by)
                    return

                first_verified_date = row[FIRST_ADDED_DATE].split('/')

                first_verified_datetime = pytz.utc.localize(datetime(int(first_verified_date[2]), int(first_verified_date[1]), int(first_verified_date[0])))

                if last_verified_by == first_verified_by and last_verified_date == first_verified_date:

                    print("Pub only has one price registered. Continuing")
                    continue

                # Create new Guinness object
                guinness = Guinness()

                guinness.creator = user_profile
                guinness.creationDate = first_verified_datetime
                guinness.price = price
                guinness.pub = pub

                guinness.save()

                # Add intermediate prices (if any)
                for loop_index, user_visits in enumerate(row[FIRST_USER_INDEX:]):

                    try:
                        num_visits = int(user_visits)
                    except:
                        continue

                    username = first_row[FIRST_USER_INDEX + loop_index]

                    recorded_so_far = 0

                    if first_verified_by == username:
                        recorded_so_far = recorded_so_far + 1

                    if last_verified_by == username:
                        recorded_so_far = recorded_so_far + 1

                    guini_to_create = num_visits - recorded_so_far

                    for i in range(0, guini_to_create):

                        try:
                            user = User.objects.get(username = username)
                        except:
                            print("No user with username %s" % username)
                            return

                        try:
                            user_profile = UserProfile.objects.get(user = user)
                        except:
                            print("No UserProfile with username %s" % username)
                            return

                        guinness = Guinness()

                        guinness.creator = user_profile
                        guinness.creationDate = last_verified_datetime - timedelta(minutes = i + 1)
                        guinness.price = price
                        guinness.pub = pub

                        guinness.save()
