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


class GuindexGoogleMapPlotter(gmplot.GoogleMapPlotter):

    def setMarkerPath(self):
        """
            Hack so generated map will request marker
            images via static url.
        """
        self.coloricon = '/static/images/%s.png'

    def write_point(self, f, lat, lon, color, title):
        """
            Overrride write_point function so we can include
            click event listener when adding markers to the map.
        """
        f.write('\t\tvar latlng = new google.maps.LatLng(%f, %f);\n' %
                (lat, lon))
        f.write('\t\tvar img = new google.maps.MarkerImage(\'%s\');\n' %
                (self.coloricon % color))
        f.write('\t\tvar marker = new google.maps.Marker({\n')
        f.write('\t\ttitle: "%s",\n' % title)
        f.write('\t\ticon: img,\n')
        f.write('\t\tposition: latlng,\n')
        f.write('\t\tdisableAutoPan: true\n')
        f.write('\t\t});\n')
        f.write('\t\tmarker.setMap(map);\n')
        f.write('\n')

        # Add click event listener to marker
        f.write('\t\tvar content = "<p> %s <p>";\n\n' % title)

        f.write('\t\tvar info_window = new google.maps.InfoWindow({\n')
        f.write('\t\t\tdisableAutoPan: true,\n')
        f.write('\t\t\tmaxWidth: 200\n')
        f.write('\t\t});\n\n')

        f.write("\t\tgoogle.maps.event.addListener(marker, 'click', (function (marker, content, info_window) {\n")
        f.write("\t\t\treturn function() {\n")
        f.write("\t\t\t\tinfo_window.setContent(content);\n")
        f.write("\t\t\t\tinfo_window.open(map, marker);\n")
        f.write("\t\t\t};\n")
        f.write("\t\t}) (marker, content, info_window));\n\n")

    def write_map(self,  f):
        """
            Overrride write_map function so we can include
            gestureHandling option when creating map.
        """
        f.write('\t\tvar centerlatlng = new google.maps.LatLng(%f, %f);\n' %
                (self.center[0], self.center[1]))
        f.write('\t\tvar myOptions = {\n')
        f.write('\t\t\tzoom: %d,\n' % (self.zoom))
        f.write('\t\t\tcenter: centerlatlng,\n')
        f.write('\t\t\tmapTypeId: google.maps.MapTypeId.ROADMAP,\n')
        f.write("\t\t\tgestureHandling: 'greedy'\n")
        f.write('\t\t};\n')
        f.write(
            '\t\tvar map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
        f.write('\n')


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        file_dir  = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../GuindexWebClient/templates/')
        file_name = 'guindex_map.html'

        gmap = GuindexGoogleMapPlotter(GuindexParameters.DUBLIN_CENTER_LATITUDE,
                                       GuindexParameters.DUBLIN_CENTER_LONGITUDE,
                                       GuindexParameters.MAP_ZOOM_LEVEL,
                                       settings.GOOGLE_MAPS_API_KEY)

        gmap.setMarkerPath()

        while True:

            logger.info("***** Generating Guindex Map Template *****")

            logger.info("Sleeping for %s seconds", GuindexParameters.MAP_GENERATION_PERIOD)

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
