from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.util import ErrorList
from django.shortcuts import render, get_object_or_404

from cyder.base.constants import get_klasses
from cyder.base.views import (BaseCreateView, BaseDeleteView,
                              BaseDetailView, BaseListView, BaseUpdateView,
                              cy_view, cy_delete, search_obj, table_update)
from cyder.cydhcp.forms import IpSearchForm
from cyder.cydhcp.network.utils import calc_networks, calc_parent
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs

import ipaddr


def cydhcp_view(request, pk=None):
    return cy_view(request, 'cydhcp/cydhcp_view.html', pk)


def cydhcp_create(request, pk=None):
    return cy_view(request, 'cydhcp/cydhcp_form.html', pk)


def cydhcp_search_obj(request):
    return search_obj(request)


def cydhcp_table_update(request, pk, obj_type=None):
    return table_update(request, pk, obj_type)


def cydhcp_detail(request, pk):
    obj_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk)
    attr_getter = getattr(obj, "{0}av_set".format(obj_type))
    return render(request, "{0}/{0}_detail.html".format(obj_type), {
        obj_type: obj,
        'attrs': attr_getter.all()
    })
