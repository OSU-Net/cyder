from django.core.management.base import BaseCommand
from django.conf import settings
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue
import ipaddr
import MySQLdb
from optparse import make_option


allow_all_subnets = ['10.192.76.2', '10.192.103.150', '10.192.15.2',
'10.197.32.0', '10.192.148.32', '10.192.144.32', '10.192.140.32',
'10.196.0.32', '10.196.4.32', '10.192.136.63', '10.196.8.8', '10.196.16.8',
'10.196.24.8', '10.196.32.8', '10.196.40.8', '10.162.128.32', '10.162.136.32',
'10.162.144.32', '10.198.0.80', '10.198.0.140', '10.192.131.9',
'10.255.255.255']


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
    if vlan:
        try:
            cursor.execute("SELECT * FROM vlan WHERE vlan_id = %s" % vlan)
            id, vlan_name, vlan_id = cursor.fetchone()
            v = Vlan.objects.get(name=vlan_name, number=vlan_id)
        except Exception, e:
            print "Unable to migrate vlan {0}".format(vlan)
    network = str(ipaddr.IPv4Address(subnet))
    prefixlen = str(calc_prefixlen(netmask))
    try:
        n, _ = Network.objects.get_or_create(
                network_str=network + '/' + prefixlen, ip_type='4',
                site=s, vlan=v)
    except Exception, e:
        print str(e)
        return None
    cursor.execute("SELECT dhcp_option, value "
                   "FROM object_option "
                   "WHERE object_id = {0} AND type = 'subnet'".format(id))
    results = cursor.fetchall() or []
    for dhcp_option, value in results:
        try:
            cursor.execute("SELECT name, type "
                           "FROM dhcp_options "
                           "WHERE id = {0}".format(dhcp_option))
            name, type = cursor.fetchone()
            kv, _ = NetworkKeyValue.objects.get_or_create(
                    value=value, key=name, network=n)
        except Exception, e:
            print str(e)
        return n


def create_range(id, start, end, type, subnet_id, comment, en, parent, known):
    """
    Takes a row form the Maintain range table
    returns a range which is saved in cyder
    """
    cursor.execute("SELECT * FROM subnet WHERE id = {0}".format(subnet_id))
    try:
        id, name, subnet, netmask, status, vlan = cursor.fetchone()
    except:
        print "Unable to find subnet with id {0}".format(subnet_id)
        return
    try:
        allow = 'legacy'
        n = Network.objects.get(ip_lower=subnet,
                prefixlen=str(calc_prefixlen(netmask)))
        if '128.193.177.71' == str(ipaddr.IPv4Address(start)):
            allow = 'vrf'
            v, _ = Vrf.objects.get_or_create(name="ip-phones-hack", network=n)
        if '128.193.166.81' == str(ipaddr.IPv4Address(start)):
            allow = 'vrf'
            v, _ = Vrf.objects.get_or_create(name="avaya-hack", network=n)
        if str(ipaddr.IPv4Address(start)) in allow_all_subnets:
            allow = None
        if known:
            allow = 'known-client'
        r_type = 'st' if type == 'static' else 'dy'
        r = Range(start_lower=start, start_str=ipaddr.IPv4Address(start),
                end_lower=end, end_str=ipaddr.IPv4Address(end), network=n,
                range_type=r_type, allow=allow)
        r.save()
        if '128.193.166.81' == str(ipaddr.IPv4Address(start)):
            rk, _ = RangeKeyValue.objects.get_or_create(range=r,
                    value='L2Q=1,L2QVLAN=503', key='ipphone242',
                    is_option=True, is_quoted=True)
    except Exception, e:
        print str(e)


