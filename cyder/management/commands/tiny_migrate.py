#!/usr/bin/env python
from django.core.management.base import LabelCommand
from django.core.exceptions import ValidationError

from cyder.models import (TXT, AddressRecord, Nameserver, MX, CNAME,
                          SOA, PTR, SRV, View, Ctnr)
from lib.utilities import ensure_domain_workaround, get_label_domain_workaround

import subprocess

"""
' txt
    'fqdn:s:ttl:timestamp:lo
+ a record without ptr
    +fqdn:ip:ttl:timestamp:lo
. nameserver + ar + soa
    .fqdn:ip:x:ttl:timestamp:lo
: ?????
    :fqdn:n:rdata:ttl:timestamp:lo
@ mx
    @fqdn:ip:x:dist:ttl:timestamp:lo
C cname
    Cfqdn:p:ttl:timestamp:lo
Z soa
    Zfqdn:mname:rname:ser:ref:ret:exp:min:ttl:timestamp:lo
^ ptr
    ^fqdn:p:ttl:timestamp:lo
"""

public = View.objects.get(name="public")
private = View.objects.get(name="private")
activectnr = None


def diglet(rdtype, target, ns='ns1.oregonstate.edu'):
    cmd = "dig %s %s @%s +short +norecurse" % (rdtype, target, ns)
    result = subprocess.check_output(cmd.split(' ')).strip()
    return result or None


def tiny2txt(fqdn, s, ttl=3600):
    ttl = int(ttl)
    label, domain = get_label_domain_workaround(fqdn)
    s = s.replace(r'\072', ':').replace(r'\040', ' ').replace(r'\057', '/')
    txt, _ = TXT.objects.get_or_create(label=label, domain=domain,
                                       txt_data=s, ttl=ttl, ctnr=activectnr)
    return txt


def tiny2ar(fqdn, ip):
    label, domain = get_label_domain_workaround(fqdn)
    if AddressRecord.objects.filter(label=label, domain=domain,
                                    ip_str=ip).exists():
        print "AddressRecord %s already exists." % domain.name
        return

    ar, _ = AddressRecord.objects.get_or_create(label=label, domain=domain,
                                                ip_str=ip, ctnr=activectnr)
    return ar


def tiny2ns(fqdn, ip, x, ttl=86400, timestamp=None, lo=None):
    ttl = int(ttl)
    domain = ensure_domain_workaround(fqdn)
    ns, _ = Nameserver.objects.get_or_create(domain=domain, server=x, ttl=ttl,
                                             ctnr=activectnr)
    return ns


def tiny2wut(fqdn, n, rdata, ttl=86400):
    n = int(n)
    if n == 33:
        digged = diglet('SRV', fqdn)
        if not digged:
            print "No SRV candidate for %s" % fqdn
            return

        priority, weight, port, target = digged.split(' ')
        target = target.rstrip('.')
        label, domain = get_label_domain_workaround(fqdn)
        try:
            srv, _ = SRV.objects.get_or_create(label=label, domain=domain,
                                               target=target, port=port,
                                               priority=priority, ttl=ttl,
                                               weight=weight, ctnr=activectnr)
            return srv
        except ValidationError, e:
            print "INVALID: %s for SRV %s" % (e, fqdn)
    elif n == 28:
        digged = diglet('AAAA', fqdn)
        label, domain = get_label_domain_workaround(fqdn)
        if AddressRecord.objects.filter(label=label, domain=domain,
                                        ip_str=digged).exists():
            print "AddressRecord %s already exists." % domain.name
            return

        ar, _ = AddressRecord.objects.get_or_create(
            label=label, domain=domain, ip_str=digged, ttl=ttl,
            ip_type='6', ctnr=activectnr)
        return ar
    else:
        raise Exception("Unknown rdtype %s for %s" % (n, fqdn))


def tiny2mx(fqdn, ip, x, dist=5, ttl=600):
    dist = int(dist)
    ttl = int(ttl)
    domain = ensure_domain_workaround(fqdn)
    existing = MX.objects.filter(label="", domain=domain,
                                 server=x, priority=dist)
    if existing.exists():
        return
    mx = MX(label="", domain=domain, server=x, priority=dist,
            ttl=ttl, ctnr=activectnr)
    mx.save()
    return mx


def tiny2cname(fqdn, p):
    label, domain = get_label_domain_workaround(fqdn)
    cname, _ = CNAME.objects.get_or_create(label=label, domain=domain,
                                           target=p, ctnr=activectnr)
    return cname


def tiny2soa(fqdn, mname, rname, ser, ref=300, ret=900, exp=604800, _min=86400,
             ttl=86400, timestamp=None, lo=None):
    domain = ensure_domain_workaround(fqdn)
    if SOA.objects.filter(root_domain=domain).exists():
        print "SOA %s already exists." % domain.name
        return

    soa, _ = SOA.objects.get_or_create(
        root_domain=domain, primary=mname, contact=rname, retry=ret,
        refresh=ref, expire=exp, minimum=_min, ttl=ttl)
    return soa


def tiny2ptr(fqdn, p, ttl=3600):
    for rdtype in ['A', 'AAAA']:
        ip_type = '6' if rdtype == 'AAAA' else '4'
        ip_str = diglet(rdtype, p)
        if ip_str:
            try:
                ptr, _ = PTR.objects.get_or_create(
                    fqdn=p, ip_str=ip_str,
                    ip_type=ip_type, ctnr=activectnr)
                ptr.views.add(public)
                ptr.views.add(private)
            except ValidationError, e:
                print "INVALID: %s for PTR %s" % (e, p)
        else:
            print "No %s candidate for PTR %s" % (rdtype, p)


class Command(LabelCommand):

    def handle_label(self, label, **options):
        global activectnr
        tinyprefixes = {"'": tiny2txt,
                        "+": tiny2ar,
                        ".": tiny2ns,
                        ":": tiny2wut,
                        "@": tiny2mx,
                        "C": tiny2cname,
                        "Z": tiny2soa,
                        "^": tiny2ptr}

        for line in open(label):
            line = line.strip()
            if not line:
                continue
            elif line[0] == '#':
                if 'ctnr' in line:
                    ctnrname = line.split()[-1]
                    activectnr = Ctnr.objects.get(name=ctnrname)
                    print
                    print ctnrname
                continue

            print line
            rdtype, line = line[0], line[1:]
            if rdtype in tinyprefixes:
                tiny2cyder = tinyprefixes[rdtype]
                try:
                    obj = tiny2cyder(*line.split(':'))
                    if obj and hasattr(obj, 'views'):
                        obj.views.add(public)
                        obj.views.add(private)
                except ValidationError, e:
                    print "ERROR: ", e
            else:
                raise Exception("Unknown prefix: %s" % rdtype)
