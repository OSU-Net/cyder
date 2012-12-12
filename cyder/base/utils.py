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
