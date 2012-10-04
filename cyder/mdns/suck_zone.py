from cyder.truth.models import Truth

from cyder.mdns.inventory_build import inventory_build_sites
from cyder.mdns.svn_build import collect_svn_zones, collect_rev_svn_zones
from cyder.mdns.svn_build import get_forward_svn_sites_changed
from cyder.mdns.svn_build import get_reverse_svn_sites_changed
from cyder.mdns.build_nics import *
from cyder.mdns.utils import *
import ipaddr
from cyder.systems.models import ScheduledTask
from django.conf import settings
from django.conf import settings
from django.conf import settings
from django.conf import settings
from cyder.core.network.models import Network
from cyder.core.interface.static_intr.models import StaticInterface

from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.cname.models import CNAME
from cyder.mozdns.domain.models import Domain
from cyder.mozdns.mx.models import MX
from cyder.mozdns.nameserver.models import Nameserver
from cyder.mozdns.ptr.models import PTR
from cyder.mozdns.soa.models import SOA
from cyder.mozdns.srv.models import SRV
from cyder.mozdns.tests.view_tests import random_label
from cyder.mozdns.txt.models import TXT
from cyder.mozdns.domain.utils import *
from cyder.mozdns.ip.utils import ip_to_domain_name

import os.path
import pprint
import re

DEBUG = 3
DO_DEBUG = False

pp = pprint.PrettyPrinter(indent=2)


def guess(nic):
    """
    Search and Guess which object in the database is supposed to correspond
    with this nic.
    """
    log("Attempting to find records for nic {0}".format(nic))
    if len(nic.ips) != 1:
        log("nic {0} system {1} doesn't have the right amount of ip's."
            .format(nic, print_system(nic.system)), ERROR)
        return None, None, None

    addrs = AddressRecord.objects.filter(ip_str=nic.ips[0])
    ptrs = PTR.objects.filter(ip_str=nic.ips[0])
    intrs = StaticInterface.objects.filter(ip_str=nic.ips[0])

    # This script probably put this info here.
    intr_certainty = False
    exintr = None
    for intr in intrs:
        if intr.fqdn.startswith(nic.hostname):
            log("Found Interface {0} that matches nic.ip {1} and partially "
                "nic.hostname {2}".format(intr, nic.ips[0], nic.hostname))
            intr_certainty = True
            if exintr:
                log("Found another Interface {0} that looks a lot like {1}, "
                    "while searching for nic.ip {2} and nic.hostname {3}."
                    "{2}".format(intr, exintr, nic.ips[0], nic.hostname),
                    WARNING)
            exintr = intr

    # Ok, we have records with the same ip. Look for name matches.
    addr_certainty = False
    exaddr = None
    for addr in addrs:
        if addr.fqdn.startswith(nic.hostname):
            # The ip patches and the hostname of the nic lines up with the
            # name on the Address Record.
            addr_certainty = True
            log("Found A {0} that matches nic.ip {1} and partially "
                "nic.hostname {2}".format(addr, nic.ips[0], nic.hostname))
            if exaddr:
                log("Found another A record {0} that looks a lot like {1}, "
                    "while searching for nic.ip {2} and nic.hostname {3}."
                    "{2}".format(addr, exaddr, nic.ips[0], nic.hostname),
                    WARNING)
            exaddr = addr

    # Search in the ptr space.
    ptr_certainty = False
    exptr = None
    for ptr in ptrs:
        if ptr.name.startswith(nic.hostname):
            log("Found PTR {0} that matches nic.ip {1} and partially "
                "nic.hostname {2}".format(ptr, nic.ips[0],
                                          nic.hostname))
            ptr_certainty = True
            if exptr:
                log("Found another PTR record {0} that looks a lot like {1}, "
                    "while searching for nic.ip {2} and nic.hostname {3}."
                    "{2}".format(addr, exaddr, nic.ips[0], nic.hostname),
                    WARNING)
            exptr = ptr

    return exintr, exaddr, exptr


