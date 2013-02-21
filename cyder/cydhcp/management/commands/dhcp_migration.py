from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup, WorkgroupKeyValue
import ipaddr
import MySQLdb
from optparse import make_option


allow_all_subnets = [
    '10.192.76.2', '10.192.103.150', '10.192.15.2',
    '10.197.32.0', '10.192.148.32', '10.192.144.32',  '10.192.140.32',
    '10.196.0.32', '10.196.4.32', '10.192.136.63', '10.196.8.8',
    '10.196.16.8', '10.196.24.8', '10.196.32.8', '10.196.40.8',
    '10.162.128.32', '10.162.136.32', '10.162.144.32', '10.198.0.80',
    '10.198.0.140', '10.192.131.9', '10.255.255.255']


class NotInMaintain(Exception):
    """"""


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


def create_subnet(subnet_id, name, subnet, netmask, status, vlan):
    """
    Takes a row from the Maintain subnet table
    returns a new network object and creates the vlan it is associated with
    """
    prefixlen = str(calc_prefixlen(netmask))
    network = str(ipaddr.IPv4Address(subnet & netmask))
    s, _ = Site.objects.get_or_create(name='Campus')
    v = None
    if cursor.execute("SELECT * "
                      "FROM vlan "
                      "WHERE vlan_id = %s" % vlan):
        vlan_id, vlan_name, vlan_number = cursor.fetchone()
        v = Vlan.objects.get(name=vlan_name)
    n, created = Network.objects.get_or_create(
        network_str=network + '/' + prefixlen, ip_type='4',
        site=s, vlan=v)
    cursor.execute("SELECT dhcp_option, value "
                   "FROM object_option "
                   "WHERE object_id = {0} "
                   "AND type = 'subnet'".format(subnet_id))
    results = cursor.fetchall()
    for dhcp_option, value in results:
        cursor.execute("SELECT name, type "
                       "FROM dhcp_options "
                       "WHERE id = {0}".format(dhcp_option))
        name, type = cursor.fetchone()
        kv, _ = NetworkKeyValue.objects.get_or_create(
            value=str(value), key=name, network=n)
    return (n, created)


def create_range(range_id, start, end, type, subnet_id, comment, en, known):
    """
    Takes a row form the Maintain range table
    returns a range which is saved in cyder
    """
    # Set the allow statement
    n = None
    r = None
    r_type = 'st' if type is 'static' else 'dy'
    allow = 'legacy'
    if cursor.execute("SELECT * FROM subnet WHERE id = {0}".format(subnet_id)):
        id, name, subnet, netmask, status, vlan = cursor.fetchone()
        n = Network.objects.get(ip_lower=subnet,
                                prefixlen=str(calc_prefixlen(netmask)))
        n.update_network()
        if str(ipaddr.IPv4Address(start)) in allow_all_subnets:
            allow = None
        if known:
            allow = 'known-client'
        if '128.193.177.71' == str(ipaddr.IPv4Address(start)):
            allow = 'vrf'
            v, _ = Vrf.objects.get_or_create(name="ip-phones-hack", network=n)
        if '128.193.166.81' == str(ipaddr.IPv4Address(start)):
            allow = 'vrf'
            v, _ = Vrf.objects.get_or_create(name="avaya-hack", network=n)

        if int(n.network.network) < start < end < int(n.network.broadcast):
            r, created = Range.objects.get_or_create(
                start_lower=start, start_str=ipaddr.IPv4Address(start),
                end_lower=end, end_str=ipaddr.IPv4Address(end),
                range_type=r_type, allow=allow, ip_type='4',
                network=n)
    if not r:
        r, created = Range.objects.get_or_create(
            start_lower=start, start_str=ipaddr.IPv4Address(start),
            end_lower=end, end_str=ipaddr.IPv4Address(end),
            is_reserved=True, range_type=r_type, allow=allow, ip_type='4')
    if '128.193.166.81' == str(ipaddr.IPv4Address(start)):
        rk, _ = RangeKeyValue.objects.get_or_create(
            range=r, value='L2Q=1,L2QVLAN=503', key='ipphone242',
            is_option=True, is_quoted=True)
    return (r, created)


