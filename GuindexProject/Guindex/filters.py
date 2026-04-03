from django.db.models import F, Q

from rest_framework_datatables.filters import DatatablesFilterBackend, is_valid_regex
from rest_framework_datatables.utils import get_param


class GuindexDatatablesFilterBackend(DatatablesFilterBackend):
    """
    Makes sure to always put NULLs last in query.
    """

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get("format") != "datatables":
            return queryset

        total_count = queryset.count()
        setattr(view, "_datatables_total_count", total_count)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        search_value = get_param(request, "search[value]")
        search_regex = get_param(request, "search[regex]") == "true"

        q = Q()
        for f in fields:
            if not f["searchable"]:
                continue
            names = f["name"] if isinstance(f["name"], list) else [f["name"]]
            if search_value and search_value != "false":
                for fname in names:
                    if search_regex:
                        if is_valid_regex(search_value):
                            q |= Q(**{"%s__iregex" % fname: search_value})
                    else:
                        q |= Q(**{"%s__icontains" % fname: search_value})
            f_search_value = f.get("search_value")
            f_search_regex = f.get("search_regex") == "true"
            if f_search_value:
                for fname in names:
                    if f_search_regex:
                        if is_valid_regex(f_search_value):
                            q &= Q(**{"%s__iregex" % fname: f_search_value})
                    else:
                        q &= Q(**{"%s__icontains" % fname: f_search_value})

        if q != Q():
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = total_count
        setattr(view, "_datatables_filtered_count", filtered_count)

        if ordering:
            order_exprs = []
            for name in ordering:
                if name.startswith("-"):
                    order_exprs.append(F(name[1:]).desc(nulls_last=True))
                else:
                    order_exprs.append(F(name).asc(nulls_last=True))
            queryset = queryset.order_by(*order_exprs)

        return queryset
