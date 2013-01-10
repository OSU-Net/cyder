from django.core.management.base import BaseCommand
from django.conf import settings
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup
import ipaddr
import MySQLdb


def calc_prefixlen(netmask):
    bits = 0
    while netmask:
        bits += netmask & 1
        netmask >>= 1
    return bits

connection = MySQLdb.connect(host=settings.MIGRATION_HOST,
                         user=settings.MIGRATION_USER,
                         passwd=settings.MIGRATION_PASSWD,
                         db=settings.MIGRATION_DB)

cursor = connection.cursor()


def create_subnet(id, name, subnet, netmask, status, vlan):
    """
    Takes a row from the Maintain subnet table
    returns a new network object and creates the vlan it is associated with
    """
    s, _ = Site.objects.get_or_create(name='Campus')
    v = None
    cursor.execute("SELECT * FROM vlan WHERE vlan_id = %s" % vlan)
    try:
        id, vlan_name, vlan_id = cursor.fetchone()
        v = Vlan.objects.get(name=vlan_name, number=vlan_id)
    except:
        print "vlan does not exist {0}".format(vlan)
    network = str(ipaddr.IPv4Address(subnet))
    prefixlen = str(calc_prefixlen(netmask))
    n = Network.objects.get_or_create(network_str=network + '/' + prefixlen,
            ip_type='4', site=s, vlan=v)
    return n


def create_range(id, start, end, type, subnet_id, comment, en, parent, allow):
    """
    Takes a row form the Maintain range table
    returns a range which is saved in cyder
    """
    cursor.execute("SELECT * FROM subnet WHERE id = {0}".format(subnet_id))
    try:
        id, name, subnet, netmask, status, vlan = cursor.fetchone()
    except:
        print ("Unable to find subnet with id {0}\n"
               "associated with range from {1} to {2}".format(
               subnet_id, ipaddr.IPv4Address(start), ipaddr.IPv4Address(end)))
        return
    r_type = 'st' if type == 'static' else 'dy'
    n = Network.objects.get(ip_lower=subnet,
            prefixlen=str(calc_prefixlen(netmask)))
    r = Range(start_lower=start, start_str=ipaddr.IPv4Address(start),
              end_lower=end, end_str=ipaddr.IPv4Address(end), network=n,
              range_type=r_type)
    try:
        r.save()
        return r
    except:
        print "cant create range {0} to {1} in {2}".format(
                ipaddr.IPv4Address(start), ipaddr.IPv4Address(end),
                n.network_str)
        return None


def create_zone(id, name, description, comment, purge, email, notify, blank):
    """
    Takes a row from the Maintain zone table
    returns a newly made container and creates the many to many relatiosnhip
    between the new ctnr and it's associated range
    """
    c = Ctnr.objects.get_or_create(name=name,
            description=comment or description)
    c.save()
    """
    We need to also create the workgroups and related them to containers
    """
    try:
        cursor.execute("SELECT zone_range.range "
                       "FROM zone_range "
                       "WHERE zone = {0}".format(id))
    except:
        print ("Unable to find any ranges associated with "
                        "{0} {1}".format(id, name))
        return
    for row in cursor.fetchall():
        cursor.execute("SELECT * FROM `ranges` WHERE id={0}".format(row[0]))
        _, start, end, _, _, _, _, _, _ = cursor.fetchone()
        r = Range.objects.get(start_lower=start, end_lower=end)
        c.ranges.add(r)


def migrate_subnets():
    created = []
    cursor.execute("SELECT * FROM subnet")
    result = cursor.fetchall()
    for row in result:
        created.append(create_subnet(*row))


def migrate_ranges():
    created = []
    cursor.execute("SELECT * FROM ranges")
    result = cursor.fetchall()
    for row in result:
        created.append(create_range(*row))


def migrate_vlans():
    cursor.execute("SELECT * FROM vlan")
    for row in cursor.fetchall():
        _, name, number = row
        Vlan.objects.get_or_create(name=name, number=number)


def migrate_workgroups():
    cursor.execute("SELECT * FROM workgroup")
    for row in cursor.fetchall():
        id, name = row
        vrf, _ = Workgroup.objects.get_or_create(name=name)


def create_ctnr(id):
    cursor.execute("SELECT * FROM zone WHERE id={0}".format(id))
    _, name, desc, comment, _, _, _, _ = cursor.fetchone()
    c, _ = Ctnr.objects.get_or_create(name=name, description=comment or desc)
    c.save()
    return c


