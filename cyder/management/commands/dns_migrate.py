#! /usr/bin/python
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.conf import settings
from sys import stderr

from cyder.base.eav.models import Attribute
from cyder.core.system.models import System, SystemAV

from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.utils import ensure_domain
from cyder.cydns.models import View

import MySQLdb
from optparse import make_option
from lib import maintain_dump, fix_maintain
from lib.utilities import (clean_mac, ip2long, long2ip, fix_attr_name,
                           range_usage_get_create)

public, _ = View.objects.get_or_create(name="public")
private, _ = View.objects.get_or_create(name="private")

BAD_DNAMES = ['', '.', '_']
connection = MySQLdb.connect(host=settings.MIGRATION_HOST,
                             user=settings.MIGRATION_USER,
                             passwd=settings.MIGRATION_PASSWD,
                             db=settings.MIGRATION_DB,
                             charset='utf8')
cursor = connection.cursor()


class Zone(object):

    def __init__(self, domain_id=None, dname=None, soa=None, gen_recs=True):
        self.domain_id = 541 if domain_id is None else domain_id
        self.dname = self.get_dname() if dname is None else dname

        self.domain = self.gen_domain()
        if self.domain:
            if gen_recs:
                self.gen_MX()
                self.gen_static()
                self.gen_AR()
                self.gen_NS()
                self.domain.soa = self.gen_SOA() or soa
            self.domain.save()
            self.walk_zone(gen_recs=gen_recs)

    def gen_SOA(self):
        """Generates an SOA record object if the SOA record exists.

        :uniqueness: primary, contact, refresh, retry, expire, minimum, comment
        """
        cursor.execute("SELECT primary_master, hostmaster, refresh, "
                       "retry, expire, ttl "
                       "FROM soa "
                       "WHERE domain = %s" % self.domain_id)
        record = cursor.fetchone()

        if record:
            primary, contact, refresh, retry, expire, minimum = record
            primary, contact = primary.lower(), contact.lower()

            soa, _ = SOA.objects.get_or_create(
                primary=primary, contact=contact, refresh=refresh,
                retry=retry, expire=expire, minimum=minimum,
                root_domain=self.domain, description='')
            return soa
        else:
            return None

    def gen_domain(self):
        """Generates a Domain object for this Zone from a hostname.

        :uniqueness: domain
        """
        if not (self.dname in BAD_DNAMES or 'in-addr.arpa' in self.dname):
            return ensure_domain(name=self.dname, force=True,
                                 update_range_usage=False)

    def gen_MX(self):
        """Generates the MX Record objects related to this zone's domain.

        .. note::
            Where multiple records with different ttls exist, only the
            first is kept.

        :uniqueness: label, domain, server, priority
        """
        cursor.execute("SELECT name, server, priority, ttl, enabled "
                       "FROM zone_mx "
                       "WHERE domain = '%s';" % self.domain_id)

        for name, server, priority, ttl, enabled in cursor.fetchall():
            name, server = name.lower(), server.lower()
            if MX.objects.filter(label=name,
                                 domain=self.domain,
                                 server=server,
                                 priority=priority).exists():
                print "Ignoring MX %s; MX already exists." % server
                continue

            try:
                mx, _ = MX.objects.get_or_create(label=name,
                                                 domain=self.domain,
                                                 server=server,
                                                 priority=priority,
                                                 ttl=ttl)
                if enabled:
                    mx.views.add(public)
                    mx.views.add(private)
            except ValidationError, e:
                stderr.write("Error generating MX. %s\n" % e)

    def gen_static(self):
        """
        Generates the Static Interface objects related to this zone's domain.

        .. note::
            Every static interface needs a system.

        :System uniqueness: hostname, mac, ip_str

        :StaticInterface uniqueness: hostname, mac, ip_str
        """
        from dhcp_migrate import maintain_find_zone, migrate_zones

        if Ctnr.objects.count() <= 2:
            print "WARNING: Zones not migrated. Attempting to migrate now."
            migrate_zones()

        sys_value_keys = {"type": "Hardware Type",
                          "os": "Operating System",
                          "location": "Location",
                          "department": "Department",
                          "serial": "Serial Number",
                          "other_id": "Other ID",
                          "purchase_date": "Purchase Date",
                          "po_number": "PO Number",
                          "warranty_date": "Warranty Date",
                          "owning_unit": "Owning Unit",
                          "user_id": "User ID"}

        keys = ("id", "ip", "name", "workgroup", "enabled", "ha", "zone",
                "type", "os", "location", "department", "serial", "other_id",
                "purchase_date", "po_number", "warranty_date", "owning_unit",
                "user_id", "last_seen", "expire", "ttl", "last_update")

        sql = ("SELECT %s FROM host WHERE ip != 0 AND domain = '%s';" %
               (", ".join(keys), self.domain_id))

        cursor.execute(sql)
        for values in cursor.fetchall():
            items = dict(zip(keys, values))
            ctnr = maintain_find_zone(items['zone'])

            name = items['name']
            enabled = bool(items['enabled'])
            ip = items['ip']
            ha = items['ha']
            if ip == 0:
                continue

            if len(ha) != 12 or ha == '0' * 12:
                ha = ""

            if ha == "":
                enabled = False

            # check for duplicate
            static = StaticInterface.objects.filter(
                label=name, mac=clean_mac(ha), ip_str=long2ip(ip))
            if static:
                stderr.write("Ignoring host %s: already exists.\n"
                             % items['id'])
                continue

            # create system
            system = System(name=name)
            system.save()
            for key in sys_value_keys.keys():
                value = items[key].strip()
                if not value or value == '0':
                    continue
                attr = Attribute.objects.get(
                    name=fix_attr_name(sys_value_keys[key]))
                eav = SystemAV(entity=system, attribute=attr, value=value)
                eav.full_clean()
                eav.save()

            # check for workgroup
            if items['workgroup'] is not None:
                cursor.execute("SELECT name "
                               "FROM workgroup "
                               "WHERE id = {0}".format(items['workgroup']))
                wname = cursor.fetchone()[0]
                w, _ = Workgroup.objects.get_or_create(name=wname)
            else:
                w = None

            static = StaticInterface(
                label=name, domain=self.domain, mac=clean_mac(ha),
                system=system, ip_str=long2ip(ip), ip_type='4',
                workgroup=w, ctnr=ctnr, ttl=items['ttl'],
                dns_enabled=enabled, dhcp_enabled=enabled,
                last_seen=items['last_seen'])

            # create static interface
            try:
                static.full_clean()
                static.save(update_range_usage=False)
            except ValidationError:
                try:
                    static.dhcp_enabled = False
                    static.dns_enabled = enabled
                    static.full_clean()
                    static.save(update_range_usage=False)
                except ValidationError, e:
                    stderr.write("Error creating static interface for host"
                                 "with IP {0}\n".format(static.ip_str))
                    stderr.write("Original exception: {0}\n".format(e))
                    static = None
                    system.delete()

            if static:
                static.views.add(public)
                static.views.add(private)

    def gen_AR(self):
        """
        Generates the Address Record and PTR objects related to this zone's
        domain.

        .. note::
            Some AddressRecords may need to be added to the pointer table in
            MAINTAIN for successful migration, for example,
            cob-dc81 and cob-dc82.bus.oregonstate.edu

        .. note::
            AddressRecords/PTRs with the same ip as a StaticInterface can't
            coexist, so if a StaticInterface with the same ip exists, it has
            priority.

        :AddressRecord uniqueness: label, domain, ip_str, ip_type

        :PTR uniqueness: name, ip_str, ip_type
        """
        name = self.domain.name
        cursor.execute("SELECT ip, hostname, type, enabled "
                       "FROM pointer "
                       "WHERE hostname LIKE '%%.%s';" % name)
        for ip, hostname, ptr_type, enabled, in cursor.fetchall():
            hostname = hostname.lower()
            label, dname = hostname.split('.', 1)
            if dname != name:
                continue

            dup_stats = StaticInterface.objects.filter(ip_str=long2ip(ip))
            if dup_stats.exists():
                if ptr_type == 'reverse':
                    print "Ignoring PTR %s; Static intr exists." % long2ip(ip)
                    continue
                elif dup_stats.filter(fqdn=hostname).exists():
                    print "Ignoring AR %s; Static intr exists." % hostname
                    continue
                else:
                    pass

            if ptr_type == 'forward':
                if AddressRecord.objects.filter(
                        fqdn=hostname, ip_str=long2ip(ip)).exists():
                    continue

                arec, _ = range_usage_get_create(
                    AddressRecord, label=label, domain=self.domain,
                    ip_str=long2ip(ip), ip_type='4')

                if enabled:
                    arec.views.add(public)
                    arec.views.add(private)

            elif ptr_type == 'reverse':
                if not PTR.objects.filter(ip_str=long2ip(ip)).exists():
                    ptr = PTR(label=label, domain=self.domain,
                              ip_str=long2ip(ip), ip_type='4')

                    # PTRs need to be cleaned independently of saving
                    # (no get_or_create)
                    ptr.full_clean()
                    ptr.save(update_range_usage=False)
                    if enabled:
                        ptr.views.add(public)
                        ptr.views.add(private)
                else:
                    print "Ignoring PTR %s; already exists." % long2ip(ip)

    def gen_NS(self):
        """
        Generates the Nameserver objects related to this zone's domain.

        :uniqueness: domain, server name
        """
        cursor.execute("SELECT * "
                       "FROM nameserver "
                       "WHERE domain='%s';" % self.domain_id)
        for _, name, _, _ in cursor.fetchall():
            name = name.lower()
            try:
                ns, _ = Nameserver.objects.get_or_create(domain=self.domain,
                                                         server=name)
                ns.views.add(public)
                ns.views.add(private)
            except ValidationError, e:
                stderr.write("Error generating NS. %s\n" % e)

    def walk_zone(self, gen_recs=True):
        """
        Recursively traverses the domain tree, creating Zone objects and
        migrating related DNS objects along the way.

        .. note::
            Child domains will inherit this domain's SOA if they do not have
            their own.
        """
        sql = ("SELECT id, name "
               "FROM domain "
               "WHERE name NOT LIKE \"%%.in-addr.arpa\" "
               "AND master_domain = %s;" % self.domain_id)
        cursor.execute(sql)
        for child_id, child_name in cursor.fetchall():
            child_name = child_name.lower()
            Zone(child_id, child_name, self.domain.soa, gen_recs=gen_recs)

    def get_dname(self):
        """
        Finds a domain name for this Zone's domain id.
        """
        cursor.execute('SELECT * FROM domain WHERE id = %s;' % self.domain_id)
        _, dname, _, _ = cursor.fetchone()
        dname = dname.lower()
        return dname

    #TODO: Cleanup functions for leftover objects to migrate
    # (static interfaces and PTRs)


