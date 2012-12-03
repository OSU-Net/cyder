from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import NoReverseMatch


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


def tablefy(objects, views=False):
    """Make list of table headers, rows of table data, list of urls
    that may be associated with table data, and metadata about the rows to be
    used as HTML data attributes.

    :param  objects: A list of objects to make table from.
    :type   objects: Generic object.
    """
    if not objects:
        return None

    metadata = []
    headers = []
    data = []
    urls = []

    # Build headers.
    for title, field, value in objects[0].details()['data']:
        headers.append(title)
    if views:
        headers.append('Views')

    for obj in objects:
        row_data = []

        for title, field, value in obj.details()['data']:
            # Build data.
            try:
                url = value.get_detail_url()
            except AttributeError:
                url = None
            row_data.append({'value': value, 'field': field, 'url': url})

        # Views.
        if views:
            view_field = None
            if hasattr(obj, 'views'):
                for view in obj.views.all():
                    if view_field:
                        view_field += ' ' + view.name
                    else:
                        view_field = view.name
                row_data.append({'value': view_field, 'field': 'view', 'url': None})
            else:
                row_data.append({'value': 'None', 'field': 'view', 'url': None})

        # Build table.
        data.append(row_data)

    return {
        'metadata': [obj.details()['metadata'] for obj in objects],
        'headers': headers,
        'data': data,
    }
