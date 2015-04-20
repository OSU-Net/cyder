import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.db.models.loading import get_model

import ipaddr

from cyder.base.helpers import do_sort
from cyder.base.utils import make_paginator, tablefy, make_megafilter
from cyder.base.views import cy_render
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.constants import (ALLOW_ANY, ALLOW_KNOWN, ALLOW_VRF,
                                    ALLOW_LEGACY)
from cyder.cydhcp.range.models import Range, RangeAV
from cyder.cydhcp.range.range_usage import range_usage
from cyder.cydhcp.utils import two_to_one
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.ip.models import ipv6_to_longs


def range_detail(request, pk):
    mrange = get_object_or_404(Range, pk=pk)

    if mrange.allow == ALLOW_ANY:
        allow = ['Any client']
    elif mrange.allow == ALLOW_KNOWN:
        allow = ['Known clients']
    else:
        allow = []
        if mrange.allow == ALLOW_VRF:
            allow += map(str, Vrf.objects.filter(network=mrange.network))
        if mrange.allow == ALLOW_LEGACY:
            allow += map(str, Ctnr.objects.filter(ranges=mrange))

    allow.sort(key=lambda x: x.lower())

    range_type = mrange.range_type
    range_data = []
    ip_usage_percent = None
    dynamic_interfaces = []
    dynamic_interfaces_page_obj = None
    dynamic_interfaces_table = None
    if range_type == 'st':
        start_upper = mrange.start_upper
        start_lower = mrange.start_lower
        end_upper = mrange.end_upper
        end_lower = mrange.end_lower
        range_data, ip_usage_percent = range_usage(
            two_to_one(start_upper, start_lower),
            two_to_one(end_upper, end_lower),
            mrange.ip_type)
    else:
        ip_usage_percent = mrange.range_usage
        DynamicInterface = get_model('cyder', 'dynamicinterface')
        dynamic_interfaces = DynamicInterface.objects.filter(range=mrange)
        dynamic_interfaces_page_obj = make_paginator(
            request, do_sort(request, dynamic_interfaces), 10)
        dynamic_interfaces_table = tablefy(dynamic_interfaces_page_obj,
                                           request=request, excluded=['Range'])

    range_table = tablefy((mrange,), request=request, detail_view=True)

    ctnr_table = tablefy(mrange.ctnr_set.all(), request=request)

    if ip_usage_percent:
        ip_usage_percent = "{0}%".format(ip_usage_percent)
    return cy_render(request, 'range/range_detail.html', {
        'obj': mrange,
        'obj_type': 'range',
        'pretty_obj_type': mrange.pretty_type,
        'ranges_table': range_table,
        'range_data': make_paginator(request, range_data, 50),
        'range_type': range_type,
        'attrs_table': tablefy(mrange.rangeav_set.all(),
                               request=request),
        'allow_list': allow,
        'range_used': ip_usage_percent,
        'dynamic_intr_table': dynamic_interfaces_table,
        'page_obj': dynamic_interfaces_page_obj,
        'ctnr_table': ctnr_table
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


def search(request):
    """Returns a list of ranges matching 'term'."""
    term = request.GET.get('term', '')
    if not term:
        raise Http404

    ranges = Range.objects.filter(make_megafilter(Range, term))[:15]
    ranges = [{'label': str(rng), 'pk': rng.id} for rng in ranges]
    return HttpResponse(json.dumps(ranges))
