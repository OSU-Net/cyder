#! /usr/bin/python
from optparse import OptionParser
import pdb

import chili_manage
import fix_maintain, maintain_dump
from utilities import get_cursor, long2ip, clean_mac

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
        cursor.execute("SELECT * FROM soa WHERE domain = '%s';" % self.domain_id)
        records = cursor.fetchall()

        if records:
            _, _, primary, contact, refresh, retry, expire, minimum, _ = records[0]
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
        if self.dname in BAD_DNAMES or 'in-addr.arpa' in self.dname:
            return None

        return ensure_domain(name = self.dname, force=True)


    def gen_MX(self):
        cursor.execute("SELECT * FROM zone_mx WHERE domain = '%s';" % self.domain_id)
        records = cursor.fetchall()
        for _, name, _, server, priority, ttl, _, _ in records:
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
        cursor.execute("SELECT * FROM host WHERE ip != 0 AND domain = '%s';" % self.domain_id)
        records = cursor.fetchall()
        for sysid, ip, dynamic_range, name, sysdomid, ha, systype, os, location, \
                serial, last_seen, other_id, workgroup, enabled, bandwidth_rate, \
                expire, ttl, last_update, zone, purchase_date, po_number, \
                warranty_date, owning_unit, user_id, department in records:

            if ip == 0:
                continue
            if len(ha) != 12:
                ha = "0" * 12
            # TODO: Make systems unique by hostname, ip, mac tuple
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
                static.update_attrs()
                static.full_clean()
                static.save()


    def gen_AR(self):
        name = self.domain.name
        cursor.execute("SELECT * FROM pointer WHERE hostname LIKE '%%.%s';" % name)
        records = cursor.fetchall()
        for _, ip, hostname, ptr_type, _, _, enabled in records:
            hostname = hostname.split('.')
            label = hostname[0]
            dname = '.'.join(hostname[1:])

            if dname.lower() != name.lower():
                continue

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
                    ptr.full_clean()
                    ptr.save()


    def gen_NS(self):
        cursor.execute("SELECT * FROM nameserver WHERE domain='%s';" % self.domain_id)
        records = cursor.fetchall()
        for _, name, _, _ in records:
            ns, _ = Nameserver.objects.get_or_create(domain = self.domain, server = name)


    def walk_zone(self):
        sql = 'SELECT * FROM domain WHERE name NOT LIKE "%%.in-addr.arpa" AND ' + \
                'master_domain = %s;' % self.domain_id
        cursor.execute(sql)
        subdomains = cursor.fetchall()
        for child_id, child_name, _, _ in subdomains:
            Zone(child_id, child_name, self.domain.soa)


    def get_dname(self):
        cursor.execute('SELECT * FROM domain WHERE id = %s;' % self.domain_id)
        _, dname, _, _ = cursor.fetchall()[0]
        return dname

#TODO: Cleanup functions for leftover objects to migrate (static interfaces and PTRs)

def gen_CNAME():
    cursor.execute("SELECT * FROM zone_cname WHERE name NOT LIKE '%.%';")
    records = cursor.fetchall()
    for _, server, name, domain_id, ttl, zone, _ in records:
        cursor.execute("SELECT name FROM domain WHERE id = '%s'" % domain_id)
        dname = cursor.fetchone()
        if not dname:
            continue
        dname = dname[0]

        if not Domain.objects.filter(name = dname).exists():
            continue

        fqdn = ".".join([name, dname])
        if Domain.objects.filter(name = fqdn).exists():
            domain = Domain.objects.get(name = fqdn)
            name = ""
        else:
            domain = Domain.objects.get(name = dname)

        cn = CNAME(label = name, domain = domain, target = server)
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

        reverses = ['193.128', '10', '211.140', '201.199', '32.198', '232.111', \
                    '127', '131.80.252.131', '5.68.98.207']

        for i in reverses:
            if '.' in i:
                reverses.append(i.split('.', 1)[1])

        reverses.reverse()

        for i in reverses:
            print "%s.in-addr.arpa" % i
            Domain.objects.get_or_create(name = "%s.in-addr.arpa" % i, is_reverse = True)

        cursor.execute('SELECT * FROM domain WHERE master_domain = 0')
        records = cursor.fetchall()
        for domain_id, dname, _, _ in records:
            if dname == "edu":
                pass
            print "Creating %s zone." % dname
            Zone(domain_id = domain_id, dname = dname,)

    if options.cname:
        gen_CNAME()

    domains = Domain.objects.all()
    ars = AddressRecord.objects.all()
    ptrs = PTR.objects.all()
    soas = SOA.objects.all()
    mxs = MX.objects.all()
    nss = Nameserver.objects.all()
    cnames = CNAME.objects.all()
    statics = StaticInterface.objects.all()

    print map(lambda x: len(x), [domains, ars, ptrs, soas, mxs, cnames, nss, statics])

    pdb.set_trace()
