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
    names = [name for name, ttl, rdata in zone.iterate_rdatas(rdtype)]
    for name in sorted(list(set(names))):
        name = name.to_text()
        results = []
        for ns in nss:
            res = resolve(name, ns, rdclass=rdtype)
            if res.strip('\n').find("unused") != -1:
                continue
            results.append(res)
        if len(set(results)) > 1:  # set() removes duplicates
            print "!! Found differences for {0} {1}".format(rdtype, name)
            r[name] = {}

            for ns, result in itertools.izip(nss, results):
                result = result.strip().split('\n')
                # print "   ", ns, result
                r[name][ns] = [i for i in result if i]

    if len(r):
        print "!! %s differences found." % len(r)

    return r


def diff_nameservers(nss, z_name, mzone):
    if z_name.endswith('in-addr.arpa'):
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


def get_z_data(z_name, filepath, dirpath):
    cwd = os.getcwd()
    os.chdir(dirpath)
    mzone = zone.from_file(filepath, z_name, relativize=False)
    os.chdir(cwd)
    return mzone


def handle_zone(nss, z_name, z_meta, z_path):
    if not z_meta['file']:
        print "No zone file for {0}".format(z_name)
        return
    print "== Diffing {0} ({1})".format(z_name, z_meta['file'])
    mzone = get_z_data(z_name, z_meta['file'], z_path)
    return diff_nameservers(nss, z_name, mzone)


def diff_zones(ns1, ns2, z_file, skip_edu=False):
    zones = MakeNamedDict(open(z_file).read())
    r = {}
    for z_name, z_meta in sorted(list(zones['orphan_zones'].iteritems())):
        if z_name in settings.ZONE_BLACKLIST or \
                (skip_edu and z_name[-4:] == ".edu"):
            print "Skipping %s" % z_name
            continue
        temp = (handle_zone([ns1, ns2], z_name, z_meta,
                            settings.ZONE_PATH))
        if temp:
            for rdtype in temp:
                if rdtype not in r:
                    r[rdtype] = {}
                for name in temp[rdtype]:
                    r[rdtype][name] = temp[rdtype][name]
    return r
