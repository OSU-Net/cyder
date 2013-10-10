from rest_framework import exceptions, filters

from cyder.core.ctnr.models import Ctnr


UNHANDLED_PARAMS = 'page', 'count',


class InvalidQuery(exceptions.APIException):
    status_code = 400

    def __init__(self, detail):
        self.detail = detail
        super(InvalidQuery, self).__init__(self)


class SearchFieldFilter(filters.BaseFilterBackend):
    """Filter based on record attributes."""

    def filter_queryset(self, request, queryset, view):
        q_include = {}
        q_exclude = {}
        q_attributes = {}

        kv_queryset = None
        f_queryset = None

        parent_model = queryset.model
        parent_name = parent_model.__name__.lower()
        keyvalue_model = getattr(view, 'keyvaluemodel', None)

        matching = lambda k, v: set(
            keyvalue_model.objects.filter(
                attribute__name__iexact=k,
                value__iexact=v
            ).values_list(
                parent_name, flat=True
            )
        )

        for q in request.QUERY_PARAMS:
            p = request.QUERY_PARAMS[q]
            if q.endswith(("__regex", "__iregex")):
                continue

            elif q.startswith("i:"):
                q_include[q[2:]] = p

            elif q.startswith("e:"):
                q_exclude[q[2:]] = p

            elif q.startswith("a:"):
                # key value matching
                q_attributes[q[2:]] = p

            elif q == "sort":
                sort = p.split(',')
                queryset = queryset.order_by(*sort)

            elif q == "ctnr_id":
                queryset &= parent_model.filter_by_ctnr(
                    Ctnr.objects.get(id=int(p)))

            elif q == "ctnr":
                queryset = queryset & parent_model.filter_by_ctnr(
                    Ctnr.objects.get(name=p)).all()

            elif q not in UNHANDLED_PARAMS:
                raise InvalidQuery(
                    "'{}' is not a valid query parameter. Check your spelling "
                    "and make sure you used the proper prefix, if appropriate."
                    .format(q)
                )

        if q_attributes:
            if getattr(view, 'avmodel', None):
                parent_set_list = (
                    matching(k, q_attributes[k]) for k in q_attributes)
                parent_ids = reduce((lambda x, y: x & y), parent_set_list)
                kv_queryset = queryset.filter(id__in=parent_ids)
            else:
                raise InvalidQuery("This record type does not have attributes.")

        if q_include or q_exclude:
            f_queryset = queryset.filter(**q_include).exclude(**q_exclude)

        if kv_queryset is not None and f_queryset is not None:
            return (kv_queryset & f_queryset).all()
        elif kv_queryset is not None:
            return kv_queryset.all()
        elif f_queryset is not None:
            return f_queryset.all()
        else:
            return queryset.all()
