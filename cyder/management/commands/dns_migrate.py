#! /usr/bin/python

from datetime import datetime
from optparse import make_option
from sys import stderr

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.conf import settings

from cyder.base.eav.models import Attribute
from cyder.base.utils import get_cursor
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System, SystemAV
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.models import View
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.utils import ensure_domain
from .lib.utilities import (clean_mac, ip2long, long2ip, fix_attr_name,
                           range_usage_get_create, get_label_domain_workaround,
                           ensure_domain_workaround)

public, _ = View.objects.get_or_create(name="public")
private, _ = View.objects.get_or_create(name="private")

BAD_DNAMES = ['', '.', '_']


cursor, _ = get_cursor('maintain_sb')


def get_delegated():
    global delegated_dnames
    if delegated_dnames is None:
        print 'Fetching delegated domain names...'

        sql = ("SELECT domain.name FROM maintain_sb.domain "
               "INNER JOIN maintain_sb.nameserver "
               "ON domain.id=nameserver.domain "
               "WHERE %s")
        where = ' and '.join(["nameserver.name != '%s'" % ns
                              for ns in settings.NONDELEGATED_NS])
        cursor.execute(sql % where)
        results = [i for (i,) in cursor.fetchall()]

        delegated_dnames = set(results)
    return delegated_dnames


delegated_dnames = None