def gen_CNAME():
    """Migrates CNAME objects.

    .. note::
        Run this only after migrating other DNS objects for every zone.

    .. note::
        Because MAINTAIN is totally messed up, some hostnames in the CNAME
        table have ``.``'s in them, so the fully qualified domain name is
        created first, then the label is stripped off of the front of that.

    .. note::
        If the fully qualified domain name of the label + domain name already
        exists as a domain object, that object becomes the alias and the label
        prefix is set to the empty string. Otherwise, the alias is the
        label + domain name.

    :uniqueness: label, domain, target
    """
    print "Creating CNAMEs."
    cursor.execute("SELECT * FROM zone_cname")

    for _, server, name, domain_id, ttl, zone, enabled in cursor.fetchall():
        server, name = server.lower(), name.lower()
        if not cursor.execute("SELECT name FROM domain WHERE id = '%s'"
                              % domain_id):
            stderr.write('Ignoring CNAME {0}; domain does not exist.\n'
                         .format(name))
            continue
        dname, = cursor.fetchone()
        if not dname:
            continue
        dname = dname.lower()

        fqdn = ".".join([name, dname])
        name, dname = fqdn.split(".", 1)

        if Domain.objects.filter(name=fqdn).exists():
            domain = Domain.objects.get(name=fqdn)
            name = ""
        elif Domain.objects.filter(name=dname).exists():
            domain = Domain.objects.get(name=dname)
        else:
            print "Ignoring CNAME %s: No domain." % fqdn
            continue

        if server == ".".join([name, domain.name]):
            # In maintain, at least one CNAME is a loop: biosys.bioe.orst.edu
            print "Ignoring CNAME %s: Is a loop." % server
            continue

        cn = CNAME(label=name, domain=domain, target=server)
        cn.set_fqdn()
        dup_ptrs = PTR.objects.filter(fqdn=cn.fqdn)
        if dup_ptrs:
            print "Removing duplicate PTR for %s" % cn.fqdn
            dup_ptrs.delete(update_range_usage=False)

        # CNAMEs need to be cleaned independently of saving (no get_or_create)
        cn.full_clean()
        cn.save()
        if enabled:
            cn.views.add(public)
            cn.views.add(private)


