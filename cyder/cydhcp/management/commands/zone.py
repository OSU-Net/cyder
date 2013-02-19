#! /usr/bin/python
from optparse import make_option

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.conf import settings

import fix_maintain
import maintain_dump
import MySQLdb
from utilities import clean_mac, ip2long, long2ip

from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.utils import ensure_domain
from cyder.cydns.models import View

public, _ = View.objects.get_or_create(name="public")

BAD_DNAMES = ['', '.', '_']
connection = MySQLdb.connect(host=settings.MIGRATION_HOST,
                             user=settings.MIGRATION_USER,
                             passwd=settings.MIGRATION_PASSWD,
                             db=settings.MIGRATION_DB)
cursor = connection.cursor()


class Zone(object):

    def __init__(self, domain_id=None, dname=None, soa=None):
        self.domain_id = 541 if domain_id == None else domain_id
        self.dname = self.get_dname() if dname == None else dname

        self.domain = self.gen_domain()
        if self.domain:
            self.domain.soa = self.gen_soa() or soa
            self.domain.save()
            self.gen_MX()
            self.gen_static()
            self.gen_AR()
            self.gen_NS()
            self.walk_zone()

    def gen_soa(self):
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
            soa, _ = SOA.objects.get_or_create(
                primary=primary, contact=contact, refresh=refresh,
                retry=retry, expire=expire, minimum=minimum,
                description='SOA for %s zone' % self.dname)
            return soa
        else:
            return None

    def gen_domain(self):
        """Generates a Domain object for this Zone from a hostname.

        :uniqueness: domain
        """
        if not (self.dname in BAD_DNAMES or 'in-addr.arpa' in self.dname):
            return ensure_domain(name=self.dname, force=True)

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
            if MX.objects.filter(label=name,
                                 domain=self.domain,
                                 server=server,
                                 priority=priority).exists():
                continue

            try:
                mx, _ = MX.objects.get_or_create(label=name,
                                                 domain=self.domain,
                                                 server=server,
                                                 priority=priority,
                                                 ttl=ttl)
                if enabled:
                    mx.views.add(public)
            except ValidationError:
                print "Error generating MX."

    def gen_static(self):
        """
        Generates the Static Interface objects related to this zone's domain.

        .. note::
            Every static interface needs a system.

        :System uniqueness: hostname, mac, ip_str

        :StaticInterface uniqueness: hostname, mac, ip_str
        """
        cursor.execute("SELECT id, ip, name, workgroup, enabled, ha, "
                       "type, os, location, department , serial, other_id, "
                       "purchase_date, po_number, warranty_date, owning_unit, "
                       "user_id "
                       "FROM host "
                       "WHERE ip != 0 AND domain = '%s';" % self.domain_id)
        for id, ip, name, workgroup, enabled, ha, type, os, location, dept, \
                serial, other_id, purchase_date, po_number, warranty_date, \
                owning_unit, user_id in cursor.fetchall():
            if ip == 0:
                continue

            if len(ha) != 12:
                ha = "0" * 12

            # TODO: Make systems unique by hostname, ip, mac tuple
            # TODO: Add key-value attributes to system objects.

            system, _ = System.objects.get_or_create(
                    name=name, location=location, department=dept)
            try:
                cursor.execute("SELECT name "
                               "FROM workgroup"
                               "WHERE id = {0}".format(workgroup))
                name = cursor.fetchone()[0]
                w, _ = Workgroup.objects.get_or_create(name=name)
                v, _ = Vrf.objects.get_or_create(name="{0}-".format(name))
            except:
                v = None
                w = None

            if not (StaticInterface.objects.filter(
                    label=name, mac=clean_mac(ha), ip_str=long2ip(ip))
                    .exists()):
                try:
                    static = StaticInterface(label=name, domain=self.domain,
                            mac=clean_mac(ha), system=system, ip_str=long2ip(ip),
                            ip_type='4', vrf=v, workgroup=w)

                    # Static Interfaces need to be cleaned independently of saving.
                    # (no get_or_create)
                    static.full_clean()
                    static.save()
                    if enabled:
                        static.views.add(public)
                    cursor.execute("SELECT dhcp_option, value "
                                   "FROM object_option "
                                   "WHERE object_id = {0} "
                                   "AND type = 'host'".format(id))
                    results = cursor.fetchall()
                    for dhcp_option, value in results:
                        cursor.execute("SELECT name, type "
                                       "FROM dhcp_options "
                                       "WHERE id = {0}".format(dhcp_option))
                        name, type = cursor.fetchone()
                        kv = StaticIntrKeyValue(intr=static, key=name, value=value)
                        kv.clean()
                        kv.save()
                except  ValidationError, e:
                    print str(e)

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

            label, dname = hostname.split('.', 1)
            if dname != name:
                continue

            if StaticInterface.objects.filter(ip_str=long2ip(ip)).exists():
                continue

            if ptr_type == 'forward':
                arec, _ = AddressRecord.objects.get_or_create(
                            label=label, domain=self.domain,
                            ip_str=long2ip(ip), ip_type='4')
                if enabled:
                    arec.views.add(public)

            elif ptr_type == 'reverse':
                if not PTR.objects.filter(
                        name=name, ip_str=long2ip(ip)).exists():
                    ptr = PTR(name=name, ip_str=long2ip(ip), ip_type='4')

                    # PTRs need to be cleaned independently of saving
                    # (no get_or_create)
                    ptr.full_clean()
                    ptr.save()
                    if enabled:
                        ptr.views.add(public)

    def gen_NS(self):
        """
        Generates the Nameserver objects related to this zone's domain.

        :uniqueness: domain, server name
        """
        cursor.execute("SELECT * "
                       "FROM nameserver "
                       "WHERE domain='%s';" % self.domain_id)
        for _, name, _, _ in cursor.fetchall():
            try:
                ns, _ = Nameserver.objects.get_or_create(
                        domain=self.domain, server=name)
                ns.views.add(public)
            except ValidationError:
                print "Error generating NS."

    def walk_zone(self):
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
            Zone(child_id, child_name, self.domain.soa)

    def get_dname(self):
        """
        Finds a domain name for this Zone's domain id.
        """
        cursor.execute('SELECT * FROM domain WHERE id = %s;' % self.domain_id)
        _, dname, _, _ = cursor.fetchone()
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
    cursor.execute("SELECT * FROM zone_cname")

    for _, server, name, domain_id, ttl, zone, enabled in cursor.fetchall():
        cursor.execute("SELECT name FROM domain WHERE id = '%s'" % domain_id)
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
            continue

        if server == ".".join([name, domain.name]):
            # In maintain, at least one CNAME is a loop: biosys.bioe.orst.edu
            continue

        cn = CNAME(label=name, domain=domain, target=server)
        # CNAMEs need to be cleaned independently of saving (no get_or_create)
        cn.full_clean()
        cn.save()
        if enabled:
            cn.views.add(public)


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
            make_option('-c', '--cname',
                action='store_true',
                dest='cname',
                default=False,
                help='Migrate CNAMEs'),
            make_option('-X', '--delete',
                dest='delete',
                action='store_true',
                default=False,
                help='Delete old objects'))

    def handle(self, **options):
        if options['dump']:
            maintain_dump.main()
            opts = settings.POINTERS
            for opt in opts:
                (ip, hn, ptype) = opt
                x = (ip2long(ip), hn, ptype)
                sql = ('INSERT INTO pointer (ip, hostname, type) '
                       'VALUES (%s, "%s", "%s")' % x)
                cursor.execute(sql)

        if options['delete']:
            if options['dns']:
                AddressRecord.objects.all().delete()
                Domain.objects.all().delete()
                MX.objects.all().delete()
                Nameserver.objects.all().delete()
                PTR.objects.all().delete()
                SOA.objects.all().delete()
                StaticInterface.objects.all().delete()
                System.objects.all().delete()
            if options['cname']:
                CNAME.objects.all().delete()

        if options['fix']:
            fix_maintain.main()

        if options['dns']:
            Domain.objects.get_or_create(name='arpa', is_reverse=True)
            Domain.objects.get_or_create(name='in-addr.arpa', is_reverse=True)

            reverses = settings.REVERSE_DOMAINS

            for i in reverses:
                if '.' in i:
                    reverses.append(i.split('.', 1)[1])

            reverses.reverse()

            for i in reverses:
                print "%s.in-addr.arpa" % i
                Domain.objects.get_or_create(name="%s.in-addr.arpa" % i,
                                             is_reverse=True)

            cursor.execute('SELECT * FROM domain WHERE master_domain = 0')
            for domain_id, dname, _, _ in cursor.fetchall():
                print "Creating %s zone." % dname
                Zone(domain_id=domain_id, dname=dname,)

        if options['cname']:
            gen_CNAME()

        print map(lambda x: len(x.objects.all()), \
                [Domain, AddressRecord, PTR, SOA, MX, \
                CNAME, Nameserver, StaticInterface])
