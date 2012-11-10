#! /usr/bin/python
from optparse import OptionParser
from ConfigParser import ConfigParser
import pdb

import chili_manage
import fix_maintain, maintain_dump
from utilities import get_cursor, long2ip, ip2long, clean_mac, config

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from cyder.core.systems.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface

from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.soa.models import SOA
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.cname.models import CNAME

from cyder.cydns.utils import ensure_label_domain, ensure_domain

BAD_DNAMES = ['', '.', '_']

cursor = get_cursor('maintain_sb')

class Zone(object):
    def __init__(self, domain_id = None, dname = None, soa = None):
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
        """
        Generates an SOA record object if the SOA record exists.

        :uniqueness: primary, contact, refresh, retry, expire, minimum, comment
        """
        cursor.execute("SELECT * FROM soa WHERE domain = '%s';" % self.domain_id)
        record = cursor.fetchone()

        if record:
            _, _, primary, contact, refresh, retry, expire, minimum, _ = record
            soa, _ = SOA.objects.get_or_create(primary = primary,
                                               contact = contact,
                                               refresh = refresh,
                                               retry = retry,
                                               expire = expire,
                                               minimum = minimum,
                                               comment = "SOA for %s zone" % self.dname)
            return soa
        else:
            return None


    def gen_domain(self):
        """
        Generates a Domain object for this Zone from a hostname.

        :uniqueness: domain
        """
        if self.dname in BAD_DNAMES or 'in-addr.arpa' in self.dname:
            return None

        return ensure_domain(name = self.dname, force=True)


    def gen_MX(self):
        """
        Generates the MX Record objects related to this zone's domain.

        .. note::
            Where multiple records with different ttls exist, only the first is kept.

        :uniqueness: label, domain, server, priority
        """
        cursor.execute("SELECT * FROM zone_mx WHERE domain = '%s';" % self.domain_id)
        for _, name, _, server, priority, ttl, _, _ in cursor.fetchall():
            if MX.objects.filter(label = name,
                                 domain = self.domain,
                                 server = server,
                                 priority = priority).exists():
                continue

            try:
                mx, _ = MX.objects.get_or_create(label = name,
                                                 domain = self.domain,
                                                 server = server,
                                                 priority = priority,
                                                 ttl = ttl)
            except ValidationError:
                pdb.set_trace()


    def gen_static(self):
        """
        Generates the Static Interface objects related to this zone's domain.

        .. note::
            Every static interface needs a system.

        :System uniqueness: hostname, mac, ip_str

        :StaticInterface uniqueness: hostname, mac, ip_str
        """
        cursor.execute("SELECT * FROM host WHERE ip != 0 AND domain = '%s';" % self.domain_id)
        for sysid, ip, dynamic_range, name, sysdomid, ha, systype, os, location, \
                serial, last_seen, other_id, workgroup, enabled, bandwidth_rate, \
                expire, ttl, last_update, zone, purchase_date, po_number, \
                warranty_date, owning_unit, user_id, department in cursor.fetchall():

            if ip == 0:
                continue

            if len(ha) != 12:
                ha = "0" * 12

            # TODO: Make systems unique by hostname, ip, mac tuple
            # TODO: Add key-value attributes to system objects.

            system, _ = System.objects.get_or_create(hostname = name)

            if not StaticInterface.objects.filter(label = name,
                                                  mac = clean_mac(ha),
                                                  ip_str = long2ip(ip)).exists():
                static = StaticInterface(label = name,
                                         domain = self.domain,
                                         mac = clean_mac(ha),
                                         system = system,
                                         ip_str = long2ip(ip),
                                         ip_type = '4')
                # Static Interfaces need to be cleaned independently of saving
                # (no get_or_create)
                static.full_clean()
                static.save()


    def gen_AR(self):
        """
        Generates the Address Record and PTR objects related to this zone's domain.

        .. note::
            Some AddressRecords may need to be added to the pointer table in MAINTAIN
            for successful migration, for example,
            cob-dc81 and cob-dc82.bus.oregonstate.edu

        .. note::
            AddressRecords/PTRs with the same ip as a StaticInterface can't coexist,
            so if a StaticInterface with the same ip exists, it has priority.

        :AddressRecord uniqueness: label, domain, ip_str, ip_type

        :PTR uniqueness: name, ip_str, ip_type
        """
        name = self.domain.name
        cursor.execute("SELECT * FROM pointer WHERE hostname LIKE '%%.%s';" % name)
        for _, ip, hostname, ptr_type, _, _, enabled in cursor.fetchall():

            label, dname = hostname.split('.', 1)

            if StaticInterface.objects.filter(ip_str = long2ip(ip)).exists():
                continue

            if ptr_type == 'forward':
                arec, _ = AddressRecord.objects.get_or_create(label = label,
                                                              domain = self.domain,
                                                              ip_str = long2ip(ip),
                                                              ip_type = '4')

            elif ptr_type == 'reverse':
                if not PTR.objects.filter(name = name, ip_str = long2ip(ip)).exists():
                    ptr = PTR(name = name, ip_str = long2ip(ip), ip_type = '4')

                    # PTRs need to be cleaned independently of saving (no get_or_create)
                    ptr.full_clean()
                    ptr.save()


    def gen_NS(self):
        """
        Generates the Nameserver objects related to this zone's domain.

        :uniqueness: domain, server name
        """
        cursor.execute("SELECT * FROM nameserver WHERE domain='%s';" % self.domain_id)
        for _, name, _, _ in cursor.fetchall():
            try:
                ns, _ = Nameserver.objects.get_or_create(domain = self.domain, server = name)
            except ValidationError:
                pdb.set_trace()


    def walk_zone(self):
        """
        Recursively traverses the domain tree, creating Zone objects and migrating
        related DNS objects along the way.

        .. note::
            Child domains will inherit this domain's SOA if they do not have
            their own.
        """
        sql = 'SELECT * FROM domain WHERE name NOT LIKE "%%.in-addr.arpa" AND ' + \
                'master_domain = %s;' % self.domain_id
        cursor.execute(sql)
        for child_id, child_name, _, _ in cursor.fetchall():
            Zone(child_id, child_name, self.domain.soa)


    def get_dname(self):
        """
        Finds a domain name for this Zone's domain id.
        """
        cursor.execute('SELECT * FROM domain WHERE id = %s;' % self.domain_id)
        _, dname, _, _ = cursor.fetchone()
        return dname

    #TODO: Cleanup functions for leftover objects to migrate (static interfaces and PTRs)