def populate_interface():
    matches = []
    misses = []
    for nic in get_nic_objs():
        log("=" * 20)
        intr, addr, ptr = guess(nic)
        if not (intr or addr or ptr):
            log("Epic failure. Couldn't find anything for nic.{0}.{1} "
                "{2}".format(nic.primary, nic.alias,
                             print_system(nic.system)), ERROR)
            misses.append(nic)
        else:
            log("SUCCESS: Guess Interface:{0} AddressRecord:{1} PTR:{2}".format(intr, addr, ptr))
            matches.append((nic, intr, addr, ptr))

    log("-+" * 80)
    log("===== Misses =====")
    for nic in misses:
        log(str(nic))
    log("===== Matches =====")
    for nic, intr, addr, ptr in matches:
        log("Nic: {1} Interface:{0} AddressRecord:{1} PTR:{2}".format(
            nic, intr, addr, ptr))
    log("Misses: " + str(len(misses)))
    log("Matches: " + str(len(matches)))


def create_domain(name, ip_type=None, delegated=False):
    if ip_type is None:
        ip_type = '4'
    if name in ('arpa', 'in-addr.arpa', 'ipv6.arpa'):
        pass
    else:
        name = ip_to_domain_name(name, ip_type=ip_type)
    d = Domain.objects.get_or_create(name=name, delegated=delegated)
    return d


def populate_reverse_dns(rev_svn_zones):
    arpa = create_domain(name='arpa')
    i_arpa = create_domain(name='in-addr.arpa')
    i6_arpa = create_domain(name='ipv6.arpa')

    for site, data in rev_svn_zones.iteritems():
        site_path, more_data = data
        zone, records = more_data
        print "-" * 15 + " " + site

        for (name, ttl, rdata) in zone.iterate_rdatas('SOA'):
            print str(name) + " SOA " + str(rdata)
            exists = SOA.objects.filter(minimum=rdata.minimum,
                                        contact=rdata.rname.to_text(
                                        ).strip('.'),
                                        primary=rdata.mname.to_text(
                                        ).strip('.'),
                                        comment="SOA for {0}.in-addr.arpa".format(site))
            if exists:
                soa = exists[0]
            else:
                soa = SOA(serial=rdata.serial, minimum=rdata.minimum,
                          contact=rdata.rname.to_text().strip('.'),
                          primary=rdata.mname.to_text().strip('.'),
                          comment="SOA for {0}.in-addr.arpa".format(site))
                soa.clean()
                soa.save()
            name = name.to_text().replace('.IN-ADDR.ARPA.', '')
            domain_split = list(reversed(name.split('.')))
            for i in range(len(domain_split)):
                domain_name = domain_split[:i + 1]
                rev_name = ip_to_domain_name(
                    '.'.join(domain_name), ip_type='4')
                base_domain, created = Domain.objects.get_or_create(
                    name=rev_name)
            base_domain.soa = soa
            base_domain.save()
        for (name, ttl, rdata) in zone.iterate_rdatas('NS'):
            name = name.to_text().strip('.')
            name = name.replace('.IN-ADDR.ARPA', '')
            name = name.replace('.in-addr.arpa', '')
            print str(name) + " NS " + str(rdata)
            domain_name = '.'.join(list(reversed(name.split('.'))))
            domain = ensure_rev_domain(domain_name)
            ns, _ = Nameserver.objects.get_or_create(domain=domain,
                                                     server=rdata.target.to_text().strip('.'))
        for (name, ttl, rdata) in zone.iterate_rdatas('PTR'):
            ip_str = name.to_text().strip('.')
            ip_str = ip_str.replace('.IN-ADDR.ARPA', '')
            ip_str = ip_str.replace('.in-addr.arpa', '')
            ip_str = '.'.join(list(reversed(ip_str.split('.'))))
            fqdn = rdata.target.to_text().strip('.')
            if fqdn.startswith('unused'):
                print "Skipping " + ip_str + " " + fqdn
                continue
            if ip_str == '10.2.171.IN':
                log("Skipping 10.2.171.IN", WARNING)
                continue
            print str(name) + " PTR " + str(fqdn)
            ptr = PTR.objects.filter(name=fqdn, ip_str=ip_str, ip_type='4')
            if ptr:
                continue
            else:
                ptr = PTR(name=fqdn, ip_str=ip_str, ip_type='4')
                ptr.full_clean()
                ptr.save()

        """
        for (name, ttl, rdata) in zone.iterate_rdatas('CNAME'):
            name = name.to_text().strip('.')
            print str(name) + " CNAME " + str(rdata)
            rev_name = ip_to_domain_name(name, ip_type='4')
            exists_domain = Domain.objects.filter(name=rev_name)
            if exists_domain:
                label = ''
                domain = exists_domain[0]
            else:
                label = name.split('.')[0]
                domain_name = name.split('.')[1:]
                domain = ensure_domain('.'.join(domain_name))
            data = rdata.target.to_text().strip('.')

            if not CNAME.objects.filter(label = label, domain = domain,
                    data = data).exists():
                cn = CNAME(label = label, domain = domain,
                        data = data)
                cn.full_clean()
                cn.save()
        """


