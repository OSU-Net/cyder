from django.db.models import Q

from cyder.base.constants import IP_TYPE_4, IP_TYPE_6
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.view.models import View
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range

from gettext import gettext as _
from cyder.core.utils import fail_mail

DEFAULT_TTL = 3600


def render_soa_only(soa, root_domain):
    kwargs = {
        'root_domain': root_domain.name,
        'primary': soa.primary,
        'contact': soa.contact,
        'refresh': soa.refresh,
        'retry': soa.retry,
        'expire': soa.expire,
        'minimum': soa.minimum
    }
    BUILD_STR = _("{root_domain}.     IN   SOA     {primary}. {contact}. (\n"
                  "\t\t{{serial}}     ; Serial\n"
                  "\t\t{refresh}     ; Refresh\n"
                  "\t\t{retry}     ; Retry\n"
                  "\t\t{expire}     ; Expire\n"
                  "\t\t{minimum}     ; Minimum\n"
                  ")\n\n".format(**kwargs))
    return BUILD_STR


def render_rdtype(rdtype_set, **kwargs):
    if len(rdtype_set) == 0:
        return ""

    rdtype_set = map(lambda obj: obj.bind_render_record(**kwargs), rdtype_set)
    rdtype_set = (r.strip() for r in rdtype_set if r.strip())
    if kwargs.pop('sort', True):
        rdtype_set = sorted(rdtype_set, key=lambda s: s.lower())

    return "\n".join(rdtype_set) + "\n"


def _render_forward_zone(default_ttl, nameserver_set, mx_set,
                         addressrecord_set, interface_set, cname_set, srv_set,
                         txt_set, sshfp_set, range_set):
    BUILD_STR = ""
    BUILD_STR += render_rdtype(nameserver_set)
    BUILD_STR += render_rdtype(mx_set)
    BUILD_STR += render_rdtype(txt_set)
    BUILD_STR += render_rdtype(sshfp_set)
    BUILD_STR += render_rdtype(srv_set)
    BUILD_STR += render_rdtype(cname_set)
    BUILD_STR += render_rdtype(interface_set, rdtype='A')
    BUILD_STR += render_rdtype(addressrecord_set)
    BUILD_STR += render_rdtype(range_set, sort=False)
    return BUILD_STR


def render_forward_zone(view, mega_filter):
    data = _render_forward_zone(
        default_ttl=DEFAULT_TTL,

        nameserver_set=Nameserver.objects
        .filter(mega_filter)
        .filter(views__name=view.name).order_by('server'),

        mx_set=MX.objects
        .filter(mega_filter)
        .filter(views__name=view.name).order_by('server'),

        addressrecord_set=AddressRecord.objects
        .filter(mega_filter).filter(views__name=view.name)
        .order_by('pk', 'ip_type', 'fqdn', 'ip_upper', 'ip_lower'),

        interface_set=StaticInterface.objects
        .filter(mega_filter, dns_enabled=True)
        .filter(views__name=view.name)
        .order_by('pk', 'ip_type', 'fqdn', 'ip_upper', 'ip_lower'),

        cname_set=CNAME.objects
        .filter(mega_filter)
        .filter(views__name=view.name)
        .order_by('fqdn'),

        srv_set=SRV.objects
        .filter(mega_filter)
        .filter(views__name=view.name)
        .order_by('pk', 'fqdn'),

        txt_set=TXT.objects
        .filter(mega_filter)
        .filter(views__name=view.name)
        .order_by('pk', 'fqdn'),

        sshfp_set=SSHFP.objects
        .filter(mega_filter)
        .filter(views__name=view.name)
        .order_by('pk', 'fqdn'),

        range_set=Range.objects
        .filter(mega_filter)
        .filter(views__name=view.name)
        .order_by('start_upper', 'start_lower'),
    )
    return data


def _render_reverse_zone(default_ttl, nameserver_set, interface_set,
                         ptr_set, range_set):
    BUILD_STR = ''
    BUILD_STR += render_rdtype(nameserver_set)
    BUILD_STR += render_rdtype(ptr_set)
    BUILD_STR += render_rdtype(interface_set, reverse=True, rdtype='PTR')
    BUILD_STR += render_rdtype(range_set, reverse=True)
    return BUILD_STR


def render_reverse_zone(view, domain_mega_filter, rdomain_mega_filter,
                        range_set, ip_type=IP_TYPE_4):
    data = _render_reverse_zone(
        default_ttl=DEFAULT_TTL,

        nameserver_set=Nameserver.objects.filter(domain_mega_filter).filter(
            views__name=view.name).order_by('server'),

        interface_set=(
            StaticInterface.objects
            .filter(rdomain_mega_filter, dns_enabled=True)
            .filter(views__name=view.name)
            .order_by('pk', 'ip_type', 'label', 'ip_upper', 'ip_lower')),

        ptr_set=PTR.objects.filter(rdomain_mega_filter).filter(
            views__name=view.name).order_by('pk', 'ip_upper',
                                            'ip_lower'),

        range_set=range_set
    )
    return data


def build_zone_data(view, root_domain, soa, logf=None):
    """
    This function does the heavy lifting of building a zone. It coordinates
    getting all of the data out of the db into BIND format.

        :param soa: The SOA corresponding to the zone being built.
        :type soa: SOA

        :param root_domain: The root domain of this zone.
        :type root_domain: str

        :returns public_file_path: The path to the zone file in the STAGEING
            dir
        :type public_file_path: str
        :returns public_data: The data that should be written to
            public_file_path
        :type public_data: str

        :returns view_zone_file: The path to the zone file in the STAGEING dir
        :type view_zone_file: str
        :param view_data: The data that should be written to view_zone_file
        :type view_data: str
    """
    ztype = 'reverse' if root_domain.is_reverse else 'forward'
    if (soa.has_record_set(view=view, exclude_ns=True) and
            not root_domain.nameserver_set.filter(views=view).exists()):
        msg = ("The {0} zone has at least one record in the {1} view, but "
               "there are no nameservers in that view. A zone file for {1} "
               "won't be built. Use the search string 'zone=:{0} view=:{1}' "
               "to find the troublesome record(s)"
               .format(root_domain, view.name))
        fail_mail(msg, subject="Shitty edge case detected.")
        logf(msg)
        return ''

    domains = soa.domain_set.all().order_by('name')

    # Build the mega filter!
    domain_mega_filter = Q(domain=root_domain)
    for domain in domains:
        domain_mega_filter = domain_mega_filter | Q(domain=domain)

    rdomain_mega_filter = Q(reverse_domain=root_domain)
    for reverse_domain in domains:
        rdomain_mega_filter = rdomain_mega_filter | Q(
            reverse_domain=reverse_domain)

    soa_data = render_soa_only(soa=soa, root_domain=root_domain)
    if root_domain.ip_type == '4':
        range_set = (root_domain.get_related_ranges()
                                .filter(views__name=view.name)
                                .order_by('start_upper', 'start_lower'))
    else:
        range_set = []

    try:
        if ztype == "forward":
            view_data = render_forward_zone(view, domain_mega_filter)
        else:
            ip_type = (IP_TYPE_6 if root_domain.name.endswith('ip6.arpa')
                       else IP_TYPE_4)
            view_data = render_reverse_zone(
                view, domain_mega_filter, rdomain_mega_filter, ip_type=ip_type,
                range_set=range_set)
    except View.DoesNotExist:
        view_data = ""

    if view_data:
        view_data = soa_data + view_data

    return view_data
