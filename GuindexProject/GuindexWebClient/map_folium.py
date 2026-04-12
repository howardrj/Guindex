# -*- coding: utf-8 -*-
"""
Live Folium map from the Guindex DB — same approach as
portfolio_website/pages/view_enabler_functions.py, but using Django ORM
instead of pandas/guindex package.
"""
import logging
import statistics

import folium
from django.utils.html import escape
from folium.plugins import MarkerCluster

from Guindex.models import Pub

logger = logging.getLogger(__name__)


def _add_osm_tiles(m):
    """
    OSM tile usage policy: tile requests should include a Referer (typically the page origin).
    Use strict-origin-when-cross-origin — never no-referrer (that strips Referer and triggers OSM warnings).
    """
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="OpenStreetMap",
        referrerPolicy="strict-origin-when-cross-origin",
    ).add_to(m)


def create_guindex_map(county=None):
    """
    Build a Folium map of approved pubs. Optional ``county`` filters to one county.

    Returns a ``folium.Map`` instance; the view passes ``._repr_html_()`` to the
    template with ``|safe`` (see portfolio ``pages/guindex_map.html``).
    """
    qs = Pub.objects.all()
    if county:
        qs = qs.filter(county=county)

    pubs = list(
        qs.iterator(
            chunk_size=500,
        )
    )

    if not pubs:
        guindex_map = folium.Map(
            location=[53.265, -7.71],
            zoom_start=7,
            control_scale=True,
            tiles=None,
        )
        _add_osm_tiles(guindex_map)
        return guindex_map

    lats = [float(p.latitude) for p in pubs]
    lngs = [float(p.longitude) for p in pubs]
    av_lat = statistics.median(lats)
    av_lon = statistics.median(lngs)

    guindex_map = folium.Map(
        location=[av_lat, av_lon],
        control_scale=True,
        tiles=None,
    )
    _add_osm_tiles(guindex_map)

    guindex_map.fit_bounds(
        [
            [min(lats), min(lngs)],
            [max(lats), max(lngs)],
        ]
    )

    cluster = MarkerCluster(
        options={"disableClusteringAtZoom": 14},
    ).add_to(guindex_map)

    for pub in pubs:
        lat = float(pub.latitude)
        lng = float(pub.longitude)
        name = escape(pub.name)

        if pub.closed:
            closed_icon = folium.Icon(
                prefix="fa",
                icon="window-close",
                color="black",
                icon_color="white",
            )
            marker = folium.Marker(
                [lat, lng],
                popup=name + " - closed",
                icon=closed_icon,
            )
        elif not pub.servingGuinness:
            not_serving_icon = folium.Icon(
                prefix="fa",
                icon="exclamation",
                color="red",
            )
            marker = folium.Marker(
                [lat, lng],
                popup=name + " - not serving Guinness",
                icon=not_serving_icon,
            )
        elif pub.lastPrice is not None:
            date_str = ""
            if pub.lastSubmissionTime:
                date_str = pub.lastSubmissionTime.date().isoformat()
            price_icon = folium.Icon(
                prefix="fa",
                icon="beer",
                color="green",
            )
            marker = folium.Marker(
                [lat, lng],
                popup=(
                    f"{name} - €{pub.lastPrice},"
                    f" Submitted: {date_str}"
                ),
                icon=price_icon,
            )
        else:
            no_price_icon = folium.Icon(
                prefix="fa",
                icon="question",
                color="lightgray",
            )
            marker = folium.Marker(
                [lat, lng],
                popup=name + " - No data submitted",
                icon=no_price_icon,
            )

        marker.add_to(cluster)

    return guindex_map