def gen_CNAME():
    """
    Migrates CNAME objects.

    .. note::
        Run this only after migrating other DNS objects for every zone.

    .. note::
        Because MAINTAIN is totally messed up, some hostnames in the CNAME table
        have ``.``'s in them, so the fully qualified domain name is created first,
        then the label is stripped off of the front of that.

    .. note::
        If the fully qualified domain name of the label + domain name already exists as
        a domain object, that object becomes the alias and the label prefix is set to
        the empty string. Otherwise, the alias is the label + domain name.

    :uniqueness: label, domain, target
    """
    cursor.execute("SELECT * FROM zone_cname;")
    for _, server, name, domain_id, ttl, zone, _ in cursor.fetchall():
        cursor.execute("SELECT name FROM domain WHERE id = '%s'" % domain_id)
        dname, = cursor.fetchone()
        if not dname:
            continue

        fqdn = ".".join([name, dname])
        name, dname = fqdn.split(".", 1)

        if Domain.objects.filter(name = fqdn).exists():
            domain = Domain.objects.get(name = fqdn)
            name = ""
        elif Domain.objects.filter(name = dname).exists():
            domain = Domain.objects.get(name = dname)
        else:
            continue

        cn = CNAME(label = name, domain = domain, target = server)
        # CNAMEs need to be cleaned independently of saving (no get_or_create)
        cn.full_clean()
        cn.save()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-D", "--dump", dest="dump", default=False, \
            action="store_true", help="Get a fresh dump of MAINTAIN.")
    parser.add_option("-f", "--fix", dest="fix", default=False, \
            action="store_true", help="Fix MAINTAIN.")
    parser.add_option("-d", "--dns", dest="dns", default=False, \
            action="store_true", help="Migrate DNS objects.")
    parser.add_option("-c", "--cname", dest="cname", default=False, \
            action="store_true", help="Migrate CNAMEs.")
    parser.add_option("-X", "--delete", dest="delete", default=False, \
            action="store_true", help="Delete old objects.")
    (options, args) = parser.parse_args()

    if options.dump:
        maintain_dump.main()
        for option in config.options("pointer-include"):
            (ip, hn, ptype) = config.get("pointer-include", option).split()
            x = (ip2long(ip), hn, ptype)
            sql = 'INSERT INTO pointer (ip, hostname, type) VALUES (%s, "%s", "%s")' % x
            cursor.execute(sql)

    if options.delete:
        if options.dns:
            Domain.objects.all().delete()
            AddressRecord.objects.all().delete()
            SOA.objects.all().delete()
            MX.objects.all().delete()
            Nameserver.objects.all().delete()
            PTR.objects.all().delete()
            System.objects.all().delete()
            StaticInterface.objects.all().delete()

        if options.cname:
            CNAME.objects.all().delete()

    if options.fix:
        fix_maintain.main()

    if options.dns:
        Domain.objects.get_or_create(name = 'arpa', is_reverse = True)
        Domain.objects.get_or_create(name = 'in-addr.arpa', is_reverse = True)

        reverses = config.get("reverse-domains", "ips").split()

        for i in reverses:
            if '.' in i:
                reverses.append(i.split('.', 1)[1])

        reverses.reverse()

        for i in reverses:
            print "%s.in-addr.arpa" % i
            Domain.objects.get_or_create(name = "%s.in-addr.arpa" % i, is_reverse = True)

        cursor.execute('SELECT * FROM domain WHERE master_domain = 0')
        for domain_id, dname, _, _ in cursor.fetchall():
            if dname == "edu":
                continue
            print "Creating %s zone." % dname
            Zone(domain_id = domain_id, dname = dname,)

    if options.cname:
        gen_CNAME()

    print map(lambda x: len(x.objects.all()), [Domain, AddressRecord, PTR, SOA, MX, CNAME, Nameserver, StaticInterface])

    pdb.set_trace()
