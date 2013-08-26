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
        q_keyvalues = {}

        parent_model = queryset.model
        parent_name = parent_model.__name__.lower()
        keyvalue_model = getattr(view, 'keyvaluemodel', None)

        kv_queryset = None
        f_queryset = None

        matching = lambda k, v: set(
            keyvalue_model.objects.filter(
                    key__iexact=k,
                    value__iexact=v
                ).values_list(
                    parent_name, flat=True
            )
        )

        for q in request.QUERY_PARAMS:
            if q.startswith("i_") and q.endswith(ALLOWED_ENDINGS):
                q_include[q[2:]] = request.QUERY_PARAMS[q]
            elif q.startswith("e_") and q.endswith(ALLOWED_ENDINGS):
                q_exclude[q[2:]] = request.QUERY_PARAMS[q]
            elif q.startswith("k_"):
                # key value matching
                q_keyvalues[q[2:]] = request.QUERY_PARAMS[q]

        if not getattr(view, 'keyvaluemodel', None):
            return queryset

        if len(q_keyvalues):
            parent_set_list = (
                matching(k, q_keyvalues[k]) for k in q_keyvalues)
            parent_ids = reduce((lambda x, y: x & y), parent_set_list)
            kv_queryset = parent_model.objects.filter(id__in=parent_ids)

        if len(q_include) or len(q_exclude):
            f_queryset = queryset.filter(**q_include).exclude(**q_exclude)

        if kv_queryset and f_queryset:
            return kv_queryset & f_queryset
        elif kv_queryset:
            return kv_queryset
        elif f_queryset:
            return f_queryset
        else:
            return queryset
