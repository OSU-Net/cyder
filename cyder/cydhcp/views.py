from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.util import ErrorList
from django.shortcuts import render, get_object_or_404

from cyder.base.views import (BaseCreateView, BaseDeleteView,
                              BaseDetailView, BaseListView, BaseUpdateView,
                              cy_view, cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.cydhcp.forms import IpSearchForm
from cyder.cydhcp.network.utils import calc_networks, calc_parent
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)
from cyder.cydhcp.interface.dynamic_intr.forms import (DynamicInterfaceForm,
                                                       DynamicIntrKeyValueForm)
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticIntrKeyValue)
from cyder.cydhcp.interface.static_intr.forms import (StaticInterfaceForm,
                                                      StaticIntrKeyValueForm)
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.network.forms import NetworkForm, NetworkKeyValueForm
from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.range.forms import RangeForm, RangeKeyValueForm
from cyder.cydhcp.site.models import Site, SiteKeyValue
from cyder.cydhcp.site.forms import SiteForm, SiteKeyValueForm
from cyder.cydhcp.vlan.models import Vlan, VlanKeyValue
from cyder.cydhcp.vlan.forms import VlanForm, VlanKeyValueForm
from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue
from cyder.cydhcp.vrf.forms import VrfForm, VrfKeyValueForm
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue
from cyder.cydhcp.workgroup.forms import WorkgroupForm, WorkgroupKeyValueForm

import ipaddr


def get_klasses(obj_type):
    return {
        'network': (Network, NetworkForm, None),
        'network_key_value': (NetworkKeyValue, NetworkKeyValueForm, None),
        'range': (Range, RangeForm, None),
        'range_key_value': (RangeKeyValue, RangeKeyValueForm, None),
        'site': (Site, SiteForm, None),
        'site_key_value': (SiteKeyValue, SiteKeyValueForm, None),
        'vlan': (Vlan, VlanForm, None),
        'vlan_key_value': (VlanKeyValue, VlanKeyValueForm, None),
        'static_interface':
            (StaticInterface, StaticInterfaceForm, None),
        'static_interface_key_value':
            (StaticIntrKeyValue, StaticIntrKeyValueForm, None),
        'dynamic_interface':
            (DynamicInterface, DynamicInterfaceForm, None),
        'dynamic_interface_key_value':
            (DynamicIntrKeyValue, DynamicIntrKeyValueForm, None),
        'vrf': (Vrf, VrfForm, None),
        'vrf_key_value': (VrfKeyValue, VrfKeyValueForm, None),
        'workgroup': (Workgroup, WorkgroupForm, None),
        'workgroup_key_value':
            (WorkgroupKeyValue, WorkgroupKeyValueForm, None),
    }.get(obj_type, (None, None, None))


def cydhcp_view(request, pk=None):
    return cy_view(request, get_klasses, 'cydhcp/cydhcp_view.html', pk)


def cydhcp_create(request, pk=None):
    return cy_view(request, get_klasses, 'cydhcp/cydhcp_form.html', pk)


def cydhcp_get_update_form(request):
    return get_update_form(request, get_klasses)


def cydhcp_search_obj(request):
    return search_obj(request, get_klasses)


def cydhcp_delete(request, pk):
    return cy_delete(request, pk, get_klasses)


def cydhcp_table_update(request, pk, obj_type=None):
    return table_update(request, pk, get_klasses, obj_type)


def cydhcp_detail(request, pk):
    obj_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk)
    attr_getter = getattr(obj, "{0}keyvalue_set".format(obj_type))
    return render(request, "{0}/{0}_detail.html".format(obj_type), {
        obj_type: obj,
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