def create_zone(id, name, description, comment, purge, email, notify, blank):
    """
    Takes a row from the Maintain zone table
    returns a newly made container and creates the many to many relatiosnhip
    between the new ctnr and it's associated range
    """
    c, created = Ctnr.objects.get_or_create(name=name,
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
        if cursor.execute("SELECT start, end "
                          "FROM `ranges` "
                          "WHERE id = {0}".format(row[0])):
            start, end = cursor.fetchone()
            r = Range.objects.get(start_lower=start, end_lower=end)
            c.ranges.add(r)
    return (c, created)


def migrate_subnets():
    migrated = []
    cursor.execute("SELECT * FROM subnet")
    results = cursor.fetchall()
    for row in results:
        migrated.append(create_subnet(*row))
    print ("Records in Maintain {0}\n"
           "Records Migrated {1}\n"
           "Records created {2}".format(
               len(results),
               len(migrated),
               len([y for x, y in migrated if y])))


def migrate_ranges():
    cursor.execute("SELECT id, start, end, type, subnet, comment, enabled, "
                   "allow_all_hosts "
                   "FROM `ranges`")
    results = cursor.fetchall()
    migrated = []
    for row in results:
        migrated.append(create_range(*row))
    print ("Records in Maintain {0}\n"
           "Records Migrated {1}\n"
           "Records created {2}".format(
               len(results),
               len(migrated),
               len([y for x, y in migrated if y])))


def migrate_vlans():
    cursor.execute("SELECT * FROM vlan")
    results = cursor.fetchall()
    migrated = []
    for _, name, number in results:
        migrated.append(Vlan.objects.get_or_create(name=name, number=number))
    print ("Records in Maintain {0}\n"
           "Records Migrated {1}\n"
           "Records created {2}".format(
               len(results),
               len(migrated),
               len([y for x, y in migrated if y])))


def migrate_workgroups():
    cursor.execute("SELECT * FROM workgroup")
    results = cursor.fetchall()
    migrated = []
    for id, name in results:
        w, created = Workgroup.objects.get_or_create(name=name)
        cursor.execute("SELECT dhcp_option, value "
                       "FROM object_option "
                       "WHERE object_id = {0} "
                       "AND type = 'workgroup'".format(id))
        _results = cursor.fetchall()
        for dhcp_option, value in _results:
            cursor.execute("SELECT name, type "
                           "FROM dhcp_options "
                           "WHERE id = {0}".format(dhcp_option))
            name, type = cursor.fetchone()
            kv, _ = WorkgroupKeyValue.objects.get_or_create(
                value=value, key=name, workgroup=w)
        migrated.append((w, created))
    print ("Records in Maintain {0}\n"
           "Records Migrated {1}\n"
           "Records created {2}".format(
               len(results),
               len(migrated),
               len([y for x, y in migrated if y])))


def create_ctnr(id):
    cursor.execute("SELECT * FROM zone WHERE id={0}".format(id))
    _, name, desc, comment, _, _, _, _ = cursor.fetchone()
    c = Ctnr.objects.get_or_create(name=name, description=comment or desc)
    return c


def migrate_zones():
    cursor.execute("SELECT name, description, comment, "
                   "support_mail, allow_blank_ha "
                   "FROM zone")
    migrated = []
    results = cursor.fetchall()
    for name, desc, comment, email_contact, allow_blank_mac in results:
        migrated.append(
            Ctnr.objects.get_or_create(
                name=name,
                description=comment or desc,
                email_contact=email_contact))
    print ("Records in Maintain {0}\n"
           "Records Migrated {1}\n"
           "Records created {2}".format(
               len(results),
               len(migrated),
               len([y for x, y in migrated if y])))


def migrate_dynamic_hosts():
    cursor.execute("SELECT dynamic_range, name, domain, ha, location, "
                   "workgroup, zone FROM host WHERE ip = 0")
    results = cursor.fetchall()
    for range_id, name, domain_id, mac, loc, workgroup_id, zone_id in results:
        r = maintain_find_range(range_id)
        c = maintain_find_zone(zone_id) if zone_id else None
        d = maintain_find_domain(domain_id) if domain_id else None
        w = maintain_find_workgroup(workgroup_id) if workgroup_id else None
        s, _ = System.objects.get_or_create(hostname=name, location=loc)
        if r.allow == 'vrf':
            v = Vrf.objects.get(network=r.network)
            intr, _ = DynamicInterface.objects.get_or_create(
                range=r, workgroup=w, ctnr=c, domain=d, vrf=v,
                mac=mac, system=s)
            continue
        intr, _ = DynamicInterface.objects.get_or_create(
            system=s, range=r, workgroup=w, ctnr=c, domain=d, mac=mac)


def migrate_user():
    cursor.execute("SELECT username FROM user")
    result = cursor.fetchall()
    for username, in result:
        username = username.lower()
        user, _ = User.objects.get_or_create(username=username)


def migrate_zone_user():
    NEW_LEVEL = {5: 0, 25: 1, 50: 2, 100: 3}
    cursor.execute("SELECT * FROM zone_user")
    result = cursor.fetchall()
    for _, username, zone_id, level in result:
        username = username.lower()
        level = NEW_LEVEL[level]
        ctnr = maintain_find_zone(zone_id)
        user, _ = User.objects.get_or_create(username=username)
        CtnrUser.get_or_create(user=user, ctnr=ctnr, level=level)


def migrate_zone_range():
    cursor.execute("SELECT * FROM zone_range")
    result = cursor.fetchall()
    for _, zone_id, range_id, _, comment, _ in result:
        if cursor.execute("SELECT name "
                          "FROM zone WHERE id={0}".format(zone_id)):
            zone_name = cursor.fetchone()[0]
        else:
            continue
        if cursor.execute("SELECT start, end "
                          "FROM `ranges` "
                          "WHERE id={0}".format(range_id)):
            r_start, r_end = cursor.fetchone()
        else:
            continue
        c = Ctnr.objects.get(name=zone_name)
        r = Range.objects.get(start_lower=r_start, end_lower=r_end)
        c.ranges.add(r)
        c.save()


def migrate_zone_domain():
    cursor.execute("SELECT zone, domain FROM zone_domain")
    results = cursor.fetchall()
    for zone_id, domain_id in results:
        ctnr = maintain_find_zone(zone_id)
        domain = maintain_find_domain(domain_id)
        try:
            ctnr.domains.add(domain)
            ctnr.save()
        except:
            raise NotInMaintain("Unable to migrate relation between "
                                "domain_id {0} and "
                                "zone_id {1}".format(zone_id, domain_id))


def migrate_zone_workgroup():
    cursor.execute("SELECT * FROM zone_workgroup")
    result = cursor.fetchall()
    for _, workgroup_id, zone_id, _ in result:
        if cursor.execute("SELECT name "
                          "FROM zone WHERE id={0}".format(zone_id)):
            zone_name = cursor.fetchone()[0]
            if cursor.execute("SELECT * "
                              "FROM workgroup "
                              "WHERE id={0}".format(workgroup_id)):
                _, w_name = cursor.fetchone()
                c = Ctnr.objects.get(name=zone_name)
                w = Workgroup.objects.get(name=w_name)
                c.workgroups.add(w)


def maintain_find_range(range_id):
    if cursor.execute("SELECT start, end "
                      "FROM `ranges` "
                      "WHERE id = {0}".format(range_id)):
        start, end = cursor.fetchone()
        return Range.objects.get(start_lower=start, end_lower=end)
    return None


def maintain_find_domain(domain_id):
    if cursor.execute("SELECT name "
                      "FROM `domain` "
                      "WHERE id = {0}".format(domain_id)):
        name = cursor.fetchone()[0]
        return Domain.objects.get(name=name)
    return None


def maintain_find_zone(zone_id):
    if cursor.execute("SELECT name FROM zone where id = {0}".format(zone_id)):
        name = cursor.fetchone()[0]
        return Ctnr.objects.get(name=name) if name else None
    return None


def maintain_find_workgroup(workgroup_id):
    if cursor.execute("SELECT name "
                      "FROM workgroup "
                      "WHERE id = {0}".format(workgroup_id)):
        name = cursor.fetchone()[0]
        return Workgroup.objects.get(name=name)
    return None


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--vlan',
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
                    help='Migrate zone workgroup relationship'),
        make_option('-D', '--delete',
                    action='store_true',
                    dest='delete',
                    default=False,
                    help='Delete things'),
        make_option('-z', '--zone-domain',
                    action='store_true',
                    dest='zone-domain',
                    default=False,
                    help='GIMME IT ALL!!!11!!'),
        make_option('-u', '--user',
                    action='store_true',
                    dest='user',
                    default=False,
                    help='Migrate users'),
        make_option('-U', '--zone-user',
                    action='store_true',
                    dest='zone-user',
                    default=False,
                    help='Migrate zone user relationship'),
        make_option('-a', '--all',
                    action='store_true',
                    dest='all',
                    default=False,
                    help='Migrate everything'))

    def handle(self, **options):
        if options['delete']:
            Range.objects.all().delete()
            Network.objects.all().delete()
            Ctnr.objects.filter(id__gt=2).delete()  # First 2 are fixtures
            DynamicInterface.objects.all().delete()
            Workgroup.objects.all().delete()
            User.objects.filter(id__gt=1).delete()  # First user is a fixture
            CtnrUser.objects.filter(id__gt=2).delete()  # First 2 are fixtures
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
        if options['zone-domain']:
            migrate_zone_domain()
        if options['user']:
            migrate_user()
        if options['zone-user']:
            migrate_zone_user()
        if options['all']:
            migrate_vlans()
            migrate_zones()
            migrate_workgroups()
            migrate_subnets()
            migrate_ranges()
            migrate_dynamic_hosts()
            migrate_zone_range()
            migrate_zone_workgroup()
            migrate_user()
            migrate_zone_user()
