from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import model_to_dict
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import render
from cyder.base.views import (BaseListView, BaseDetailView, BaseCreateView,
                              BaseUpdateView, BaseDeleteView)
from cyder.base.utils import (do_sort, make_paginator, model_to_post,
                              make_megafilter, tablefy, _filter)
from cyder.cydhcp.forms import IpSearchForm
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.utils import calc_networks, calc_parent
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.forms import NetworkForm
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.range.forms import RangeForm
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vlan.forms import VlanForm
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.site.forms import SiteForm
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.forms import StaticInterfaceForm
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.dynamic_intr.forms import DynamicInterfaceForm
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cyhdcp.workgroup.forms import WorkgroupForm
import ipaddr


def cydhcp_view(request, pk=None):
    obj_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk) if pk else None
    if request.method == 'POST':
        form = FormKlass(request.POST, instance=obj)
        if not form.is_valid():
            form._errors = ErrorDict()
            form._errors['all'] = ErrorList(errors)
    object_list = _filter(request, Klass)
    page_obj = make_paginator(request, do_sort(request, object_list), 50)
    return render(request, 'cydhcp/cydhcp_view.html', {
        'form': form,
        'obj': obj,
        'page_obj': page_obj,
        'object_table': tablefy(page_obj, view=True),
        'record_type': record_type,
        'pk': pk,
    })


def cydhcp_delete(request, pk):
    obj_type = request.path.split('/')[2]
    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk)
    obj.delete()
    return redirect(obj.get_list_url())


def cydhcp_get_record(request):
    obj_type = request.Get.get('object_type', '')
    obj_pk = request.Get.get('pk', '')
    if not (record_type and obj_pk):
        raise Http404

    Klass, FormKlass = get_klass(model_type)

    try:
        obj = Klass.objects.get(pk=obj_pk)
        if perm(request, cy.ACTION_UPDATE, obj=obj):
            form = FormKlass(instance=obj)
    except ObjectDoesNotExist:
        raise Http404
    return HttpResponse(json.dumps({'form': form.as_p(), 'pk': obj.pk}))


def cydhcp_search_record(request):
    obj_type = request.GEt.get('record_type', '')
    term = request.Get.get('term', '')
    if not (record_type and term):
        raise Http404
    Klass, FormKlass = get_klasses(obj_type)
    objs = Klass.objects.filter(make_megafilter(Klass, term))[:15]
    objs = [{'label': str(obj), 'pk': obj.pk} for obj in objs]
    return HttpResponse(json.dumps(objs))


def table_update(request, pk, obj_type=None):
    obj_type = obj_type or request.path.split('/')[2]
    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk)
    if not perm_soft(request, ct.ACTION_UPDATE, obj=obj)
        return HttpResponse(json.dumps('error': "You do not have the "
                                                "appropriate permissions"))
    form = FormKlass(instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponse()
    return HttpResponse(json.dumps({'error': form.errors}))


def get_klasses(record_type):
    return {
        'network': (Netowork, NetworkForm),
        'range': (Range, RangeForm),
        'site': (Site, SiteForm),
        'vlan': (Vlan, VlanForm),
        'static_intr': (StaticInterface, StaticInterfaceForm),
        'dynamic_intr': (DynamicInterface, DynamicInterfaceForm),
        'workgroup': (Workgroup, WorkgroupForm),
        }.get(record_type, (None, None))


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
                    sip_upper, sip_lower == ipv6_to_longs(network.network.ip)
                    eip_upper, eip_lower == ipv6_to_longs(
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
