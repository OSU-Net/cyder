from django.core.exceptions import ValidationError
import re


mac_match = "^[0-9a-f]{12}$"
is_mac = re.compile(mac_match)

MAC_ERR = "MAC address not of valid type."
EMPTY_MAC_ERR = ('If you want to use a blank MAC address, uncheck "DHCP '
                 'enabled"')

def validate_mac(mac):
    if not isinstance(mac, basestring) or not is_mac.match(mac):
        raise ValidationError(MAC_ERR)
    if mac == '000000000000':
        raise ValidationError(EMPTY_MAC_ERR)
