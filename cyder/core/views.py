from django.shortcuts import render

from cyder.base.views import (BaseCreateView, BaseDeleteView, BaseDetailView,
                              BaseListView, BaseUpdateView,
                              cy_view, cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.core.ctnr.forms import CtnrForm
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.forms import SystemForm
from cyder.core.system.models import System


def get_klasses(record_type):
    return {
        'ctnr': (Ctnr, CtnrForm, None),
        'system': (System, SystemForm, None),
    }.get(record_type, (None, None, None))


def core_view(request, pk=None):
    return cy_view(request, get_klasses, 'core/core_view.html', pk)


def core_get_update_form(request):
    return get_update_form(request, get_klasses)


def core_search_obj(request):
    return search_obj(request, get_klasses)


def core_delete(request, pk):
    return cy_delete(request, pk, get_klasses)


def core_table_update(request, pk, record_type=None):
    return table_update(request, pk, get_klasses, record_type)


def core_index(request):
    return render(request, 'core/core_index.html')


class CoreDeleteView(BaseDeleteView):
    """"""
    template_name = "core/core_confirm_delete.html"


class CoreDetailView(BaseDetailView):
    """"""
    template_name = "core/core_detail.html"


class CoreCreateView(BaseCreateView):
    """"""
    template_name = "core/core_form.html"


class CoreUpdateView(BaseUpdateView):
    """"""
    template_name = "core/core_form.html"


class CoreListView(BaseListView):
    """"""
    template_name = 'core/core_list.html'
