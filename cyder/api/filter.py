from rest_framework import filters

class SearchFieldFilter(filters.BaseFilterBackend):
    """Filter based on record attributes."""

    def filter_queryset(self, request, queryset, view):
        if not getattr(view, 'search_fields', None):
            return queryset

        query = {}

        for f in view.search_fields:
            if f in request.QUERY_PARAMS:
                query[f + '__iexact'] = request.QUERY_PARAMS[f]

        if len(query):
            return queryset.filter(**query)

        return queryset
