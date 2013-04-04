import json

from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

import ipaddr

from cyder.base.utils import make_paginator, tablefy
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.constants import *
from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.range.utils import ip_taken
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ptr.models import PTR


def delete_range_attr(request, attr_pk):
    """
    An view destined to be called by ajax to remove an attr.
    """
    attr = get_object_or_404(RangeKeyValue, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def range_detail(request, pk):
    mrange = get_object_or_404(Range, pk=pk)

    allow = None
    if mrange.allow == ALLOW_OPTION_VRF:
        try:
            allow = [Vrf.objects.get(network=mrange.network)]
        except ObjectDoesNotExist:
            allow = []
    elif mrange.allow == ALLOW_OPTION_KNOWN:
        allow = [ALLOW_OPTION_KNOWN]
    elif mrange.allow == ALLOW_OPTION_LEGACY:
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
    ips_total = ((end_upper << 64) + end_lower - 1 -
                 (start_upper << 64) + start_lower)
    ips_used = 0
    for i in xrange((start_upper << 64) + start_lower, (end_upper << 64) +
                   end_lower - 1):
        ip_str = str(ipaddr.IPv4Address(i))
        kwarg_data = json.dumps({'ip_str': ip_str, 'ip_type': mrange.ip_type})
        ptr_taken = ip_taken(i, ptrs)
        adr_taken = ip_taken(i, records)
        intr_taken = ip_taken(i, intrs)
        taken = any([ptr_taken, adr_taken, intr_taken])
        if ptr_taken and adr_taken:
            if ptr_taken.name == adr_taken.fqdn:
                range_data.append(
                    ('A/PTR', ip_str, ptr_taken, adr_taken, kwarg_data))
            else:
                range_data.append(('PTR', ip_str, ptr_taken, kwarg_data))
                range_data.append(('A', ip_str, adr_taken, kwarg_data))
        elif ptr_taken and not adr_taken:
            range_data.append(('PTR', ip_str, ptr_taken, kwarg_data))
        elif not ptr_taken and adr_taken:
            range_data.append(('A', ip_str, adr_taken, kwarg_data))
        if not taken:
            range_data.append((None, ip_str, kwarg_data))
        else:
            ips_used += 1

    return render(request, 'range/range_detail.html', {
        'obj': mrange,
        'obj_type': 'range',
        'ranges_table': tablefy((mrange,)),
        'range_data': make_paginator(request, range_data, 50),
        'attrs_table': tablefy(mrange.rangekeyvalue_set.all()),
        'allow_list': allow,
        'range_used': "{0}%".format(
            int(100 * float(ips_used) / ips_total) if ips_total else "N/A")
    })


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
