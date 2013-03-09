from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.util import ErrorList
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from cyder.base.views import (BaseCreateView, BaseDeleteView,
                              BaseDetailView, BaseListView, BaseUpdateView,
                              cy_view, cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.cydhcp.forms import IpSearchForm
from cyder.cydhcp.network.utils import calc_networks, calc_parent
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.forms import NetworkForm
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.range.forms import RangeForm
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.site.forms import SiteForm
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vlan.forms import VlanForm
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.vrf.forms import VrfForm
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydhcp.workgroup.forms import WorkgroupForm

import ipaddr
import simplejson as json


def get_klasses(record_type):
    return {
        'network': (Network, NetworkForm, None),
        'range': (Range, RangeForm, None),
        'site': (Site, SiteForm, None),
        'vlan': (Vlan, VlanForm. None),
        'static_interface': (StaticInterface, StaticInterfaceForm. None),
        'dynamic_interface': (DynamicInterface, DynamicInterfaceForm, None),
        'vrf': (Vrf, VrfForm, None),
        'workgroup': (Workgroup, WorkgroupForm. None),
    }.get(record_type, (None, None))


def cydhcp_view(request, pk=None):
    return cy_view(request, get_klasses, 'cydhcp/cydhcp_view.html', pk)


def cydhcp_get_update_form(request):
    return get_update_form(request, get_klasses)


def cydhcp_search_obj(request):
    return search_obj(request, get_klasses)


def cydhcp_delete(request, pk):
    return cy_delete(request, pk, get_klasses)


def cydhcp_table_update(request, pk, record_type=None):
    return table_update(request, pk, get_klasses, record_type)


def cydhcp_create(request):
    record_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(record_type)
    if request.method == 'POST':
        form = FormKlass(request)
        if form.is_valid():
            obj = form.instance
            obj.save()
            return redirect(obj.get_list_url())
        else:
            return HttpResponse(json.dumps({'form': form}))
    return render(request, 'cydhcp/cydhcp_form.html', {'form': form})


def cydhcp_detail(request, pk):
    record_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(record_type)
    obj = get_object_or_404(Klass, pk=pk)
    attr_getter = getattr(obj, "{0}keyvalue_set".format(record_type))
    return render(request, "{0}/{0}_detail.html".format(record_type), {
        record_type: obj,
        'attrs': attr_getter.all()
    })


class CydhcpListView(BaseListView):
    template_name = 'cydhcp/cydhcp_list.html'


class CydhcpDetailView(BaseDetailView):
    template_name = 'cydhcp/cydhcp_detail.html'


class CydhcpCreateView(BaseCreateView):
    template_name = 'cydhcp/cydhcp_form.html'


class CydhcpUpdateView(BaseUpdateView):
    template_name = 'cydhcp/cydhcp_form.html'


class CydhcpDeleteView(BaseDeleteView):
    template_name = 'cydhcp/cydhcp_confirm_delete.html'
    succcess_url = '/cydhcp/'


def search_ip(request):
    if request.method == "POST":
        form = IpSearchForm(request.POST)
        try:
            if form.is_valid():
                ip_type = form.cleaned_data['ip_type']
                search_ip = form.cleaned_data['search_ip']
                try:
                    if ip_type == '4':
                        network = ipaddr.IPv4Network(search_ip)
                    if ip_type == '6':
                        network = ipaddr.IPv6Network(search_ip)
                except ipaddr.AddressValueError, e:
                    form._errors['__all__'] = ErrorList(
                        ["Bad IPv{0} Address {1}".format(ip_type, search_ip)])
                    return render(request, 'cydhcp/cydhcp_form.html', {
                        'form': form
                    })
                try:
                    network = Network.objects.get(network_str=search_ip)
                    search_ip = network
                    found_exact = True
                except ObjectDoesNotExist:
                    found_exact = False
                    network = Network(ip_type, network_str=search_ip,
                                      ip_type=ip_type)
                parent = calc_parent(network)
                eldars, sub_networks = calc_networks(network)
                if ip_type == '6':
                    sip_upper, sip_lower = ipv6_to_longs(network.network.ip)
                    eip_upper, eip_lower = ipv6_to_longs(
                        network.network.broadcast)
                else:
                    sip_upper, sip_lower = 0, int(network.network.ip)
                    eip_upper, eip_lower = 0, int(network.network.broadcast)

                addrs_count = AddressRecord.objects.filter(
                    ip_upper__gte=sip_upper,
                    ip_lower__gte=sip_lower,
                    ip_upper__lte=eip_upper,
                    ip_lower__lte=eip_lower).count()

                if addrs_count > 100:
                    addrs = None  # This is too much
                else:
                    addrs = AddressRecord.objects.filter(
                        ip_upper__gte=sip_upper,
                        ip_lower__gte=sip_lower,
                        ip_upper__lte=eip_upper,
                        ip_lower__lte=eip_lower)

                ptrs_count = PTR.objects.filter(
                    ip_upper__gte=sip_upper,
                    ip_lower__gte=sip_lower,
                    ip_upper__lte=eip_upper,
                    ip_lower__lte=eip_lower).count()

                if ptrs_count > 100:
                    ptrs = None  # This is too much
                else:
                    ptrs = PTR.objects.filter(
                        ip_upper__gte=sip_upper,
                        ip_lower__gte=sip_lower,
                        ip_upper__lte=eip_upper,
                        ip_lower__lte=eip_lower)

            return render(request, 'cydhcp/cydhcp_results.html', {
                'search_ip': search_ip,
                'found_exact': found_exact,
                'addrs': addrs,
                'addrs_count': addrs_count,
                'ptrs_count': ptrs_count,
                'ptrs': ptrs,
                'parent': parent,
                'eldars': eldars,
                'sub_networks': sub_networks,
            })
        except ValidationError, e:
            form._errors['__all__'] = ErrorList(e.messages)
            return render(request, 'cydhcp/cydhcp_form.html', {
                'form': form
            })
    else:
        form = IpSearchForm()
        return render(request, 'cydhcp/cydhcp_form.html', {
            'form': form
        })
