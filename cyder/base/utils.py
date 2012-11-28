from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    """Given a list of objects, build a matrix that is can be printed as a
    table. Also return the headers for that table. Populate the given url with
    the pk of the object. Return all headers, field array, and urls in a
    separate lists.

    :param  objects: A list of objects to make the matrix out of.
    :type   objects: AddressRecords
    """
    matrix = []
    urls = []
    headers = []
    if not objects:
        return (None, None, None)

    # Build the headers
    for title, value in objects[0].details():
        headers.append(title)
    if views:
        headers.append("Views")

    # Build the matrix and urls
    for obj in objects:
        row = []
        urls.append(obj.get_detail_url())
        for title, value in obj.details():
            row.append(value)
        if views:
            view_field = ""
            if hasattr(obj, 'views'):
                for view in obj.views.all():
                    view_field += view.name + ", "
                view_field = view_field.strip(", ")
                row.append(view_field)
            else:
                row.append('None')

        matrix.append(row)

    return (headers, matrix, urls)

