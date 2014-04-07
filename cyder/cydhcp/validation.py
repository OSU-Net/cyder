# encoding: utf-8
from django.core.exceptions import ValidationError
import re


mac_pattern = re.compile(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$')

def validate_mac(mac):
    if mac == '00:00:00:00:00:00':
        raise ValidationError('Invalid MAC address—to disable DHCP for this '
                              'interface, uncheck "Enable DHCP"')
    elif not mac_pattern.match(mac):
        raise ValidationError('Invalid MAC address')
