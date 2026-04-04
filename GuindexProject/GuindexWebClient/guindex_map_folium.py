# -*- coding: utf-8 -*-
"""Build Folium pub maps from the Guindex database (by county)."""

import logging
import re

import folium
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster

from Guindex.GuindexParameters import GuindexParameters
from Guindex.models import Pub

from GuindexWebClient.forms import GUINDEX_MAP_ALL_PUBS

logger = logging.getLogger(__name__)

# Default Folium layer (resolves to OSM via xyzservices). Tile requests need a
# non-empty Referer; see Referrer-Policy on guindex_map_page responses.
FOLIUM_DEFAULT_TILES = "OpenStreetMap"

_COUNTY_KEY_RE = re.compile(r"[^A-Za-z]")


def _county_gps_key(county: str) -> str:
    return _COUNTY_KEY_RE.sub("", county).upper()


def _county_default_center(county: str) -> tuple[float, float]:
    prefix = f"GPS_{_county_gps_key(county)}"
    try:
        lat_min = float(getattr(GuindexParameters, f"{prefix}_MIN_LATITUDE"))
        lat_max = float(getattr(GuindexParameters, f"{prefix}_MAX_LATITUDE"))
        lon_min = float(getattr(GuindexParameters, f"{prefix}_MIN_LONGITUDE"))
        lon_max = float(getattr(GuindexParameters, f"{prefix}_MAX_LONGITUDE"))
        return (lat_min + lat_max) / 2, (lon_min + lon_max) / 2
    except AttributeError:
        logger.warning("No GPS bounds for county %r; using Dublin centre", county)
        return (
            float(GuindexParameters.DUBLIN_CENTER_LATITUDE),
            float(GuindexParameters.DUBLIN_CENTER_LONGITUDE),
        )


def _empty_map_center_zoom(county: str) -> tuple[float, float, int]:
    """Default view when there are no coordinates to plot."""
    if county == GUINDEX_MAP_ALL_PUBS:
        return (
            float(GuindexParameters.DUBLIN_CENTER_LATITUDE),
            float(GuindexParameters.DUBLIN_CENTER_LONGITUDE),
            int(GuindexParameters.MAP_ZOOM_LEVEL),
        )
    av_lat, av_lon = _county_default_center(county)
    return av_lat, av_lon, 9


def create_guindex_map(county: str):
    """Create a Folium map of approved pubs for one county, or all pubs if county is GUINDEX_MAP_ALL_PUBS."""

    qs = Pub.objects.values(
        "name",
        "latitude",
        "longitude",
        "closed",
        "servingGuinness",
        "lastPrice",
        "lastSubmissionTime",
    )
    if county != GUINDEX_MAP_ALL_PUBS:
        qs = qs.filter(county=county)
    rows = list(qs)
    pubs = pd.DataFrame(rows)

    if pubs.empty:
        av_lat, av_lon, zoom = _empty_map_center_zoom(county)
        return folium.Map(
            location=[av_lat, av_lon],
            tiles=FOLIUM_DEFAULT_TILES,
            control_scale=True,
            zoom_start=zoom,
        )

    pubs = pubs.rename(
        columns={
            "servingGuinness": "serving_guinness",
            "lastPrice": "last_price",
            "lastSubmissionTime": "last_submission_time",
        }
    )

    pubs["latitude"] = pd.to_numeric(pubs["latitude"], errors="coerce")
    pubs["longitude"] = pd.to_numeric(pubs["longitude"], errors="coerce")
    pubs = pubs.dropna(subset=["latitude", "longitude"])

    if pubs.empty:
        av_lat, av_lon, zoom = _empty_map_center_zoom(county)
        return folium.Map(
            location=[av_lat, av_lon],
            tiles=FOLIUM_DEFAULT_TILES,
            control_scale=True,
            zoom_start=zoom,
        )

    pubs["last_price"] = pd.to_numeric(pubs["last_price"], errors="coerce")
    pubs["price"] = np.where(
        pubs["closed"] | (~pubs["serving_guinness"]),
        np.nan,
        pubs["last_price"],
    )
    pubs["date"] = pd.to_datetime(
        pubs["last_submission_time"], errors="coerce"
    ).dt.date

    av_lat = float(pubs["latitude"].median())
    av_lon = float(pubs["longitude"].median())

    guindex_map = folium.Map(
        location=[av_lat, av_lon],
        tiles=FOLIUM_DEFAULT_TILES,
        control_scale=True,
    )
    guindex_map.fit_bounds(
        [
            [float(pubs["latitude"].min()), float(pubs["longitude"].min())],
            [float(pubs["latitude"].max()), float(pubs["longitude"].max())],
        ]
    )

    # CircleMarker avoids Leaflet.awesome-markers + Font Awesome CDNs (often blocked
    # in iframes / by CSP).
    cluster = MarkerCluster(
        options={"disableClusteringAtZoom": 14},
    ).add_to(guindex_map)

    for _, pub in pubs.iterrows():
        lat_f = float(pub["latitude"])
        lon_f = float(pub["longitude"])

        if pub["closed"]:
            stroke, fill = "#000000", "#333333"
            popup_html = f"{pub['name']} - closed"
        elif not pub["serving_guinness"]:
            stroke, fill = "#b30000", "#e62e2e"
            popup_html = f"{pub['name']} - not serving Guinness"
        elif pd.notnull(pub["price"]):
            stroke, fill = "#1a7f1a", "#2db82d"
            submitted = (
                pub["date"] if pd.notna(pub["date"]) else "date unknown"
            )
            popup_html = (
                f"{pub['name']} - €{pub['price']:.2f}, "
                f"Submitted: {submitted}"
            )
        else:
            stroke, fill = "#666666", "#999999"
            popup_html = f"{pub['name']} - No data submitted"

        folium.CircleMarker(
            location=[lat_f, lon_f],
            radius=7,
            color=stroke,
            weight=2,
            fill=True,
            fill_color=fill,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(cluster)

    return guindex_map
