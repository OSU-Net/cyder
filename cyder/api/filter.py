from rest_framework import filters

class SearchFieldFilter(filters.BaseFilterBackend):
    """Filter based on record attributes."""

    def filter_queryset(self, request, queryset, view):
        ALLOWED_ENDINGS = ('__exact', '__iexact', '__contains', '__icontains',
                '__gt', '__gte', '__lt', '__lte', '__startswith',
                '__istartswith', '__endswith', '__iendswith', '__isnull',
                '__search',)

        q_include = {}
        q_exclude = {}

        for q in request.QUERY_PARAMS:
            if q.startswith("i_") and q.endswith(ALLOWED_ENDINGS):
                q_include[q[2:]] = request.QUERY_PARAMS[q]
            elif q.startswith("e_") and q.endswith(ALLOWED_ENDINGS):
                q_exclude[q[2:]] = request.QUERY_PARAMS[q]

        if len(q_include) or len(q_exclude):
            return queryset.filter(**q_include).exclude(**q_exclude)

        return queryset
