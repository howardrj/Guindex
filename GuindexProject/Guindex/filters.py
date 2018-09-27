from django.db.models import Q, F

from rest_framework_datatables.filters import DatatablesFilterBackend


class GuindexDatatablesFilterBackend(DatatablesFilterBackend):
    """
        Makes sure to always put NULLs last in query.
    """
    def filter_queryset(self, request, queryset, view):
        """
            Changed slightly from filter_queryset in rest_framework_datatables.filters
            to always put NULL values last.
        """
        if request.query_params.get('format') != 'datatables':
            return queryset

        total_count = queryset.count()
        # set the queryset count as an attribute of the view for later
        # TODO: find a better way than this hack
        setattr(view, '_datatables_total_count', total_count)

        # parse query params
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        search_value = getter('search[value]')
        search_regex = getter('search[regex]') == 'true'

        # filter queryset
        q = Q()
        for f in fields:
            if not f['searchable']:
                continue
            if search_value and search_value != 'false':
                if search_regex:
                    if self.is_valid_regex(search_value):
                        q |= Q(**{'%s__iregex' % f['name']: search_value})
                else:
                    q |= Q(**{'%s__icontains' % f['name']: search_value})
            f_search_value = f.get('search_value')
            f_search_regex = f.get('search_regex') == 'true'
            if f_search_value:
                if f_search_regex:
                    if self.is_valid_regex(f_search_value):
                        q &= Q(**{'%s__iregex' % f['name']: f_search_value})
                else:
                    q &= Q(**{'%s__icontains' % f['name']: f_search_value})

        if q != Q():
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = total_count
        # set the queryset count as an attribute of the view for later
        # TODO: maybe find a better way than this hack ?
        setattr(view, '_datatables_filtered_count', filtered_count)

        # order queryset
        if len(ordering):
            # TODO My hack is here
            # Understand these lines of code at some point.
            # I blindly took this from stackoverflow and rejigged it
            # until it worked
            if ordering[0][0] == '-':
                queryset = queryset.order_by(F(ordering[0][1:]).asc(nulls_last=True))
            else:
                queryset = queryset.order_by(F(ordering[0]).desc(nulls_last=True))

        return queryset
