import MySQLdb
from django.conf import settings


def get_cursor(name):
    connection = MySQLdb.connect(host=settings.MIGRATION_HOST,
                                 user=settings.MIGRATION_USER,
                                 passwd=settings.MIGRATION_PASSWD,
                                 db=settings.MIGRATION_DB)
    cursor = connection.cursor()
    return cursor


def long2ip(ip):
    return ".".join(map(lambda x: str((ip >> x) & 255), range(24, -1, -8)))


def ip2long(ip):
    return reduce(lambda num, octet: (num << 8) | int(octet), ip.split('.'), 0)


def clean_mac(mac):
    return mac.lower().replace(':', '')


def calc_prefixlen(netmask):
    bits = 0
    while netmask:
        bits += netmask & 1
        netmask >>= 1
    return bits


ATTR_CONVERSIONS = {
    'slp-scope': 'slp-service-scope'
}


def fix_attr_name(attr_name):
    if attr_name in ATTR_CONVERSIONS:
        return ATTR_CONVERSIONS[attr_name]
    else:
        return attr_name