def migrate_zones():
    cursor.execute("SELECT * FROM zone")
    result = cursor.fetchall()
    for _, name, desc, comment, _, _, _, _ in result:
        c, _ = Ctnr.objects.get_or_create(name=name,
                description=comment or desc)
        c.save()


def migrate_dynamic_hosts():
    cursor.execute("SELECT dynamic_range, name, domain, ha, location, "
                   "workgroup, zone * FROM hosts WHERE ip = 0")
    results = cursor.fetchall()
    for range_id, name, domain_id, mac, loc, workgroup_id, zone_id in results:
        s, _ = System.objects.get_or_create(hostname=name, location=loc)
        r = maintain_find_range(range_id)
        c = maintain_find_zone(zone_id)
        d = maintain_find_domain(domain_id)
        w = maintain_find_workgroup(workgroup_id)
        v = Vrf.objects.get(name=w.name)
        intr, _ = DynamicInterface.objects.get_or_create(range=r, workgroup=w,
                ctnr=c, domain=d, vrf=v)


def migrate_zone_range():
    cursor.execute("SELECT * FROM zone_range WHERE enabled=1")
    result = cursor.fetchall()
    for _, zone_id, range_id, _, comment, _ in result:
        cursor.execute("SELECT name FROM zone WHERE id={0}".format(zone_id))
        try:
            zone_name = cursor.fetchone()
            if not zone_name:
                continue
        except:
            print "zone with id {0} does not exist".format(zone_id[0])
            continue
        cursor.execute("SELECT start, end "
                       "FROM `ranges` "
                       "WHERE id={0}".format(range_id))
        try:
            r_start, r_end = cursor.fetchone()
        except:
            print "range with id {0} does not exist".format(range_id)
            continue
        try:
            c = Ctnr.objects.get(name=zone_name[0])
        except:
            print "can't find container named {0}".format(zone_name[0])
            continue
        try:
            r = Range.objects.get(start_lower=r_start, end_lower=r_end)
        except:
            print ("can't find range with "
                   "start_lower = {0} and end_lower = {1}". format(
                       r_start, r_end))
            continue
        c.ranges.add(r)


def migrate_zone_workgroup():
    cursor.execute("SELECT * FROM zone_workgroup")
    result = cursor.fetchall()
    for _, workgroup_id, zone_id, _ in result:
        cursor.execute("SELECT name FROM zone WHERE id={0}".format(zone_id))
        try:
            zone_name = cursor.fetchone()
            if not zone_name:
                continue
        except:
            print "zone with id {0} does not exist".format(zone_id)
            continue
        cursor.execute("SELECT * FROM workgroup WHERE id={0}".format(zone_id))
        try:
            _, w_name = cursor.fetchone()
        except:
            print "workgroup with id {0} does not exist".format(zone_id)
            continue
        try:
            c = Ctnr.objects.get(name=zone_name[0])
        except:
            print "can't find container named {0}".format(zone_name[0])
            continue
        try:
            w = Workgroup.objects.get(name=w_name)
        except:
            print "can't find workgroup named {0}". format(w_name)
            continue
        c.workgroups.add(w)


def maintain_find_range(range_id):
    cursor.exeute("SELECT start, end "
                  "FROM `ranges` "
                  "WHERE id = {0}".format(range_id))
    try:
        start, end = cursor.fetchone()
        return Range.objects.get(start=start, end=end)
    except:
        print "Can't find range with an id of {0}".format(range_id)
        return None


def maintain_find_domain(domain_id):
    cursor.execute("SELECT name "
                   "FROM `domain` "
                   "WHERE id = {0}".format(domain_id))
    try:
        name = cursor.fetchone()[0]
        return Domain.objects.get(name=name)
    except:
        print "Can't find domain with an id of {0}".format(domain_id)
        return None


def maintain_find_zone(zone_id):
    cursor.execute("SELECT name FROM zone where id = {0}".format(zone_id))
    try:
        name = cursor.fetchone()[0]
        return Ctnr.objects.get(name=name)
    except:
        print "Can't find zone with id of {0}".format(zone_id)
        return None


def maintain_find_workgroup(workgroup_id):
    cursor.execute("SELECT name "
                   "FROM workgroup "
                   "WHERE id = {0}".format(workgroup_id))
    try:
        name = cursor.fetchone()[0]
        return Workgroup.objects.get(name=name)
    except:
        print "Can't find workgroup with id {0}".format(workgroup_id)
        return None


class Command(BaseCommand):

    def handle(self, *args, **options):
        migrate_vlans()
        migrate_workgroups()
        migrate_subnets()
        migrate_ranges()
        migrate_zones()
        migrate_zone_range()
        migrate_zone_workgroup()