def gen_reverses():
    print "Creating reverse domains."
    add_pointers_manual()
    Domain.objects.get_or_create(name='arpa', is_reverse=True)
    Domain.objects.get_or_create(name='in-addr.arpa', is_reverse=True)

    reverses = settings.REVERSE_DOMAINS

    for i in reverses:
        if '.' in i:
            reverses.append(i.split('.', 1)[1])

    reverses.reverse()

    for i in reverses:
        Domain.objects.get_or_create(name="%s.in-addr.arpa" % i,
                                     is_reverse=True)


def gen_DNS(skip_edu=False):
    gen_reverses()

    cursor.execute('SELECT * FROM domain WHERE master_domain = 0')
    for domain_id, dname, _, _ in cursor.fetchall():
        if "edu" in dname and skip_edu:
            continue
        print "Creating %s zone." % dname
        Zone(domain_id=domain_id, dname=dname)


def gen_domains_only():
    gen_reverses()

    cursor.execute('SELECT * FROM domain WHERE master_domain = 0')
    for domain_id, dname, _, _ in cursor.fetchall():
        print "Creating %s. (domain only)" % dname
        Zone(domain_id=domain_id, dname=dname, gen_recs=False)


def add_pointers_manual():
    opts = settings.POINTERS
    for opt in opts:
        (ip, hn, ptype) = opt
        ip = ip2long(ip)
        sql = ('SELECT count(*) FROM pointer WHERE ip = %s AND hostname = "%s"'
               'AND type = "%s"' % (ip, hn, ptype))
        cursor.execute(sql)
        exists = cursor.fetchone()[0]
        if not exists:
            sql = ('INSERT INTO pointer (ip, hostname, type) '
                   'VALUES (%s, "%s", "%s")' % (ip, hn, ptype))
            cursor.execute(sql)


