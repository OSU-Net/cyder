import operator

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


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
    for title, value in objects[0].details()['data']:
        headers.append(title)
    if extra_cols:
        for col in extra_cols:
            headers.append(col['header'])
    if views:
        headers.append('Views')
    headers.append('Actions')

    for i, obj in enumerate(objects):
        row_data = []

        # Columns.
        for title, value in obj.details()['data']:
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
                         'url': ['#', obj.get_delete_url()],
                         'data': [[('pk', obj.id)], None],
                         'class': ['update', 'delete']})

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


def qd_to_py_dict(qd):
    """Django QueryDict to Python dict."""
    ret = {}
    for k in qd:
        ret[k] = qd[k]
    return ret
