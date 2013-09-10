from cyder.cydhcp.utils import start_end_filter, two_to_one, one_to_two
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR
from cyder.base.utils import qd_to_py_dict

from django.db.models.loading import get_model
from django.http import HttpResponse

import json


def pretty_ranges(ranges):
    return [(rng.start_str + " - " + rng.end_str) for rng in ranges]


def ip_taken(ip, records):
    """
    Given an ip as an integer and a queryset find an object in the queryset
    with the same ip as the integer.  This is inteded for ptrs and arecords and
    interfaces.
    """
    ip_low, ip_high = one_to_two(ip)
    for record in records:
        if record.ip_lower is ip_low and record.ip_upper is ip_high:
            return record
    return None


def range_usage(ip_start, ip_end, ip_type, get_objects=True):
    """Returns ip usage statistics about the range starting at ip_start and
    ending at ip_end.

    Given an inclusive contiguous range of positive integers (IP addresses)
    between `a` and `b` and a list of lists where each sublist contains
    integers (IP addresses) that are within the range, how many integers
    between `a` and `b` do not exist in any of the lists; this is what this
    function calculates.

    For example:

    ```
        Start = 0
        End = 9
        Lists = [[1,2,3], [2,3,4]]
    ```

    The integers that do not occur in `Lists` are `0`, `5`, `6`, `7`, `8`, and
    `9`, so there are 6 integers that do not exist in Lists that satisfy `Start
    <= n <= End`.

    Start can be small and End can be very large (the range may be
    larger than you would want to itterate over). Due to the size of IPv6
    ranges, we should not use recursion.

    There are three types of objects (that we care about) that have IP's
    associated with them: AddressRecord, PTR, StaticInterface. Because we get
    objects back as Queryset's that are hard to merge, we have to do this
    algorithm while retaining all three lists. The gist of the algoritm is as
    follows::

        # Assume the lists are sorted
        while lists:
            note the start number (ip)
            lowest =: of the things in list (PTR, A, INTR), find the lowest
            difference =: start - lowest.ip
            total_free +=: difference
            start =: lowest.ip + 1

            if any PTR, A, or INTR has the same IP as lowest:
                remove those items from their lists

    """
    istart, iend, ipf_q = start_end_filter(ip_start, ip_end, ip_type)

    def get_ip(rec):
        return two_to_one(rec.ip_upper, rec.ip_lower)

    lists = [sorted(AddressRecord.objects.filter(ipf_q), key=get_ip),
             sorted(PTR.objects.filter(ipf_q), key=get_ip),
             sorted(StaticInterface.objects.filter(ipf_q), key=get_ip)]

    free_ranges = []

    def cmp_ip_upper_lower(a, b):
        if a.ip_upper > b.ip_upper:
            return a
        elif a.ip_upper < b.ip_upper:
            return b
        elif a.ip_lower > b.ip_lower:
            return a
        elif a.ip_lower < b.ip_lower:
            return b
        else:
            return a  # redundant, maybe?

    unused = 0
    minimum_i = 0
    rel_start = int(istart)
    end = int(iend)

    # This is translated directly from a recursive implementation.
    while True:
        if rel_start > end:
            break
        lists = [l for l in lists if l]
        if not lists:
            free_ranges.append((rel_start, end))
            unused += end - rel_start + 1
            break

        min_list = min(lists, key=lambda x: two_to_one(x[0].ip_upper,
                       x[0].ip_lower))

        minimum = min_list[0]
        minimum_i = two_to_one(minimum.ip_upper, minimum.ip_lower)
        unused += minimum_i - rel_start
        if minimum_i != rel_start:
            free_ranges.append((rel_start, minimum_i - 1))

        for l in lists:
            while (l and l[0].ip_upper == minimum.ip_upper and
                   l[0].ip_lower == minimum.ip_lower):
                l.pop(0)

        rel_start = minimum_i + 1

    return {
        'unused': unused,
        'used': int(iend) - int(istart) - unused + 1,
        'free_ranges': free_ranges,
    }


def range_wizard(request):
    from cyder.cydhcp.network.utils import get_ranges
    vrf_networks = set()
    site_networks = set()
    Range = get_model('range', 'range')
    if request.POST:
        data = qd_to_py_dict(request.POST)
        if data['range']:
            rng = Range.objects.get(id=data['range'])

            if data['free_ip'] and rng and rng.ip_type == '4':
                ip_str = rng.get_next_ip()
                if ip_str is None:
                    ip_str = 'This range is full!'

                if isinstance(ip_str, HttpResponse):
                    ip_str = 'This range is too small'

            else:
                ip_str = '.'.join(rng.start_str.split('.')[:-1])

            return HttpResponse(json.dumps({
                'ip_type': rng.ip_type,
                'ip_str': str(ip_str), }))

        if data['vrf']:
            Vrf = get_model('vrf', 'vrf')
            vrf = Vrf.objects.get(id=data['vrf'])
            vrf_networks = vrf.get_related_networks([vrf])

        if data['site']:
            Site = get_model('site', 'site')
            site = Site.objects.get(id=data['site'])
            # Right now campus will return a result of all networks
            if site.name != 'Campus':
                site_networks = site.get_related_networks([site])

        if len(vrf_networks) > 0 and len(site_networks) > 0:
            networks = vrf_networks.intersection(site_networks)
        else:
            networks = vrf_networks.union(site_networks)

        if not data['site'] and not data['vrf']:
            if request.session['ctnr'].name == 'global':
                ranges = Range.objects.all()
            else:
                ranges = Range.objects.filter(
                    ctnr__id=request.session['ctnr'].id)
        else:
            ranges = get_ranges(networks, ctnr=request.session['ctnr'])

        ranges = [(pretty_ranges(ranges)), ([r.id for r in ranges])]
        return HttpResponse(json.dumps({'ranges': ranges}))

    else:
        return None