def dump_maintain():
    maintain_dump.main()


def delete_DNS():
    print "Deleting DNS objects."
    for thing in [Domain, AddressRecord, PTR, SOA, MX, Nameserver,
                  StaticInterface, System, Workgroup]:
        thing.objects.all().delete()


def delete_CNAME():
    print 'Deleting CNAMEs.'
    CNAME.objects.all().delete()


def do_everything(skip_edu=False):
    delete_DNS()
    delete_CNAME()
    gen_DNS(skip_edu)
    gen_CNAME()


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-D', '--dump',
                    action='store_true',
                    dest='dump',
                    default=False,
                    help='Get a fresh dump of MAINTAIN'),
        make_option('-f', '--fix',
                    action='store_true',
                    dest='fix',
                    default=False,
                    help='Fix MAINTAIN'),
        make_option('-d', '--dns',
                    dest='dns',
                    default=False,
                    action='store_true',
                    help='Migrate DNS objects'),
        make_option('-o', '--domains-only',
                    dest='domains',
                    default=False,
                    action='store_true',
                    help='Migrate domains only'),
        make_option('-c', '--cname',
                    action='store_true',
                    dest='cname',
                    default=False,
                    help='Migrate CNAMEs'),
        make_option('-X', '--delete',
                    dest='delete',
                    action='store_true',
                    default=False,
                    help='Delete old objects'),
        make_option('-s', '--skip',
                    dest='skip',
                    action='store_true',
                    default=False,
                    help='Skip edu zone.'))

    def handle(self, **options):
        if options['dump']:
            dump_maintain()

        if options['delete']:
            if options['dns']:
                delete_DNS()
            if options['cname']:
                delete_CNAME()

        if options['fix']:
            fix_maintain.main()

        if options['dns']:
            gen_DNS(options['skip'])

        if options['cname']:
            gen_CNAME()

        if options['domains']:
            gen_domains_only()
