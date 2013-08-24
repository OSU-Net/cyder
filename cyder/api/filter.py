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
        keyvalue_model = getattr(view, 'keyvaluemodel', None)

        kv_queryset = None
        f_queryset = None

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
            things = parent_model.objects.all()
            kv_queryset = keyvalue_model.objects.all()
            for key in q_keyvalues:
                x = kv_queryset.filter(key=key, value=q_keyvalues[key])
                things = things & x.values_list

        kv_queryset = set(kv_queryset.values_list('system', flat=True))

        if len(q_include) or len(q_exclude):
            f_queryset = set(queryset.filter(**q_include).exclude(**q_exclude))

        if kv_queryset and f_queryset:
            return kv_queryset & f_queryset
        elif kv_queryset:
            return kv_queryset
        elif f_queryset:
            return f_queryset
        else:
            return queryset