class Zone(object):

    def __init__(self, domain_id=None, dname=None, soa=None,
                 gen_recs=True, secondary=False):
        self.domain_id = domain_id
        self.dname = self.get_dname() if dname is None else dname
        self.dname = self.dname.lower()
        self.domain = None

        if gen_recs:
            try:
                self.domain = Domain.objects.get(name=self.dname)
            except Domain.DoesNotExist:
                print "WARNING: Domain %s does not exist." % self.dname
                return

            if self.dname in settings.SECONDARY_ZONES or secondary:
                print ("WARNING: Domain %s is a secondary, so its records "
                       "will not be migrated." % self.dname)
                secondary = True
                self.gen_static(simulate_delegated=True)
                self.gen_AR(reverse_only=True)
            else:
                if self.dname in get_delegated():
                    self.domain.soa = self.gen_SOA() or soa
                    if not self.domain.soa:
                        print ("WARNING: Could not migrate domain %s; no SOA"
                               % self.domain.name)
                        self.domain.delete()
                        return
                    else:
                        self.domain.delegated = True
                        print "%s has been marked as delegated." % self.dname
                        self.domain.save()

                if self.domain_id is not None:
                    # XXX: if SOA is created before AR and NS, then
                    # creating glue will raise an error. However,
                    # when creating delegated domains, an SOA is needed
                    if self.dname not in get_delegated():
                        self.gen_MX()
                        self.gen_static()
                        self.gen_AR()
                    else:
                        self.gen_static(simulate_delegated=True)
                        self.gen_AR(reverse_only=True)
                    self.gen_NS()
                    if self.dname not in get_delegated():
                        self.domain.soa = self.gen_SOA() or soa

        else:
            self.domain = self.gen_domain()
            if not self.domain:
                return
            self.domain.save()

        if self.domain:
            master_domain = self.domain.master_domain
            if master_domain and master_domain.delegated:
                raise Exception("Whoa dude %s has a delegated master"
                                % self.domain.name)

        if self.domain and self.domain_id is not None:
            self.walk_zone(gen_recs=gen_recs, secondary=secondary)

    def gen_SOA(self):
        """Generates an SOA record object if the SOA record exists.

        :uniqueness: primary, contact, refresh, retry, expire, minimum, comment
        """
        if self.domain_id is None:
            return None

        cursor.execute("SELECT primary_master, hostmaster, refresh, "
                       "retry, expire, ttl "
                       "FROM soa "
                       "WHERE domain = %s" % self.domain_id)
        record = cursor.fetchone()

        if record:
            primary, contact, refresh, retry, expire, minimum = record
            primary, contact = primary.lower(), contact.lower()

            try:
                soa = SOA.objects.get(root_domain=self.domain)
            except SOA.DoesNotExist:
                soa = SOA()

            soa.primary = primary
            soa.contact = contact
            soa.refresh = refresh
            soa.retry = retry
            soa.expire = expire
            soa.minimum = minimum
            soa.root_domain = self.domain
            soa.description = ''
            soa.save()

            return soa
        else:
            master_domain = self.domain.master_domain
            if master_domain and master_domain.soa:
                soa = master_domain.soa
            else:
                print "WARNING: No SOA exists for %s." % self.domain.name
                return None

        return soa

    def gen_domain(self):
        """Generates a Domain object for this Zone from a hostname.

        :uniqueness: domain
        """
        if not (self.dname in BAD_DNAMES):
            try:
                domain = ensure_domain(name=self.dname, force=True,
                                       update_range_usage=False)
                domain.clean()
                domain.save()
                return domain
            except ValidationError, e:
                print "Could not migrate domain %s: %s" % (self.dname, e)
                return None
        else:
            print "Did not migrate %s because it is blacklisted." % self.dname

    def gen_MX(self):
        """Generates the MX Record objects related to this zone's domain.

        .. note::
            Where multiple records with different ttls exist, only the
            first is kept.

        :uniqueness: label, domain, server, priority
        """
        cursor.execute("SELECT zone_mx.name, server, priority, ttl, "
                       "enabled, zone.name FROM zone_mx "
                       "JOIN zone ON zone_mx.zone = zone.id "
                       "WHERE domain = '%s';" % self.domain_id)

        for (name, server, priority, ttl,
                enabled, zone) in cursor.fetchall():
            name, server = name.lower(), server.lower()
            if MX.objects.filter(label=name,
                                 domain=self.domain,
                                 server=server,
                                 priority=priority).exists():
                print "Ignoring MX %s; MX already exists." % server
                continue

            ctnr = self.ctnr_from_zone_name(zone, 'MX')
            if ctnr is None:
                continue

            try:
                mx, _ = MX.objects.get_or_create(label=name,
                                                 domain=self.domain,
                                                 server=server,
                                                 priority=priority,
                                                 ttl=ttl, ctnr=ctnr)
                if enabled:
                    mx.views.add(public)
                    mx.views.add(private)
            except ValidationError, e:
                stderr.write("Error generating MX. %s\n" % e)

    def gen_static(self, simulate_delegated=False):
        """
        Generates the Static Interface objects related to this zone's domain.

        .. note::
            Every static interface needs a system.

        :System uniqueness: hostname, mac, ip_str

        :StaticInterface uniqueness: hostname, mac, ip_str
        """
        from dhcp_migrate import migrate_zones

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

        keys = ("host.id", "ip", "host.name", "zone.name", "workgroup",
                "enabled", "ha", "zone", "type", "os", "location",
                "department", "serial", "other_id", "purchase_date",
                "po_number", "warranty_date", "owning_unit", "user_id",
                "last_seen", "expire", "ttl", "last_update")

        sql = ("SELECT %s FROM host JOIN zone ON host.zone = zone.id "
               "WHERE ip != 0 AND domain = '%s';" %
               (", ".join(keys), self.domain_id))

        cursor.execute(sql)
        for values in cursor.fetchall():
            items = dict(zip(keys, values))
            name = items['host.name']

            if simulate_delegated:
                print ("WARNING: Did not migrate host %s because it is in a "
                       "delegated or secondary zone." % name)
                continue

            ctnr = self.ctnr_from_zone_name(items['zone.name'])
            if ctnr is None:
                continue

            enabled = bool(items['enabled'])
            dns_enabled, dhcp_enabled = enabled, enabled
            ip = items['ip']
            ha = items['ha']
            if ip == 0:
                continue

            if len(ha) != 12 or ha == '0' * 12:
                ha = ""

            if ha == "":
                dhcp_enabled = False

            # check for duplicate
            static = StaticInterface.objects.filter(
                label=name, mac=(clean_mac(ha) or None), ip_str=long2ip(ip))
            if static:
                stderr.write("Ignoring host %s: already exists.\n"
                             % items['host.id'])
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

            last_seen = items['last_seen'] or None
            if last_seen:
                last_seen = datetime.fromtimestamp(last_seen)

            static = StaticInterface(
                label=name, domain=self.domain, mac=(clean_mac(ha) or None),
                system=system, ip_str=long2ip(ip), ip_type='4',
                workgroup=w, ctnr=ctnr, ttl=items['ttl'],
                dns_enabled=dns_enabled, dhcp_enabled=dhcp_enabled,
                last_seen=last_seen)

            # create static interface
            try:
                static.save(update_range_usage=False)
            except ValidationError as e:
                fqdn = ".".join((name, self.domain.name))
                try:
                    static.dhcp_enabled = False
                    static.dns_enabled = dns_enabled
                    static.save(update_range_usage=False)
                    stderr.write('WARNING: Static interface {} has '
                                 'been disabled: '.format(fqdn))
                    stderr.write('{}\n'.format(e))
                except ValidationError as e:
                    stderr.write('WARNING: Could not create the static '
                                 'interface {}: '.format(fqdn))
                    stderr.write('{}\n'.format(e))
                    static = None
                    system.delete()

            if static:
                static.views.add(public)
                static.views.add(private)

    def gen_AR(self, reverse_only=False):
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

        cursor.execute("SELECT ip, hostname, type, zone.name, enabled "
                       "FROM pointer JOIN zone ON pointer.zone = zone.id "
                       "WHERE hostname LIKE '%%.%s';" % name)
        for ip, hostname, ptr_type, zone, enabled, in cursor.fetchall():
            hostname = hostname.lower()
            label, dname = hostname.split('.', 1)
            temp_reverse_only = True if dname != name else False

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

            ctnr = self.ctnr_from_zone_name(zone, 'AR/PTR')
            if ctnr is None:
                continue

            if (ptr_type == 'forward' and not reverse_only
                    and not temp_reverse_only):
                if AddressRecord.objects.filter(
                        fqdn=hostname, ip_str=long2ip(ip)).exists():
                    continue

                try:
                    arec, _ = range_usage_get_create(
                        AddressRecord, label=label, domain=self.domain,
                        ip_str=long2ip(ip), ip_type='4', ctnr=ctnr)
                except ValidationError, e:
                    print "Could not migrate AR %s: %s" % (hostname, e)
                    continue

                if enabled:
                    arec.views.add(public)
                    arec.views.add(private)

            if ptr_type == 'reverse':
                if not PTR.objects.filter(ip_str=long2ip(ip)).exists():
                    ptr = PTR(fqdn=hostname, ip_str=long2ip(ip),
                              ip_type='4', ctnr=ctnr)

                    # PTRs need to be cleaned independently of saving
                    # (no get_or_create)
                    try:
                        ptr.full_clean()
                    except ValidationError, e:
                        print "Could not migrate PTR %s: %s" % (ptr.ip_str, e)
                        continue

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
        for pk, name, _, _ in cursor.fetchall():
            name = name.lower()
            try:
                ns, _ = Nameserver.objects.get_or_create(domain=self.domain,
                                                         server=name)
                ns.views.add(public)
                ns.views.add(private)
            except ValidationError, e:
                stderr.write("Error generating NS %s. %s\n" % (pk, e))

    def walk_zone(self, gen_recs=True, secondary=False):
        """
        Recursively traverses the domain tree, creating Zone objects and
        migrating related DNS objects along the way.

        .. note::
            Child domains will inherit this domain's SOA if they do not have
            their own.
        """
        if self.dname in get_delegated():
            print "%s is delegated, so no children to create." % self.dname
            return

        sql = ("SELECT id, name "
               "FROM domain "
               "WHERE master_domain = %s;" % self.domain_id)
        cursor.execute(sql)
        for child_id, child_name in cursor.fetchall():
            child_name = child_name.lower()
            Zone(child_id, child_name, self.domain.soa, gen_recs=gen_recs,
                 secondary=secondary)

    def get_dname(self):
        """
        Finds a domain name for this Zone's domain id.
        """
        cursor.execute('SELECT * FROM domain WHERE id = %s;' % self.domain_id)
        _, dname, _, _ = cursor.fetchone()
        dname = dname.lower()
        return dname

    @staticmethod
    def ctnr_from_zone_name(zone, obj_type="Object"):
        from dhcp_migrate import clean_zone_name
        zone = clean_zone_name(zone)
        try:
            ctnr = Ctnr.objects.get(name=zone)
        except Ctnr.DoesNotExist:
            print ("%s migration error; ctnr %s does not exist." %
                   (obj_type, zone))
            ctnr = None

        return ctnr

    @staticmethod
    def ctnr_from_zone_id(zone_id):
        from dhcp_migrate import maintain_find_zone
        return maintain_find_zone(zone_id)


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
    sql = ("SELECT zone_cname.id, zone_cname.server, zone_cname.name, "
           "zone_cname.enabled, zone.name, domain.name FROM zone_cname "
           "JOIN zone ON zone_cname.zone = zone.id "
           "JOIN domain ON zone_cname.domain = domain.id")
    cursor.execute(sql)

    for pk, server, name, enabled, zone, dname in cursor.fetchall():
        server, name = server.lower(), name.lower()
        dname = dname.lower()
        server = server.strip('.')

        fqdn = ".".join([name, dname])
        name, dname = fqdn.split(".", 1)

        if Domain.objects.filter(name=fqdn).exists():
            domain = Domain.objects.get(name=fqdn)
            name = ""
        elif Domain.objects.filter(name=dname).exists():
            domain = Domain.objects.get(name=dname)
        else:
            _, domain = get_label_domain_workaround(fqdn)

        if server == ".".join([name, domain.name]):
            # In maintain, at least one CNAME is a loop: biosys.bioe.orst.edu
            print "Ignoring CNAME %s: Is a loop." % server
            continue

        if CNAME.objects.filter(label=name, domain=domain).exists():
            c = CNAME.objects.get(label=name, domain=domain)
            if c.target != server:
                print ("ALERT: Conflicting CNAME with fqdn %s already exists."
                       % fqdn)
            continue

        ctnr = Zone.ctnr_from_zone_name(zone, 'CNAME')
        if ctnr is None:
            continue

        fqdn = "%s.%s" % (name, domain.name)
        fqdn = fqdn.lower().strip('.')
        if ctnr not in domain.ctnr_set.all():
            print "CNAME %s has mismatching container for its domain." % fqdn
            continue

        cn = CNAME(label=name, domain=domain, target=server, ctnr=ctnr)
        cn.set_fqdn()
        dup_ptrs = PTR.objects.filter(fqdn=cn.fqdn)
        if dup_ptrs:
            print "Removing duplicate PTR for %s" % cn.fqdn
            dup_ptrs.delete(update_range_usage=False)

        # CNAMEs need to be cleaned independently of saving (no get_or_create)
        try:
            cn.full_clean()
            cn.save()
            if enabled:
                cn.views.add(public)
                cn.views.add(private)
        except ValidationError, e:
            print "Error for CNAME %s.%s: %s" % (name, domain.name, e)


