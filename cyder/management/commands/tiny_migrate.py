#!/usr/bin/env python
from django.core.management.base import LabelCommand
from django.core.exceptions import ValidationError

from cyder.models import (Domain, TXT, AddressRecord, Nameserver, MX, CNAME,
                          SOA, PTR, SRV, StaticInterface, View)

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


def ensure_domain(name):
    parts = name.split('.')
    parts, dom = parts[:-1], parts[-1]
    while parts:
        Domain.objects.get_or_create(name=dom)
        parts, dom = parts[:-1], ".".join([parts[-1], dom])
    dom, _ = Domain.objects.get_or_create(name=dom)
    return dom


def diglet(rdtype, target, ns='ns1.oregonstate.edu'):
    cmd = "dig %s %s @%s +short +norecurse" % (rdtype, target, ns)
    result = subprocess.check_output(cmd.split(' ')).strip()
    return result or None


def get_label_domain(fqdn):
    conflict_objects = [MX, StaticInterface, AddressRecord, CNAME]
    label, domain_name = tuple(fqdn.split('.', 1))
    objs = []
    for obj_type in conflict_objects:
        objs.extend(list(obj_type.objects
                         .filter(fqdn=domain_name).exclude(label="")))

    if objs:
        for obj in objs:
            obj.label = "not_a_real_label_please_delete"
            obj.save()
        domain, _ = Domain.objects.get_or_create(name=domain_name)
        for obj in objs:
            obj.label = ""
            obj.domain = domain
            obj.save()

        objs = []
        for obj_type in conflict_objects:
            objs.extend(list(obj_type.objects
                             .filter(fqdn=domain_name).exclude(label="")))
        assert not objs

    ensure_domain(domain_name)
    domain, _ = Domain.objects.get_or_create(name=domain_name)
    return label, domain


def tiny2txt(fqdn, s, ttl=3600):
    ttl = int(ttl)
    label, domain = get_label_domain(fqdn)
    s = s.replace(r'\072', ':').replace(r'\040', ' ').replace(r'\057', '/')
    txt, _ = TXT.objects.get_or_create(label=label, domain=domain,
                                       txt_data=s, ttl=ttl)
    return txt


def tiny2ar(fqdn, ip):
    label, domain = get_label_domain(fqdn)
    if AddressRecord.objects.filter(label=label, domain=domain,
                                    ip_str=ip).exists():
        print "AddressRecord %s already exists." % domain.name
        return

    ar, _ = AddressRecord.objects.get_or_create(label=label, domain=domain,
                                                ip_str=ip)
    return ar


def tiny2ns(fqdn, ip, x, ttl=86400, timestamp=None, lo=None):
    ttl = int(ttl)
    domain = ensure_domain(fqdn)
    ns, _ = Nameserver.objects.get_or_create(domain=domain, server=x, ttl=ttl)
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
        label, domain = get_label_domain(fqdn)
        try:
            srv, _ = SRV.objects.get_or_create(label=label, domain=domain,
                                               target=target, port=port,
                                               priority=priority, ttl=ttl,
                                               weight=weight)
            return srv
        except ValidationError, e:
            print "INVALID: %s for SRV %s" % (e, fqdn)
    elif n == 28:
        digged = diglet('AAAA', fqdn)
        label, domain = get_label_domain(fqdn)
        if AddressRecord.objects.filter(label=label, domain=domain,
                                        ip_str=digged).exists():
            print "AddressRecord %s already exists." % domain.name
            return

        ar, _ = AddressRecord.objects.get_or_create(label=label, domain=domain,
                                                    ip_str=digged, ttl=ttl,
                                                    ip_type='6')
        return ar
    else:
        raise Exception("Unknown rdtype %s for %s" % (n, fqdn))


def tiny2mx(fqdn, ip, x, dist=5, ttl=600):
    dist = int(dist)
    ttl = int(ttl)
    domain = ensure_domain(fqdn)
    existing = MX.objects.filter(label="", domain=domain,
                                 server=x, priority=dist)
    if existing.exists():
        return
    mx = MX(label="", domain=domain, server=x, priority=dist, ttl=ttl)
    mx.save()
    return mx


def tiny2cname(fqdn, p):
    label, domain = get_label_domain(fqdn)
    cname, _ = CNAME.objects.get_or_create(label=label, domain=domain,
                                           target=p)
    return cname


def tiny2soa(fqdn, mname, rname, ser, ref=300, ret=900, exp=604800, _min=86400,
             ttl=86400, timestamp=None, lo=None):
    domain = ensure_domain(fqdn)
    if SOA.objects.filter(root_domain=domain).exists():
        print "SOA %s already exists." % domain.name
        return

    soa, _ = SOA.objects.get_or_create(root_domain=domain, primary=mname,
                                       contact=rname, retry=ret, refresh=ref,
                                       expire=exp, minimum=_min, ttl=ttl)
    return soa


def tiny2ptr(fqdn, p, ttl=3600):
    label, domain = get_label_domain(p)
    for rdtype in ['A', 'AAAA']:
        ip_type = '6' if rdtype == 'AAAA' else '4'
        ip_str = diglet(rdtype, p)
        if ip_str:
            try:
                ptr, _ = PTR.objects.get_or_create(label=label, domain=domain,
                                                   ip_str=ip_str,
                                                   ip_type=ip_type)
                ptr.views.add(public)
                ptr.views.add(private)
            except ValidationError, e:
                print "INVALID: %s for PTR %s" % (e, p)
        else:
            print "No %s candidate for PTR %s" % (rdtype, p)


class Command(LabelCommand):

    def handle_label(self, label, **options):
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
            if not line or line[0] == '#':
                continue

            rdtype, line = line[0], line[1:]
            if rdtype in tinyprefixes:
                tiny2cyder = tinyprefixes[rdtype]
                obj = tiny2cyder(*line.split(':'))
                if obj and hasattr(obj, 'views'):
                    obj.views.add(public)
                    obj.views.add(private)
            else:
                raise Exception("Unknown prefix: %s" % rdtype)