def ensure_rev_domain(name):
    parts = name.split('.')
    domain_name = ''
    for i in range(len(parts)):
        domain_name = domain_name + '.' + parts[i]
        domain_name = domain_name.strip('.')
        rev_name = ip_to_domain_name(domain_name, ip_type='4')
        domain, created = Domain.objects.get_or_create(name=
                                                       rev_name)
        if domain.master_domain and domain.master_domain.soa:
            domain.soa = domain.master_domain.soa
            domain.save()

    return domain


def populate_forward_dns(svn_zones):
    for site, data in svn_zones.iteritems():
        zone, records = data
        print "-" * 15 + " " + site

        for (name, ttl, rdata) in zone.iterate_rdatas('SOA'):
            print str(name) + " SOA " + str(rdata)
            exists = SOA.objects.filter(minimum=rdata.minimum,
                                        contact=rdata.rname.to_text(
                                        ).strip('.'),
                                        primary=rdata.mname.to_text().strip('.'), comment="SOA for"
                                        " {0}.mozilla.com".format(site))
            if exists:
                soa = exists[0]
            else:
                soa = SOA(serial=rdata.serial, minimum=rdata.minimum,
                          contact=rdata.rname.to_text().strip('.'),
                          primary=rdata.mname.to_text().strip('.'), comment="SOA for"
                          " {0}.mozilla.com".format(site))
                soa.clean()
                soa.save()
            domain_split = list(reversed(name.to_text().strip('.').split('.')))
            for i in range(len(domain_split)):
                domain_name = domain_split[:i + 1]
                base_domain, created = Domain.objects.get_or_create(name=
                                                                    '.'.join(list(reversed(domain_name))))
            base_domain.soa = soa
            base_domain.save()

        """
            Algo for creating names and domains.
            Get all names.
            Sort by number of labels, longest first.
            For each name:
                if exists_domain(name):
                    label = ''
                    domain = name
                else:
                    label = name.split('.')[0]
                    domain_name = name.split('.')[1:]
                    if domain_name exists:
                        domain = domain_name
                    else:
                        domain = create(domain_name)
        """
        # Create list
        names = []
        for (name, ttl, rdata) in zone.iterate_rdatas('A'):
            names.append((name.to_text().strip('.'), rdata))
        sorted_names = list(sorted(names, cmp=lambda n1, n2: -1 if
                                   len(n1[0].split('.')) > len(n2[0].split('.')) else 1))

        for name, rdata in sorted_names:
            print str(name) + " A " + str(rdata)
            exists_domain = Domain.objects.filter(name=name)
            if exists_domain:
                label = ''
                domain = exists_domain[0]
            else:
                label = name.split('.')[0]
                if label.find('unused') != -1:
                    continue
                parts = list(reversed(name.split('.')[1:]))
                domain_name = ''
                for i in range(len(parts)):
                    domain_name = parts[i] + '.' + domain_name
                    domain_name = domain_name.strip('.')
                    domain, created = Domain.objects.get_or_create(name=
                                                                   domain_name)
                    if domain.master_domain and domain.master_domain.soa:
                        domain.soa = domain.master_domain.soa
            a, _ = AddressRecord.objects.get_or_create(label=label,
                                                       domain=domain, ip_str=rdata.to_text(), ip_type='4')

        for (name, ttl, rdata) in zone.iterate_rdatas('NS'):
            name = name.to_text().strip('.')
            print str(name) + " NS " + str(rdata)
            domain = ensure_domain(name)
            ns, _ = Nameserver.objects.get_or_create(domain=domain,
                                                     server=rdata.target.to_text().strip('.'))
        for (name, ttl, rdata) in zone.iterate_rdatas('MX'):
            name = name.to_text().strip('.')
            print str(name) + " MX " + str(rdata)
            exists_domain = Domain.objects.filter(name=name)
            if exists_domain:
                label = ''
                domain = exists_domain[0]
            else:
                label = name.split('.')[0]
                domain_name = name.split('.')[1:]
                domain = ensure_domain(domain_name)
            priority = rdata.preference
            server = rdata.exchange.to_text().strip('.')
            mx, _ = MX.objects.get_or_create(label=label, domain=domain,
                                             server=server, priority=priority, ttl="3600")
        for (name, ttl, rdata) in zone.iterate_rdatas('CNAME'):
            name = name.to_text().strip('.')
            print str(name) + " CNAME " + str(rdata)
            exists_domain = Domain.objects.filter(name=name)
            if exists_domain:
                label = ''
                domain = exists_domain[0]
            else:
                label = name.split('.')[0]
                domain_name = name.split('.')[1:]
                domain = ensure_domain('.'.join(domain_name))
            data = rdata.target.to_text().strip('.')

            if not CNAME.objects.filter(label=label, domain=domain,
                                        data=data).exists():
                cn = CNAME(label=label, domain=domain,
                           data=data)
                cn.full_clean()
                cn.save()

