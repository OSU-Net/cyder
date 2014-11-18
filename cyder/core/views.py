from django.shortcuts import render

from cyder.base.views import cy_view, search_obj, table_update


def core_view(request, pk=None):
    return cy_view(request, 'core/core_view.html', pk)


def core_search_obj(request):
    return search_obj(request)


def core_table_update(request, pk, obj_type=None):
    return table_update(request, pk, obj_type)


def core_index(request):
    return render(request, 'core/core_index.html')
