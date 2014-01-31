from rest_framework import exceptions, filters

from cyder.core.ctnr.models import Ctnr


UNHANDLED_PARAMS = 'page', 'count',


class InvalidQuery(exceptions.APIException):
    status_code = 400


def namehack(field):
    """
    This function is the meat of a hack to handle an issue where trying to
    filter by attribute or view led to a very strange-seeming error. The issue
    is that attribute names in records with attributes and view names in DNS
    records are represented using SlugRelatedFields so they appear with friendly
    names (like "Hardware type" in the former case and "public" in the latter
    case), but because of how this filter module is written, it will just
    attempt to search by the related field, confusing Django when it gets a
    query requesting a field with a string primary key like "public".
    """
    if field.endswith(("attribute", "views")):
        return field + "__name"
    else:
        return field


class SearchFieldFilter(filters.BaseFilterBackend):
    """Filter based on record attributes."""

    def filter_queryset(self, request, queryset, view):
        q_include = {}
        q_exclude = {}
        q_attributes = {}

        kv_queryset = None
        f_queryset = None

        parent_model = queryset.model

        for q in request.QUERY_PARAMS:
            p = request.QUERY_PARAMS[q]
            if q.endswith(("__regex", "__iregex")):
                continue

            elif q.startswith("i:"):
                q_include[namehack(q[2:])] = p

            elif q.startswith("e:"):
                q_exclude[namehack(q[2:])] = p

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
            avmodel = getattr(view, 'avmodel', None)
            if avmodel:
                avmodel_entity = getattr(view, 'avmodel_entity', 'entity')
                matching = lambda k, v: set(
                    avmodel.objects.filter(
                        attribute__name__iexact=k,
                        value__iexact=v
                    ).values_list(
                        avmodel_entity,
                        flat=True
                    )
                )

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
