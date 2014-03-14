from django.core.exceptions import ValidationError
import re


mac_pattern = re.compile(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$')

def validate_mac(mac):
    if not isinstance(mac, basestring) or not mac_pattern.match(mac) \
            or mac == '00:00:00:00:00:00':
        raise ValidationError('Invalid MAC address')