def gen_reverses():
    print "Creating reverse domains."
    add_pointers_manual()
    Domain.objects.get_or_create(name='arpa', is_reverse=True)
    Domain.objects.get_or_create(name='in-addr.arpa', is_reverse=True)

    gen_reverse_soa()


def gen_reverse_soa():
    public = View.objects.get(name="public")
    private = View.objects.get(name="private")

    for rname in settings.REVERSE_SOAS:
        if not rname.endswith(".arpa"):
            rname = rname + ".in-addr.arpa"

        print "Creating reverse SOA %s" % rname
        dom = ensure_domain_workaround(rname)
        ns1, _ = Nameserver.objects.get_or_create(domain=dom,
                                                  server="ns1.oregonstate.edu")
        ns2, _ = Nameserver.objects.get_or_create(domain=dom,
                                                  server="ns2.oregonstate.edu")
        SOA.objects.get_or_create(root_domain=dom,
                                  primary="ns1.oregonstate.edu",
                                  contact="hostmaster.oregonstate.edu")

        ns1.views.add(public)
        ns2.views.add(public)
        ns1.views.add(private)
        ns2.views.add(private)


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
    sql = 'SELECT id FROM zone WHERE name LIKE "zone.nws"'
    cursor.execute(sql)
    zone_id = cursor.fetchone()[0]
    for opt in opts:
        (ip, hn, ptype) = opt
        ip = ip2long(ip)
        sql = ('SELECT count(*) FROM pointer WHERE ip = %s AND hostname = "%s"'
               'AND type = "%s AND zone = %s"' % (ip, hn, ptype, zone_id))
        cursor.execute(sql)
        exists = cursor.fetchone()[0]
        if not exists:
            sql = ('INSERT INTO pointer (ip, hostname, type, zone) '
                   'VALUES (%s, "%s", "%s", %s)' % (ip, hn, ptype, zone_id))
            cursor.execute(sql)


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
        if options['delete']:
            if options['dns']:
                delete_DNS()
            if options['cname']:
                delete_CNAME()

        if options['dns']:
            gen_DNS(options['skip'])

        if options['cname']:
            gen_CNAME()

        if options['domains']:
            gen_domains_only()
