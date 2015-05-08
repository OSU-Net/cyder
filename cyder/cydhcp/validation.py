# encoding: utf-8
from django.core.exceptions import ValidationError
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


def validate_system_static_ctnr(system, static):
    if system.ctnr not in static.domain.ctnr_set.all():
        raise ValidationError("System's container must match static "
                              "interface's domain's containers.")


def validate_system_dynamic_ctnr(system, dynamic):
    if system.ctnr not in dynamic.range.domain.ctnr_set.all():
        raise ValidationError("System's container must match dynamic "
                              "interface's range's domain's containers.")