def create_zone(id, name, description, comment, purge, email, notify, blank):
    """
    Takes a row from the Maintain zone table
    returns a newly made container and creates the many to many relatiosnhip
    between the new ctnr and it's associated range
    """
    c, _ = Ctnr.objects.get_or_create(name=name,
            description=comment or description)
    """
    We need to also create the workgroups and related them to containers
    """
    try:
        cursor.execute("SELECT zone_range.range "
                       "FROM zone_range "
                       "WHERE zone = {0}".format(id))
    except Exception, e:
        print str(e)
        return

    for row in cursor.fetchall():
        cursor.execute("SELECT start, end "
                       "FROM `ranges`"
                       "WHERE id = {0}".format(row[0]))
        start, end = cursor.fetchone()
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
        w, _ = Workgroup.objects.get_or_create(name=name)
        v, _ = Vrf.objects.get_or_create(name="{0}-vrf".format(name))
        cursor.execute("SELECT dhcp_option, value "
                       "FROM object_option "
                       "WHERE object_id = {0} "
                       "AND type = 'workgroup'".format(id))
        results = cursor.fetchall()
        print len(results)
        for dhcp_option, value in results:
            cursor.execute("SELECT name, type "
                           "FROM dhcp_options "
                           "WHERE id = {0}".format(dhcp_option))
            name, type = cursor.fetchone()
            kv, _ = WorkgroupKeyValue.objects.get_or_create(
                        value=value, key=name, workgroup=w)


def create_ctnr(id):
    cursor.execute("SELECT * FROM zone WHERE id={0}".format(id))
    _, name, desc, comment, _, _, _, _ = cursor.fetchone()
    c, _ = Ctnr.objects.get_or_create(name=name, description=comment or desc)
    return c


def migrate_zones():
    cursor.execute("SELECT * FROM zone")
    result = cursor.fetchall()
    for _, name, desc, comment, _, _, _, _ in result:
        c, _ = Ctnr.objects.get_or_create(name=name,
                description=comment or desc)


def migrate_dynamic_hosts():
    cursor.execute("SELECT dynamic_range, name, domain, ha, location, "
                   "workgroup, zone FROM host WHERE ip = 0")
    results = cursor.fetchall()
    print len(results)
    for range_id, name, domain_id, mac, loc, workgroup_id, zone_id in results:
        try:
            r = maintain_find_range(range_id)
        except Exception, e:
            print str(e)
            continue
        try:
            c = maintain_find_zone(zone_id)
        except:
            print "Unable to find zone with id {0}".format(zone_id)
            c = None
        try:
            d = maintain_find_domain(domain_id)
        except:
            print "Unable to find domain with id {0}".format(domain_id)
            d = None
        try:
            w = maintain_find_workgroup(workgroup_id) if workgroup_id else None
        except:
            print "Unable to find workgroup with id {0}".format(workgroup_id)
            w = None
        s, _ = System.objects.get_or_create(hostname=name, location=loc)
        if r.allow == 'vrf':
            v = Vrf.objects.get(network=r.network)
            intr, _ = DynamicInterface.objects.get_or_create(
                            range=r, workgroup=w, ctnr=c, domain=d, vrf=v)
            continue
        intr, _ = DynamicInterface.objects.get_or_create(
                            range=r, workgroup=w, ctnr=c, domain=d)


def migrate_zone_range():
    cursor.execute("SELECT * FROM zone_range")
    result = cursor.fetchall()
    for _, zone_id, range_id, _, comment, _ in result:
        cursor.execute("SELECT name FROM zone WHERE id={0}".format(zone_id))
        try:
            zone_name = cursor.fetchone()
            if not zone_name:
                continue
        except:
            # print "zone with id {0} does not exist".format(zone_id[0])
            continue
        cursor.execute("SELECT start, end "
                       "FROM `ranges` "
                       "WHERE id={0}".format(range_id))
        try:
            r_start, r_end = cursor.fetchone()
        except:
            # print "range with id {0} does not exist".format(range_id)
            continue
        try:
            c = Ctnr.objects.get(name=zone_name[0])
        except:
            # print "can't find container named {0}".format(zone_name[0])
            continue
        try:
            r = Range.objects.get(start_lower=r_start, end_lower=r_end)
        except:
            # print ("can't find range with "
            #       "start_lower = {0} and end_lower = {1}". format(
            #           r_start, r_end))
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
            # print "zone with id {0} does not exist".format(zone_id)
            continue
        cursor.execute("SELECT * FROM workgroup WHERE id={0}".format(zone_id))
        try:
            _, w_name = cursor.fetchone()
        except:
            # print "workgroup with id {0} does not exist".format(zone_id)
            continue
        try:
            c = Ctnr.objects.get(name=zone_name[0])
        except:
            # print "can't find container named {0}".format(zone_name[0])
            continue
        try:
            w = Workgroup.objects.get(name=w_name)
        except:
            # print "can't find workgroup named {0}". format(w_name)
            continue
        c.workgroups.add(w)


