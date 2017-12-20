import logging
import csv

from django.template.loader import render_to_string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from UserProfile.models import UserProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        with open('Guindex/management/commands/guindex.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                print(row)
                print(row[0])
                print(row[0],row[1],row[2],)