is_generate1 = re.compile("^.*(\d+){(\+|-)(\d+),(\d+),(.)}.*$")
is_generate2 = re.compile("^.*(\d+){(\+|-?)(\d+)}.*$")
is_generate3 = re.compile("^.*(\d+){(\d+),(\d+),(.)}.*$")


def resolve_generate(name):
    g1 = is_generate1.match(name)
    g2 = is_generate2.match(name)
    g3 = is_generate3.match(name)
    if g1 or g2 or g3:
        log("Skipping {0}".format(name), WARNING)
        # TODO, expand this.
    if g1:
        log("Skipping {0}".format(name), WARNING)
        # TODO, expand this.
        pdb.set_trace()
        return False
    elif g2:
        log("Skipping {0}".format(name), WARNING)
        # TODO, expand this.
        pdb.set_trace()
        return False
    elif g3:
        log("Skipping {0}".format(name), WARNING)
        # TODO, expand this.
        return False
    return True


def ensure_domain(name):
    parts = list(reversed(name.split('.')))
    domain_name = ''
    for i in range(len(parts)):
        domain_name = parts[i] + '.' + domain_name
        domain_name = domain_name.strip('.')
        domain, created = Domain.objects.get_or_create(name=
                                                       domain_name)
        if domain.master_domain and domain.master_domain.soa:
            domain.soa = domain.master_domain.soa

    return domain


