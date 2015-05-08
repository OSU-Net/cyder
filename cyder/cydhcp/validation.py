# encoding: utf-8
from django.core.exceptions import ValidationError
from django.db.models import Q
import re


ERROR_TOO_LONG = 'MAC address is too long'

mac_pattern = re.compile(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$')


def validate_mac(mac):
    if mac == ERROR_TOO_LONG:
        raise ValidationError(ERROR_TOO_LONG)
    elif mac == '00:00:00:00:00:00':
        raise ValidationError('Invalid MAC address—to disable DHCP for this '
                              'interface, uncheck "Enable DHCP"')
    elif not mac_pattern.match(mac):
        raise ValidationError('Invalid MAC address')


def get_partial_overlap(n, netmodel=None):
    from cyder.cydhcp.network.models import Network
    if netmodel is None:
        netmodel = Network
    A = Q(start_upper=n.start_upper, end_upper=n.end_upper)
    A = A & (Q(end_lower__gte=n.start_lower, end_lower__lte=n.end_lower) |
             Q(start_lower__gte=n.start_lower, start_lower__lte=n.end_lower) |
             Q(start_lower__lte=n.start_lower, end_lower__gte=n.end_lower))
    B = Q(end_upper=n.end_upper) & ~Q(start_upper=n.start_upper)
    C = Q(start_upper=n.start_upper) & ~Q(end_upper=n.end_upper)
    D = Q(start_upper__lt=n.start_upper, end_upper__gt=n.end_upper)
    networks = netmodel.objects.filter(A | B | C | D)
    if n.pk is not None and isinstance(n, netmodel):
        networks = networks.exclude(pk=n.pk)
    return networks


def get_total_overlap(n, netmodel=None):
    from cyder.cydhcp.network.models import Network
    if netmodel is None:
        netmodel = Network
    A = Q(start_upper=n.start_upper, end_upper=n.end_upper)
    A = A & (Q(end_lower__gte=n.start_lower, end_lower__lte=n.end_lower) &
             Q(start_lower__gte=n.start_lower, start_lower__lte=n.end_lower))
    B = Q(start_upper__gt=n.start_upper, end_upper=n.end_upper)
    B = B & Q(end_lower__lte=n.end_lower)
    C = Q(start_upper=n.start_upper, end_upper__lt=n.end_upper)
    C = C & Q(start_lower__gte=n.start_lower)
    D = Q(start_upper__gt=n.start_upper, end_upper__lt=n.end_upper)
    networks = netmodel.objects.filter(A | B | C | D)
    if n.pk is not None and isinstance(n, netmodel):
        networks = networks.exclude(pk=n.pk)
    return networks


def validate_network_overlap(n1):
    from cyder.cydhcp.supernet.models import Supernet
    is_supernet = isinstance(n1, Supernet)
    if not is_supernet:
        partial_overlap = get_partial_overlap(n1)
        if partial_overlap.exists():
            raise ValidationError("%s overlaps another network." % n1)
        total_overlap = get_total_overlap(n1, Supernet)
        if total_overlap.exists():
            if (total_overlap.count() == 1 and
                    total_overlap.all()[0].network_str == n1.network_str):
                pass
            else:
                raise ValidationError("%s fully overlaps a supernet." % n1)
        partial_overlap = get_partial_overlap(n1, Supernet)
        if partial_overlap.count() >= 2:
            raise ValidationError(
                "%s crosses two supernets." % n1)
        elif partial_overlap.count() == 1:
            s1 = partial_overlap.all()[0]
            if not s1.contains(n1):
                raise ValidationError(
                    "%s is partially overlapped by a supernet." % n1)

    if is_supernet:
        partial_overlap = get_partial_overlap(n1, Supernet)
        if partial_overlap.exists():
            raise ValidationError("%s overlaps another supernet." % n1)
        partial_overlap = get_partial_overlap(n1)
        total_overlap = get_total_overlap(n1)
        if partial_overlap.count() - total_overlap.count() != 0:
            raise ValidationError("%s partially overlaps a network." % n1)


def validate_system_static_ctnr(system, static):
    if system.ctnr not in static.domain.ctnr_set.all():
        raise ValidationError("System's container must match static "
                              "interface's domain's containers.")


def validate_system_dynamic_ctnr(system, dynamic):
    if system.ctnr not in dynamic.range.domain.ctnr_set.all():
        raise ValidationError("System's container must match dynamic "
                              "interface's range's domain's containers.")
