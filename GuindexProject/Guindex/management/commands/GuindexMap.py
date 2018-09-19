#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time
import os
from gmplot import gmplot

from django.core.management.base import BaseCommand
from django.conf import settings

from Guindex.models import Pub, Guinness
from Guindex.GuindexParameters import GuindexParameters


logger = logging.getLogger(__name__.split('.')[-1])


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        file_dir  = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../GuindexWebClient/templates/')
        file_name = 'guindex_map.html' 

        while True:

            logger.info("***** Generating Guindex Map Template *****")

            logger.info("Sleeping for %s seconds", GuindexParameters.MAP_GENERATION_PERIOD)

            gmap = gmplot.GoogleMapPlotter(GuindexParameters.DUBLIN_CENTER_LATITUDE,
                                           GuindexParameters.DUBLIN_CENTER_LONGITUDE,
                                           GuindexParameters.MAP_ZOOM_LEVEL,
                                           settings.GOOGLE_MAPS_API_KEY,
                                           True) # Utilise hack I added to gmplot

            for pub in Pub.objects.all():

                if pub.closed:
                    colour = 'red'
                    marker_title = '%s - Closed' % pub.name.encode('utf-8')
                elif not pub.servingGuinness:
                    colour = 'black'
                    marker_title = '%s - Not Serving Guinness' % pub.name.encode('utf-8')
                elif len(Guinness.objects.filter(pub = pub)):
                    price = Guinness.objects.filter(pub = pub).order_by('-id')[0].price
                    colour = 'green'
                    marker_title = '%s - €%.2f' % (pub.name.encode('utf-8'), price)
                else:
                    colour = 'darkgray'
                    marker_title = '%s - Not Yet Visited' % pub.name.encode('utf-8') 
                 
                gmap.marker(pub.latitude, pub.longitude, colour, title = marker_title)

            gmap.draw(file_dir + file_name)

            time.sleep(GuindexParameters.MAP_GENERATION_PERIOD)