def build_reverse(sites_to_build, inv_reverse, rev_svn_zones):
    final_records = {}
    for network, interfaces in inv_reverse.items():
        network_path, svn_entries = rev_svn_zones[network]
        network_path, inv_entries = final_records.setdefault(network,
                                                             (network_path, set()))
        # TODO, rename inv_entries to something more descriptive.
        for intr in interfaces:
            name = intr.hostname + "."
            for ip in intr.ips:
                dnsip = ip_to_domain_name(ip)
                if (dnsip, name) in svn_entries:
                    log("System {0} (interface: {1}, {2}) has "
                        "conflict".format(intr.system, dnsip, name), INFO)
                else:
                    inv_entries.add((dnsip, name))

    log("=" * 10 + " Final DNS data", BUILD)
    for network, network_data in final_records.items():
        network_path, records = network_data
        # Inv entries are in (<'name'>, <'ip'>) form
        generate_reverse_inventory_data_file(network, records, network_path)


def build_forward(sites_to_build, inv_forward, svn_zones):

    final_records = {}
    for vlan_site, network, site_path in sites_to_build:
        network, inv_interfaces = inv_forward[vlan_site]
        vlan, site = vlan_site.split('.')
        # svn entries are [['pao1', 'ad', 'services' ...]

        # inv entires are [(IPv4Network('10.22.1.0/24'),
        # [<mdns.build_nics.Interface object at 0xab54250>]),...]

        # svn_entries are [('baz.bar.scl3.mozilla.com.', '10.22.85.212'),
        # ('foo.bar.scl3.mozilla.com.', '64.245.223.118'), ... ]

        # This is where we loose the 'vlan' part of the site. It's no longer
        # important because inventory files are per site.
        site_path, inv_entries = final_records.setdefault(site,
                                                          (site_path, set()))

        for intr in inv_interfaces:
            if not intr.has_dns_info():
                continue  # Don't event try
            for ip in intr.ips:
                # We need to collect all the entries in all the vlans into
                # the same site.
                # !!! This '.' is important!
                inv_entries.add((intr.hostname + ".", ip, intr))

    log("=" * 10 + " Final DNS data", DEBUG)
    for site, site_data in final_records.items():
        site_path, inv_entries = site_data
        # Inv entries are in (<'name'>, <'ip'>) form

        zone, svn_entries = svn_zones.get(site, None)

        if svn_entries is not None:
            raw_a_records = filter_forward_conflicts(svn_entries, inv_entries,
                                                     site_path)
            clean_a_records = []
            for name, ip, intr in raw_a_records:
                cname_conflict = False
                for dns_name, ttl, dns_data in zone.iterate_rdatas('CNAME'):
                    cname = dns_name.to_text()
                    cdata = dns_data.to_text()
                    # This is madness, but it must be done.
                    if cname == name:
                        log("'{0}  A {1}' would conflict with '{2}   CNAME {3}', This "
                            "A record will not be included in the build "
                            "output.".format(name, ip, cname, cdata),
                            WARNING)
                        log("^ The system the conflict belongs to: "
                            "{0}".format(print_system(intr.system)))
                        cname_conflict = True
                if not cname_conflict:
                    clean_a_records.append((name, ip, intr))

        else:
            log("Couldn't find site {0} in svn".format(site),
                WARNING)
            continue

        generate_forward_inventory_data_file(site, clean_a_records, site_path)


def generate_reverse_inventory_data_file(network, records, network_file):
    inventory_file = '{0}.inventory'.format(network_file)
    inv_fd = open(inventory_file, 'w+')
    try:
        log(";---------- PTR records for {0} (in file {1})\n".format(network,
                                                                     inventory_file), BUILD)
        template = "{dnsip:50} {rclass:10} {rtype:15} {name:7}\n"
        for dnsip, name in records:
            info = {'dnsip': dnsip, 'rclass': "IN", 'rtype':
                    'PTR', 'name': name}
            log(template.format(**info), BUILD)
            inv_fd.write(template.format(**info))
        # Bump the soa in network file
        increment_soa(network_file)
        # Insure that the inventory file is included.
        ensure_include(network_file, 'reverse', inventory_file)
    except Exception, e:
        log(str(e), ERROR)
    finally:
        inv_fd.close()

    if DEBUG == True:
        pp.pprint(records)