def maintain_find_range(range_id):
    try:
        cursor.execute("SELECT start, end "
                       "FROM `ranges` "
                       "WHERE id = {0}".format(range_id))
        start, end = cursor.fetchone()
        return Range.objects.get(start_lower=start, end_lower=end)
    except:
        raise Exception("Can't find range with an id of {0}".format(range_id))


def maintain_find_domain(domain_id):
    try:
        cursor.execute("SELECT name "
                       "FROM `domain` "
                       "WHERE id = {0}".format(domain_id))
        name = cursor.fetchone()[0]
        return Domain.objects.get(name=name)
    except:
        raise Exception("Can't find domain with id of {0}".format(domain_id))


def maintain_find_zone(zone_id):
    try:
        cursor.execute("SELECT name FROM zone where id = {0}".format(zone_id))
        name = cursor.fetchone()[0]
        return Ctnr.objects.get(name=name)
    except:
        raise Exception("Can't find zone with id of {0}".format(zone_id))


def maintain_find_workgroup(workgroup_id):
    try:
        cursor.execute("SELECT name "
                       "FROM workgroup "
                       "WHERE id = {0}".format(workgroup_id))
        name = cursor.fetchone()[0]
        return Workgroup.objects.get(name=name)
    except:
        raise Exception("Can't find workgroup id {0}".format(workgroup_id))
        return None
        migrate_dynamic_hosts()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option( '--vlan',
                action='store_true',
                dest='vlan',
                default=False,
                help='Migrate vlans'),
            make_option('-Z', '--zone',
                action='store_true',
                dest='zone',
                default=False,
                help='Migrate zones to ctnrs'),
            make_option('-w', '--workgroup',
                action='store_true',
                dest='workgroup',
                default=False,
                help='Migrate workgroups'),
            make_option('-s', '--subnet',
                action='store_true',
                dest='subnet',
                default=False,
                help='Migrate subnets'),
            make_option('-r', '--range',
                action='store_true',
                dest='range',
                default=False,
                help='Migrate ranges'),
            make_option('-d', '--dynamic',
                action='store_true',
                dest='dynamic',
                default=False,
                help='Migrate dynamic interfaces'),
            make_option('-R', '--zone-range',
                action='store_true',
                dest='zone-range',
                default=False,
                help='Migrate zone range relationship'),
            make_option('-W', '--zone-workgroup',
                action='store_true',
                dest='zone-workgroup',
                default=False,
                help='MIgrate zone workgroup relationship'),
            make_option('-D', '--delete',
                action='store_true',
                dest='delete',
                default=False,
                help='Fuck it'))

    def handle(self, **options):
        if options['vlan']:
            migrate_vlans()
        if options['zone']:
            migrate_zones()
        if options['workgroup']:
            migrate_workgroups()
        if options['subnet']:
            migrate_subnets()
        if options['range']:
            migrate_ranges()
        if options['dynamic']:
            migrate_dynamic_hosts()
        if options['zone-range']:
            migrate_zone_range()
        if options['zone-workgroup']:
            migrate_zone_workgroup()
        if options['delete']:
            Range.objects.all().delete()
            Network.objects.all().delete()
            Ctnr.objects.all().delete()
            DynamicInterface.objects.all().delete()
            Workgroup.objects.all().delete()
