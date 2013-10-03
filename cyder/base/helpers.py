# Jingo helpers (Jinja2 custom filters)
import re
import json
import string
import urllib
import urlparse

from django.utils.encoding import smart_str
from django.db.models import ForeignKey

from jingo import register

mac_re = re.compile("(([0-9a-f]){2}:){5}([0-9a-f]){2}$")


def strip_if_mac_with_colons(word):
    if mac_re.match(word):
        word = word.replace(':', '')
    return word


def clean_sort_param(request):
    """
    Handles empty and invalid values for sort and sort order
    'id' by ascending is the default ordering.
    """
    sort = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    if order not in ('desc', 'asc'):
        order = 'asc'
    return sort, order


def do_sort(request, qs):
    """Returns an order_by string based on request GET parameters"""
    sort, order = clean_sort_param(request)
    if sort == "id" and hasattr(qs.model, 'eg_metadata'):
        fields = [m['name'] for m in qs.model.eg_metadata()['metadata']]
        if fields[0] in [f.name for f in qs.model._meta.fields]:
            sort, order = fields[0], 'asc'

    if sort in ['ip_str', 'network_str']:
        sort = 'ip_lower'

    if sort == 'start_str':
        sort = 'start_lower'

    if sort in [f.name for f in qs.model._meta.fields]:
        try:
            field = getattr(qs.model, sort).field

            if isinstance(field, ForeignKey):
                qs = qs.select_related(sort)
                sort = "__".join([sort, field.rel.to.display_fields[0]])
        except AttributeError:
            pass

    if order == 'asc':
        order_by = sort
    else:
        order_by = '-%s' % sort

    return qs.order_by(order_by)


def create_sort_link(pretty_name, sort_field, get_params, sort, order):
    """Generate table header sort links.

    pretty_name -- name displayed on table header
    sort_field -- name of the sort_type GET parameter for the column
    get_params -- additional get_params to include in the sort_link
    sort -- the current sort type
    order -- the current sort order
    """
    get_params.append(('sort', sort_field))

    if sort == sort_field and order == 'asc':
        # Have link reverse sort order to desc if already sorting by desc.
        get_params.append(('order', 'desc'))
    else:
        # Default to ascending.
        get_params.append(('order', 'asc'))

    # Show little sorting sprite if sorting by this field.
    url_class = ''
    if sort == sort_field:
        url_class = ' class="sort-icon ed-sprite-sort-%s"' % order

    return u'<a href="?%s"%s>%s</a>' % (urllib.urlencode(get_params),
                                        url_class, pretty_name)


def urlparams(url_, hash=None, **query):
    """
    Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = urllib.urlencode([(k2, v2) for k2, v2 in query_dict.items()
                                     if v2 is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()


urlparams = register.filter(urlparams)


@register.filter
def humanized_class_name(obj, *args, **kwargs):
    """
    Adds spaces to camel-case class names.
    """
    humanized = ''

    class_name = obj.__class__.__name__

    for i in range(len(class_name)):
        humanized += class_name[i]
        # Insert space between every camel hump.
        if (i + 1 < len(class_name) and class_name[i].islower()
                and class_name[i + 1].isupper()):
            humanized += ' '

    return humanized


@register.filter
def humanized_model_name(model_name, *args, **kwargs):
    """
    Capitalize and add spaces to underscored db table names.
    """
    model_name.replace('_', ' ')
    return string.join([word[0].upper() + word[1:]
                        for word in model_name.split()])


@register.filter
def prettify_obj_type(obj_type, *args, **kwargs):
    """
    Turns all-lowercase record type string to all caps or splits into
    words if underscore.
    e.g. 'cname' to 'CNAME' and 'address_record' to 'Address Record'
    """
    if not obj_type:
        return

    prettified = ''
    if obj_type in ['range', 'network', 'site', 'domain', 'nameserver',
                    'workgroup', 'system']:
        return obj_type[0].upper() + obj_type[1:]
    elif '_' in obj_type:
        capitalize = True
        for i in range(len(obj_type)):
            if capitalize:
                prettified += obj_type[i].upper()
                capitalize = False
            elif obj_type[i] == '_':
                prettified += ' '
                capitalize = True
            else:
                prettified += obj_type[i]
        if 'Av' in prettified:
            prettified = prettified.split(' ')[0] + ' Attribute'
            return prettified
        return prettified

    return obj_type.upper()


@register.function
def a_or_an(next_word):
    """
    Chooses 'a' or 'an' depending on first letter of next word.
    Add in special cases if next word is 'hour' or something.
    """
    if next_word[0] in ['a', 'e', 'i', 'o', 'u']:
        return 'an'
    else:
        return 'a'


@register.function
def has_attr(obj, attr):
    return hasattr(obj, attr)


@register.filter
def to_json(obj):
    """Object to JSON."""
    return json.dumps(obj)


@register.function
def sort_link(request, pretty_name, sort_field):
    """Get table header sort links.

    pretty_name -- name displayed on table header
    sort_field -- name of get parameter, referenced to in views
    """
    sort, order = clean_sort_param(request)

    # Copy search/filter GET parameters.
    get_params = [(k, v) for k, v in request.GET.items()
                  if k not in ('sort', 'order')]

    return create_sort_link(pretty_name, sort_field, get_params,
                            sort, order)


def get_display(obj):
    return " - ".join(getattr(obj, f) for f in obj.display_fields)
