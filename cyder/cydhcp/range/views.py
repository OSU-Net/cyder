import json

from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

import ipaddr

from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.range.forms import RangeForm
from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.views import (CydhcpDeleteView, CydhcpDetailView,
                                CydhcpCreateView, CydhcpUpdateView,
                                CydhcpListView)
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR


class RangeView(object):
    model = Range
    form_class = RangeForm
    queryset = Range.objects.all()


class RangeDeleteView(RangeView, CydhcpDeleteView):
    success_url = "/cydhcp/range/"


class RangeDetailView(RangeView, CydhcpDetailView):
    template_name = 'range/range_detail.html'


def delete_range_attr(request, attr_pk):
    """
    An view destined to be called by ajax to remove an attr.
    """
    attr = get_object_or_404(RangeKeyValue, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def range_detail(request, range_pk):
    mrange = get_object_or_404(Range, pk=range_pk)
    attrs = mrange.rangekeyvalue_set.all()

    allow = None
    if mrange.allow == "vrf":
        try:
            allow = [Vrf.objects.get(network=mrange.network)]
        except ObjectDoesNotExist:
            allow = []
    elif mrange.allow == "known-client":
        allow = ["Known client"]
    elif mrange.allow == "legacy":
        allow = [ctnr for ctnr in Ctnr.objects.filter(ranges=mrange)]
    start_upper, start_lower = mrange.start_upper, mrange.start_lower
    end_upper, end_lower = mrange.end_upper, mrange.end_lower

    gt_start = Q(ip_upper=start_upper, ip_lower__gte=start_lower)
    gt_start = gt_start | Q(ip_upper__gte=start_upper)

    lt_end = Q(ip_upper=end_upper, ip_lower__lte=end_lower)
    lt_end = lt_end | Q(ip_upper__lte=end_upper)

    records = AddressRecord.objects.filter(gt_start, lt_end)
    ptrs = PTR.objects.filter(gt_start, lt_end)
    intrs = StaticInterface.objects.filter(gt_start, lt_end)

    range_data = []
    ips_total = ((end_upper << 64) + end_lower - 1) - \
                ((start_upper << 64) + start_lower)
    ips_used = 0
    for i in range((start_upper << 64) + start_lower, (end_upper << 64) +
                   end_lower - 1):
        taken = False
        adr_taken = None
        ip_str = str(ipaddr.IPv4Address(i))
        for record in records:
            if record.ip_lower == i:
                adr_taken = record
                break

        ptr_taken = None
        for ptr in ptrs:
            if ptr.ip_lower == i:
                ptr_taken = ptr
                break

        if ptr_taken and adr_taken:
            if ptr_taken.name == adr_taken.fqdn:
                range_data.append(('A/PTR', ip_str, ptr_taken, adr_taken))
            else:
                range_data.append(('PTR', ip_str, ptr_taken))
                range_data.append(('A', ip_str, adr_taken))
            taken = True
        elif ptr_taken and not adr_taken:
            range_data.append(('PTR', ip_str, ptr_taken))
            taken = True
        elif not ptr_taken and adr_taken:
            range_data.append(('A', ip_str, adr_taken))
            taken = True

        for intr in intrs:
            if intr.ip_lower == i:
                range_data.append(('Interface', ip_str, intr))
                taken = True
                break

        if not taken:
            range_data.append((None, ip_str))
        else:
            ips_used += 1
    paginator = Paginator(range_data, 20)
    page = request.GET.get('page')
    try:
        range_data = paginator.page(page)
    except PageNotAnInteger:
        range_data = paginator.page(1)
    except EmptyPage:
        range_data = paginator.page(paginator.num_pages)
    return render(request, 'range/range_detail.html', {
        'range_': mrange,
        'allow_list': allow,
        'attrs': attrs,
        'range_data': range_data,
        'range_used': "{0}%".format(
            int(100*float(ips_used)/ips_total) if ips_total else "N/A")
    })


class RangeCreateView(RangeView, CydhcpCreateView):
    """"""


def redirect_to_range_from_ip(request):
    ip_str = request.GET.get('ip_str')
    ip_type = request.GET.get('ip_type')
    if not (ip_str and ip_type):
        return HttpResponse(json.dumps({'failure': "Slob"}))

    if ip_type == '4':
        try:
            ip_upper, ip_lower = 0, int(ipaddr.IPv4Address(ip_str))
        except ipaddr.AddressValueError:
            return HttpResponse(json.dumps(
                {'success': False,
                 'message': "Failure to recognize {0} as an IPv4 "
                            "Address.".format(ip_str)}))
    else:
        try:
            ip_upper, ip_lower = ipv6_to_longs(ip_str)
        except ValidationError:
            return HttpResponse(json.dumps({'success': False,
                                            'message': 'Invalid IP'}))

    range_ = Range.objects.filter(
        start_upper__lte=ip_upper, start_lower__lte=ip_lower,
        end_upper__gte=ip_upper, end_lower__gte=ip_lower)
    if not len(range_) == 1:
        return HttpResponse(json.dumps({'failure': "Failture to find range"}))
    else:
        return HttpResponse(json.dumps(
            {'success': True,
             'redirect_url': range_[0].get_detail_url()}))


class RangeUpdateView(RangeView, CydhcpUpdateView):
    """"""


class RangeListView(RangeView, CydhcpListView):
    """"""
