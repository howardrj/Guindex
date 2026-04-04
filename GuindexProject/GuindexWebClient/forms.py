# -*- coding: utf-8 -*-
from django import forms

from Guindex.GuindexParameters import GuindexParameters

# POST value for “show every pub”; must match create_guindex_map handling.
GUINDEX_MAP_ALL_PUBS = "__all__"


class GuindexMapCountyForm(forms.Form):
    """County selector for the interactive Folium pub map."""

    county = forms.ChoiceField(
        choices=[
            (GUINDEX_MAP_ALL_PUBS, "All pubs"),
            *[(c, c) for c in GuindexParameters.SUPPORTED_COUNTIES],
        ],
        label="County",
    )
