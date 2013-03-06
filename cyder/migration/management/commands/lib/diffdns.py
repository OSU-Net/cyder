from django.conf import settings

from dns import zone
from iscpy.iscpy_dns.named_importer_lib import MakeNamedDict

import os
import subprocess
import itertools


def resolve(name, ns, rdclass="all"):
    proc = subprocess.Popen(["dig", "@{0}".format(ns), name, rdclass,
                            "+short", "+norecurse"], stdout=subprocess.PIPE)
    x = proc.communicate()[0].lower()
    x = x.split('\n')
    x = '\n'.join(sorted(x))
    return x


def check_rdtype(zone, nss, rdtype):
    r = {}
    for (name, ttl, rdata) in zone.iterate_rdatas(rdtype):
        name = name.to_text()
        results = []
        for ns in nss:
            res = resolve(name, ns, rdclass=rdtype)
            if res.strip('\n').find("unused") != -1:
                continue
            results.append(res)
        if len(set(results)) > 1:  # set() removes duplicates
            r[name] = {}

            for ns, result in itertools.izip(nss, results):
                r[name][ns] = [i for i in result.strip().split('\n') if i]

            if r[name] == {}:
                del(r[name])

    return r


def diff_nameservers(nss, zone_name, mzone):
    if zone_name.endswith('in-addr.arpa'):
        # Don't check for MX's
        rdtypes = ["A", "AAAA", "CNAME", "NS", "SRV", "TXT", "PTR"]
    else:
        rdtypes = ["A", "AAAA", "CNAME", "NS", "MX", "SRV", "TXT", "PTR"]
    r = {}
    for rdtype in rdtypes:
        temp = check_rdtype(mzone, nss, rdtype)
        if temp:
            r[rdtype] = temp
    return r


def get_zone_data(zone_name, filepath, dirpath):
    cwd = os.getcwd()
    os.chdir(dirpath)
    mzone = zone.from_file(filepath, zone_name, relativize=False)
    os.chdir(cwd)
    return mzone


def handle_zone(nss, zone_name, zone_meta, zone_path):
    if not zone_meta['file']:
        print "No zone file for {0}".format(zone_name)
        return
    print "== Diffing {0}. ({1})".format(zone_name, zone_meta['file'])
    mzone = get_zone_data(zone_name, zone_meta['file'], zone_path)
    return diff_nameservers(nss, zone_name, mzone)


def diff_zones(ns1, ns2, zone_file, skip_edu=False):
    zones = MakeNamedDict(open(zone_file).read())
    r = {}
    for zone_name, zone_meta in zones['orphan_zones'].iteritems():
        if zone_name in settings.ZONE_BLACKLIST or \
                (skip_edu and zone_name[-4:] == ".edu"):
            print "Skipping %s" % zone_name
            continue
        temp = (handle_zone([ns1, ns2], zone_name, zone_meta,
                            settings.ZONE_PATH))
        if temp:
            for rdtype in temp:
                if rdtype not in r:
                    r[rdtype] = {}
                for name in temp[rdtype]:
                    r[rdtype][name] = temp[rdtype][name]
    return r
