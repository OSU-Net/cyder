import operator
import urllib
import urlparse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils.encoding import smart_str


def make_paginator(request, qs, num):
    """
    Paginator, returns object_list.
    """
    paginator = Paginator(qs, num)
    page = request.GET.get('page')
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        return paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)


def tablefy(objects, views=False, users=False, extra_cols=None):
    """Make list of table headers, rows of table data, list of urls
    that may be associated with table data, and postback urls.

    :param  objects: A list of objects to make table from.
    :type   objects: Generic object.
    :param  extra_cols: Extra columns to add outside of objects' .details()
    :type  extra_cols: [{'col_header': '',
                         'col_data': [{'value': '',
                                       'url': ''}]
                       },]
    """
    if not objects:
        return None

    if users:
        objects = [user.get_profile() for user in objects]

    headers = []
    data = []

    # Build headers.
    for title, sort_field, value in objects[0].details()['data']:
        headers.append([title, sort_field])
    if extra_cols:
        for col in extra_cols:
            headers.append([col['header'], col['sort_field']])
    if views:
        headers.append(['Views', None])
    headers.append(['Actions', None])

    for i, obj in enumerate(objects):
        row_data = []

        # Columns.
        for title, field, value in obj.details()['data']:
            # Build data.
            try:
                url = value.get_detail_url()
            except AttributeError:
                url = None
            row_data.append({'value': [value], 'url': [url]})

        if extra_cols:
            # Manual extra columns.
            for col in extra_cols:
                d = col['data'][i]
                row_data.append({'value': [d['value']], 'url': [d['url']]})

        if views:
            # Another column for views.
            view_field = None
            if hasattr(obj, 'views'):
                for view in obj.views.all():
                    if view_field:
                        view_field += ' ' + view.name
                    else:
                        view_field = view.name
                row_data.append({'value': [view_field], 'url': [None]})
            else:
                row_data.append({'value': ['None'], 'url': [None]})

        # Actions
        row_data.append({'value': ['Update', 'Delete'],
                         'url': [obj.get_update_url(), obj.get_delete_url()],
                         'data': [[('pk', obj.id)], None],
                         'class': ['update', 'delete'],
                         'img': ['/media/img/update.png',
                                 '/media/img/delete.png']})

        # Build table.
        data.append(row_data)

    return {
        'headers': headers,
        'postback_urls': [obj.details()['url'] for obj in objects],
        'data': data,
    }


def make_megafilter(Klass, term):
    """
    Builds a query string that searches over fields in model's
    search_fields.
    """
    megafilter = [Q(**{"{0}__icontains".format(field): term}) for field in
                  Klass.search_fields]
    return reduce(operator.or_, megafilter)


def _filter(request, Klass):
    if request.GET.get('filter'):
        return Klass.objects.filter(make_megafilter(Klass,
                                    request.GET.get('filter')))
    return Klass.objects.all()


def qd_to_py_dict(qd):
    """Django QueryDict to Python dict."""
    ret = {}
    for k in qd:
        ret[k] = qd[k]
    return ret


def model_to_post(post, obj):
    """
    Updates requests's POST dictionary with values from object, for update
    purposes.
    """
    ret = qd_to_py_dct(post)
    for k, v in model_to_dict(obj).iteritems():
        if k not in post:
            ret[k] = v
    return ret


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

    query_string = urllib.urlencode([(k, v) for k, v in query_dict.items()
                                     if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()
