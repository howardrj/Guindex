from django.db.models import F

from rest_framework_datatables.filters import DatatablesFilterBackend


class GuindexDatatablesFilterBackend(DatatablesFilterBackend):
    """
    Datatables filtering compatible with current rest_framework_datatables
    (field metadata uses list-valued `name`). Optionally order with NULLs last
    on the primary sort column (SQLite-friendly).
    """

    def filter_queryset(self, request, queryset, view):
        if not self.check_renderer_format(request):
            return queryset

        total_count = view.get_queryset().count()
        self.set_count_before(view, total_count)

        if len(getattr(view, 'filter_backends', [])) > 1:
            filtered_count_before = queryset.count()
        else:
            filtered_count_before = total_count

        datatables_query = self.parse_datatables_query(request, view)

        q = self.get_q(datatables_query)
        if q:
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = filtered_count_before
        self.set_count_after(view, filtered_count)

        ordering = self.get_ordering(request, view, datatables_query['fields'])
        if ordering:
            primary = ordering[0]
            rest = ordering[1:]
            if primary.startswith('-'):
                field_name = primary[1:]
                queryset = queryset.order_by(
                    F(field_name).desc(nulls_last=True), *rest
                )
            else:
                queryset = queryset.order_by(
                    F(primary).asc(nulls_last=True), *rest
                )

        return queryset
