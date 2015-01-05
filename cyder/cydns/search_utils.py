from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def fqdn_search(fqdn, *args, **kwargs):
    """Find any records that have a name that is the provided fqdn. This
    name would show up on the left hand side of a zone file and in a PTR's
    case the right side.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: (type, Querysets) tuples containing all the objects that matched
        during
    the search are returned.
    """
    return _build_queries(fqdn, *args, **kwargs)


def smart_fqdn_exists(fqdn, *args, **kwargs):
    """
    Searching for a fqdn by actually looking at a fqdn is very inefficient.
    Instead we should:
        1) Look for a domain with the name of fqdn.
        2) Look for a label = fqdn.split('.')[0]
            and domain = fqdn.split('.')[1:]
    """
    from cyder.cydns.domain.models import Domain

    # Try approach 1
    try:
        search_domain = Domain.objects.get(name=fqdn)
        label = ''
    except ObjectDoesNotExist:
        search_domain = None
    if search_domain:
        for type_, qset in _build_label_domain_queries(
                label, search_domain, **kwargs):
            if qset.exists():
                return qset

    # Try approach 2
    search_domain = None
    if len(fqdn.split('.')) == 1:
        return None
    try:
        label = fqdn.split('.')[0]
        domain_name = '.'.join(fqdn.split('.')[1:])
        search_domain = Domain.objects.get(
            name=domain_name)
    except ObjectDoesNotExist:
        search_domain = None
    if search_domain:
        for type_, qset in _build_label_domain_queries(
                label, search_domain, **kwargs):
            if qset.exists():
                return qset


def _build_label_domain_queries(label, domain, mx=True, sr=True, tx=True,
                                cn=True, ar=True, intr=True, ns=True, ss=True):
    # We import this way to make it easier to import this file without
    # getting cyclic imports.
    qsets = []
    if mx:
        from cyder.cydns.mx.models import MX
        qsets.append(('MX', MX.objects.
                      filter(**{'label': label, 'domain': domain})))
    if ns:
        if label == '':
            from cyder.cydns.nameserver.models import Nameserver
            qsets.append(('NS', Nameserver.objects.
                          filter(**{'domain': domain})))
    if sr:
        from cyder.cydns.srv.models import SRV
        qsets.append(('SRV', SRV.objects.
                      filter(**{'label': label, 'domain': domain})))
    if tx:
        from cyder.cydns.txt.models import TXT
        qsets.append(('TXT', TXT.objects.
                      filter(**{'label': label, 'domain': domain})))
    if ss:
        from cyder.cydns.sshfp.models import SSHFP
        qsets.append(('SSHFP', SSHFP.objects.
                      filter(**{'label': label, 'domain': domain})))
    if cn:
        from cyder.cydns.cname.models import CNAME
        qsets.append(('CNAME', CNAME.objects.
                      filter(**{'label': label, 'domain': domain})))
    if ar:
        from cyder.cydns.address_record.models import AddressRecord
        ars = AddressRecord.objects.filter(
            **{'label': label, 'domain': domain})
        qsets.append(('AddressRecord', ars))
    if intr:
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        intrs = StaticInterface.objects.filter(
            **{'label': label, 'domain': domain})
        qsets.append(('AddressRecord', intrs))

    return qsets


def fqdn_exists(fqdn, **kwargs):
    """Return a Queryset or False depending on whether an object exists
    with the fqdn.

    :param fqdn: The name to search for.
    :type   fqdn: str
    :return: True or False
    """
    for type_, qset in _build_queries(fqdn, **kwargs):
        if qset.exists():
            return qset
    return False


def _build_queries(fqdn, dn=True, mx=True, sr=True, tx=True,
                   cn=True, ar=True, pt=True, ip=False, intr=True,
                   search_operator=''):
    # We import this way to make it easier to import this file without
    # getting cyclic imports.
    qsets = []
    if dn:
        from cyder.cydns.domain.models import Domain
        qsets.append(
            ('Domain', Domain.objects.filter(
                **{'name{0}'.format(search_operator): fqdn})))
    if mx:
        from cyder.cydns.mx.models import MX
        qsets.append(
            ('MX', MX.objects.filter(
                **{'fqdn{0}'.format(search_operator): fqdn})))
    if sr:
        from cyder.cydns.srv.models import SRV
        qsets.append(
            ('SRV', SRV.objects.filter(
                **{'fqdn{0}'.format(search_operator): fqdn})))
    if tx:
        from cyder.cydns.txt.models import TXT
        qsets.append(
            ('TXT', TXT.objects.filter(
                **{'fqdn{0}'.format(search_operator): fqdn})))
    if cn:
        from cyder.cydns.cname.models import CNAME
        qsets.append(
            ('CNAME', CNAME.objects.filter(
                **{'fqdn{0}'.format(search_operator): fqdn})))
    if ar:
        from cyder.cydns.address_record.models import AddressRecord
        ars = AddressRecord.objects.filter(Q(fqdn=fqdn) | Q(ip_str=ip))
        qsets.append(('AddressRecord', ars))
    if pt:
        from cyder.cydns.ptr.models import PTR
        qsets.append(
            ('PTR', PTR.objects.filter(
                  Q(**{'fqdn{0}'.format(search_operator): fqdn}) |
                  Q(**{'ip_str{0}'.format(search_operator): ip}))))
    if intr:
        from cyder.cydhcp.interface.static_intr.models import StaticInterface
        qsets.append(
            ('StaticInterface', StaticInterface.objects.filter(
                Q(**{'fqdn{0}'.format(search_operator): fqdn}) |
                Q(**{'ip_str{0}'.format(search_operator): ip}))))

    return qsets
