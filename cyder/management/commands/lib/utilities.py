import MySQLdb
from django.conf import settings


def get_cursor(name):
    connection = MySQLdb.connect(host=settings.MIGRATION_HOST,
                                 user=settings.MIGRATION_USER,
                                 passwd=settings.MIGRATION_PASSWD,
                                 db=settings.MIGRATION_DB)
    cursor = connection.cursor()
    return cursor


def long2ip(ip):
    return ".".join(map(lambda x: str((ip >> x) & 255), range(24, -1, -8)))


def ip2long(ip):
    return reduce(lambda num, octet: (num << 8) | int(octet), ip.split('.'), 0)


def clean_mac(mac):
    return mac.lower().replace(':', '')


def calc_prefixlen(netmask):
    bits = 0
    while netmask:
        bits += netmask & 1
        netmask >>= 1
    return bits


ATTR_CONVERSIONS = {
    'slp-scope': 'slp-service-scope'
}


def fix_attr_name(attr_name):
    if attr_name in ATTR_CONVERSIONS:
        return ATTR_CONVERSIONS[attr_name]
    else:
        return attr_name


def range_usage_get_create(Klass, **kwargs):
    created = False
    try:
        obj = Klass.objects.get(**kwargs)
    except Klass.DoesNotExist:
        obj = Klass(**kwargs)
        obj.full_clean()
        created = True

    obj.save(update_range_usage=False)
    return obj, created


def ensure_domain_workaround(name):
    # This creates all levels of a fqdn without dealing with all of the stuff
    # in the normal ensure_domain
    from cyder.models import Domain
    parts = name.split('.')
    parts, dom = parts[:-1], parts[-1]
    while parts:
        Domain.objects.get_or_create(name=dom)
        parts, dom = parts[:-1], ".".join([parts[-1], dom])
    dom, _ = Domain.objects.get_or_create(name=dom)
    return dom


def get_label_domain_workaround(fqdn):
    # This creates a label/domain from a fqdn and resolves any conflicts with
    # existing objects by giving them a blank label
    from cyder.models import (Domain, MX, StaticInterface, AddressRecord,
                              CNAME, TXT)
    conflict_objects = [MX, StaticInterface, AddressRecord, CNAME, TXT]
    label, domain_name = tuple(fqdn.split('.', 1))
    objs = []
    for obj_type in conflict_objects:
        objs.extend(list(obj_type.objects
                         .filter(fqdn=domain_name).exclude(label="")))

    if objs:
        for obj in objs:
            print "Clobbering %s %s %s" % (obj.pretty_type, obj.label,
                                           obj.domain.name)
            obj.label = "not_a_real_label_please_delete"
            obj.save()

        domain, _ = Domain.objects.get_or_create(name=domain_name)
        for obj in objs:
            obj.label = ""
            ctnr_set = obj.domain.ctnr_set
            for ctnr in ctnr_set.all():
                ctnr.domains.add(domain)
            obj.domain = domain
            obj.save()

        objs = []
        for obj_type in conflict_objects:
            objs.extend(list(obj_type.objects
                             .filter(fqdn=domain_name).exclude(label="")))
        assert not objs

    ensure_domain_workaround(domain_name)
    domain, _ = Domain.objects.get_or_create(name=domain_name)
    return label, domain
