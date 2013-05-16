from itertools import chain, groupby

import json
from cyder.base.constants import IP_TYPE_4, IP_TYPE_6

from cyder.cydhcp.utils import start_end_filter, two_to_one
from cyder.cydhcp.interface.static_intr.models import StaticInterface

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR


def contiguous_ips(ip_list, ip_type=IP_TYPE_4):
    """
    Given a sorted set of ips of the same type group them into a list of
    the contiguous sublists
    """
    grouped_ips = []
    contiguous_list = []
    """
    We need to group together objects which have the same ip addres.
    They willb e stored in a tuple with the first element being an
    ipaddr object and the second element is a list of records which
    have that ip address.
    """
    for ip, grp in groupby(ip_list, key=lambda rec: rec.get_wrapped_ip()):
        grouped_ips.append((ip, list(grp)))
    if not grouped_ips:
        return [], 0
    ips_used = len(grouped_ips)
    current_list = [grouped_ips[0]]
    for ip_grp in grouped_ips[1:]:
        """
        If the next record is the successor of the last contiguous record
        add it to the current list of contiguous records else add that
        contiguous list to the list of contigguous ranges and start a new one.
        """
        if current_list[-1][0] == ip_grp[0] + 1:
            current_list.append(ip_grp)
        else:
            contiguous_list.append(current_list)
            current_list = [ip_grp]
    contiguous_list.append(current_list)
    return contiguous_list, ips_used


def range_usage(start, end, ip_type):
    """
    Takes a start and end address as integers and returns a range usage list
    containing tuples of the available ips and lists of contiguously used ip
    addresses.
    """
    ip_start, ip_end, ipf_q = start_end_filter(start, end, ip_type)
    record_ip = lambda x: two_to_one(x.ip_upper, x.ip_lower)
    taken_ips = sorted(chain(AddressRecord.objects.filter(ipf_q),
                             PTR.objects.filter(ipf_q),
                             StaticInterface.objects.filter(ipf_q)),
                             key=record_ip)
    contiguous_ip_list, total_used = contiguous_ips(taken_ips)
    total_ips = end - start
    range_usage_list = []
    free_range_start = ip_start
    for filled_range in contiguous_ip_list:
        # if the first address in the current contiguous range is greater
        # than the first free address add that free range of ips to the range
        # usage list
        if free_range_start < filled_range[0][0]:
            range_usage_list.append(
                ("Free",
                 free_range_start, filled_range[0][0] - 1,
                 json.dumps({"ip_str": str(free_range_start),
                             "ip_type": ip_type})))
        # the new free range may start with the next address after the end of
        # the current filled range
        free_range_start = filled_range[-1][0] + 1
        range_usage_list.append(filled_range)
    # handle the case where there is an additional free range after the final
    # filled range
    if free_range_start < ip_end:
        range_usage_list.append(
                ("Free",
                 free_range_start, ip_end,
                 json.dumps({"ip_str": str(free_range_start),
                             "ip_type": ip_type})))

    return range_usage_list, int((float(total_used) / total_ips) * 100)
