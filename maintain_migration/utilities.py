from ConfigParser import ConfigParser
import MySQLdb


CONFIG_FILE = "database.cfg"
config = ConfigParser()
config.read(CONFIG_FILE)


def get_cursor(name):
    connection = MySQLdb.connect(host=config.get(name, 'host'),
                                 user=config.get(name, 'user'),
                                 passwd=config.get(name, 'passwd'),
                                 db=config.get(name, 'db'))

    cursor = connection.cursor()
    return cursor


def long2ip(ip):
    return ".".join(map(lambda x: str((ip >> x) & 255), range(24, -1, -8)))


def ip2long(ip):
    return reduce(lambda num, octet: (num << 8) | int(octet), ip.split('.'), 0)


def clean_mac(mac):
    return ":".join([mac[x: x + 2] for x in range(0, 11, 2)])


def calc_prefixlen(netmask):
    bits = 0
    while netmask:
        bits += netmask & 1
        netmask >>= 1
    return bits
