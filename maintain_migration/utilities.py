from ConfigParser import ConfigParser
import MySQLdb


CONFIG_FILE = "database.cfg"
config = ConfigParser()
config.read(CONFIG_FILE)


def get_cursor(name):
    connection = MySQLdb.connect(host = config.get(name, 'host'),
                                 user = config.get(name, 'user'),
                                 passwd = config.get(name, 'passwd'),
                                 db = config.get(name, 'db'))

    cursor = connection.cursor()
    return cursor


def long2ip(ip):
    return ".".join(map(lambda x: str((ip >> x) & 255), range(24,-1,-8)))


def ip2long(ip):
    return reduce(lambda num, octet: (num << 8) | int(octet), ip.split('.'), 0)


def clean_mac(mac):
    return ":".join([mac[x:x+2] for x in range(0,11,2)])


def calc_prefixlen(netmask):
    bits = 0
    while netmask:
        bits += netmask & 1
        netmask >>= 1
    return bits

class Maintain2Cyder:
    def __init__(self, cursor_name):
        self.cursor = get_cursor("maintain_sb")

    def maintain_range_find(range_id):
        self.cursor.exeute("SELECT start, end FROM `ranges` WHERE id =
                {0}".format(range_id))
        try:
            start, end = cursor.fetchone()
            return Range.objects.get(start=start, end=end)
        except:
            print "Can't find range with an id "
                  "of {0}".format(range_id)
            return None


    def maintain_domain_find(domain_id):
        self.cursor.execute("SELECT name "
                \   "FROM `domain` "
                       "WHERE id = {0}".format(domain_id))
        try:
            name = cursor.fetchone()[0]
            return Domain.objects.get(name=name)
        except:
            print "Can't find domain with an id of{0}".format(domain_id)
            return None


    def maintain_zone_find(zone_id):
        self.cursor.execute("SELECT name "
                       "FROM zone "
                       "WHERE id = {0}".format(zone_id))
        try:
            name = cursor.fetchone()[0]
            return Ctnr.objects.get(name=name)
        except:
            print "Can't find zone with id of {0}".format(zone_id)
            return None


    def maintain_workgroup_find(workgroup_id):
            self.cursor.execute("SELECT name "
                           "FROM workgroup "
                           "WHERE id = {0}".format(workgroup_id))
        try:
            name = cursor.fetchone()[0]
            return Workgroup.objects.get(name=name)
        except:
            print "Can't find workgroup with id {0}".format(workgroup_id)
            return None