def generate_forward_inventory_data_file(site, records, site_path):
    inventory_file = os.path.join(site_path, 'inventory')
    private_file = os.path.join(site_path, 'private')
    soa_file = os.path.join(site_path, 'SOA')

    inv_fd = open(inventory_file, 'w+')

    # Because the interface objects are in records at this point, we have to
    # take them out before we remove duplicates.
    a_records = [(name, address) for name, address, intr in records]
    a_records = set(a_records)
    try:
        log(";---------- A records for {0} (in file {1})\n".format(site,
                                                                   site_path), BUILD)
        template = "{name:50} {rclass:10} {rtype:15} {address:7}\n"
        for name, address in a_records:
            info = {'name': name, 'rclass': "IN", 'rtype': 'A',
                    'address': address}
            inv_fd.write(template.format(**info))
            log(template.format(**info), BUILD)
        # Bump the soa
        increment_soa(soa_file)
        # Insure that the inventory file is included.
        ensure_include(private_file, 'forward', inventory_file)
    except Exception, e:
        log(str(e), ERROR)
    finally:
        inv_fd.close()

    if DEBUG == True:
        pp.pprint(records)


def filter_forward_conflicts(svn_records, inv_entries, site):
    """
    :param svn_records: All interfaces in the private file.
    :type svn_records: list

    :param inventory_interfaces: All interfaces in the inventory KV store.
    :type invnetory_interfaces: list

    """
    no_conflict_entries = []
    for name, ip, intr in inv_entries:
        if (name, ip) in svn_records:
            log("System {0} (interface: {1}, {2}) has conflict"
                .format(intr.system, ip, name), INFO)
        else:
            no_conflict_entries.append((name, ip, intr))

    return no_conflict_entries


def analyse_svn(forward, reverse):

    # forward_prime
    forward_p = set()
    for site, values in forward.iteritems():
        # Transform foward to look like reverse so we can use sets. Nifty
        # python sets are nifty.
        rzone, records = values
        for name, ip in records:
            if not ip.startswith('10'):
                continue
            if name.find('unused') > -1:
                # Don't care
                continue
            if name.find('sjc1') > -1:
                # Don't care
                continue
            dnsip = ip_to_domain_name(ip)
            forward_p.add((dnsip, name))

    # Make reverse_p
    reverse_p = set()
    for site, site_data in reverse.iteritems():
        site_path, values = site_data
        rzone, records = values
        for dnsip, name in records:
            if not dns2ip_form(dnsip).startswith('10'):
                continue
            if name.find('unused') > -1:
                # Don't care
                continue
            if name.find('sjc1') > -1:
                # Don't care
                continue
            reverse_p.add((dnsip, name))

    print ("PTR records in sysadmins/dnsconfig/ip-addr/ with no matching A "
           "record in sysadmins/dnsconfig/zones/mozilla.com")
    for dnsip, name in reverse_p.difference(forward_p):
        template = "{dnsip:50} {rclass:10} {rtype:15} {name:7}"
        info = {'dnsip': dnsip, 'rclass': "IN", 'rtype': 'PTR', 'name': name}
        print template.format(**info)

    print ("A records in sysadmins/dnsconfig/zones/mozilla.com with no "
           "matching PTR record in sysadmins/dnsconfig/ip-addr/")
    for dnsip, name in forward_p.difference(reverse_p):
        address = dns2ip_form(dnsip)
        template = "{name:50} {rclass:10} {rtype:15} {address:7}"
        info = {'name': name, 'rclass': "IN", 'rtype': 'A', 'address': address}
        print template.format(**info)
