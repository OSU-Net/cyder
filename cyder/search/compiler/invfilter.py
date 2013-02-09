import operator
import ipaddr
import re

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.exceptions import ValidationError
from django.db.models import Q

from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.utils import IPFilter
from cyder.cydhcp.utils import start_end_filter
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.soa.models import SOA
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.txt.models import TXT
from cyder.cydns.view.models import View


searchables = (
        ('A', AddressRecord),
        ('CNAME', CNAME),
        ('DOMAIN', Domain),
        ('INTR', StaticInterface),
        ('MX', MX),
        ('NS', Nameserver),
        ('PTR', PTR),
        ('SOA', SOA),
        ('SRV', SRV),
        ('SSHFP', SSHFP),
        ('SYSTEM', System),
        ('TXT', TXT),
)


def get_managers():
    managers = []
    for name, Klass in searchables:
        managers.append(Klass.objects)
    return managers


class _Filter(object):
    """
    The Base class of different filters. Implement these methods
    """
    ntype = "FILTER"

    def __str__(self):
        return self.value

    def __repr__(self):
        return "<{1}>".format(self.__class__, self)

    def compile_Q(self, ntype):
        pass


def build_filter(filter_, fields, filter_type):
    # rtucker++
    final_filter = Q()
    for t in fields:
        final_filter = final_filter | Q(**{"{0}__{1}".format(t,
            filter_type): filter_})

    return final_filter


class TextFilter(_Filter):

    def __init__(self, rvalue):
        self.value = rvalue
        self.Q = self.compile_Q(rvalue)

    def compile_Q(self, value):
        # Value is the search term
        result = []
        for name, Klass in searchables:
            result.append(build_filter(value, Klass.search_fields,
                                       'icontains'))
        return result


class REFilter(TextFilter):
    """Regex filter."""
    num_match = re.compile("\[(\d+)-(\d+)\]")

    def _expand_number_regex(self, value):
        """We want to turn something like /hp-node[31-40].phx1 into
            '/hp-node(31|32|33|34|35|36|37|38|39|40).phx1'"""
        matches = self.num_match.findall(value)
        for low, high in matches:
            if int(low) >= int(high):
                continue
            new_value = ""
            for i in xrange(int(low), int(high) + 1):
                new_value += "{0}|".format(i)
            new_value = '(' + new_value.strip('|') + ')'
            value = value.replace('[{0}-{1}]'.format(low, high), new_value)
        return value

    def compile_Q(self, value):
        result = []
        value = self._expand_number_regex(value)
        for name, Klass in searchables:
            result.append(build_filter(value, Klass.search_fields, 'regex'))
        return result


class DirectiveFilter(_Filter):
    """Directive Filter. Queryset is build when the object is created."""

    def __init__(self, rvalue, directive, dvalue):
        self.value = rvalue
        self.directive = directive
        self.dvalue = dvalue
        self.Q = self.compile_Q(directive, dvalue)

    def compile_Q(self, directive, dvalue):
        if directive == 'view':
            return build_view_qsets(dvalue)
        elif directive == 'network':
            return build_network_qsets(dvalue)
        elif directive == 'vlan':
            return build_vlan_qsets(dvalue)
        elif directive == 'zone':
            return build_zone_qsets(dvalue)
        elif directive == 'range':
            return build_range_qsets(dvalue)
        elif directive == 'type':
            return build_rdtype_qsets(dvalue)
        elif directive == 'site':
            return build_site_qsets(dvalue)
        else:
            raise BadDirective("Unknown Directive '{0}'".format(directive))


# TODO, move this into it's own file
##############################################################################
##########################  Directive Filters  ###############################
##############################################################################


class BadDirective(Exception):
    pass


def build_rdtype_qsets(rdtype):
    """This function needs to filter out all records of a certain rdtype (like
    A or CNAME). Any filter produced here has to be able to be negated. We use
    the fact that every object has a pk > -1. When a qset is negated the query
    becomes pk <= -1.
    """
    rdtype = rdtype.upper()  # Let's get consistent
    select = Q(pk__gt=-1)
    no_select = Q(pk__lte=-1)
    result = []
    for name, Klass in searchables:
        if name == rdtype:
            result.append(select)
        else:
            result.append(no_select)
    return result


def build_view_qsets(view_name):
    """Filter based on DNS views."""
    view_name = view_name.lower()  # Let's get consistent
    try:
        view = View.objects.get(name=view_name)
    except ObjectDoesNotExist:
        raise BadDirective("'{0}' isn't a valid view.".format(view_name))
    view_filter = Q(views=view)  # This will slow queries down due to joins
    q_sets = []
    select = Q(pk__gt=-1)
    for name, Klass in searchables:
        if name == 'SOA':
            q_sets.append(select)  # SOA's are always public and private
        elif hasattr(Klass, 'views'):
            q_sets.append(view_filter)
        else:
            q_sets.append(None)
    return q_sets


def build_ipf_qsets(q):
    """Filter based on IP address views.
    :param q: A filter for a certain IP or IP range
    :type q: Q
    """
    q_sets = []
    for name, Klass in searchables:
        if name == 'A' or name == 'INTR' or name == 'PTR':
            q_sets.append(q)
        else:
            q_sets.append(None)
    return q_sets


def build_range_qsets(range_):
    try:
        start, end = range_.split(',')
    except ValueError:
        raise BadDirective("Specify a range using the format: start,end")
    if start.find(':') > -1:
        ip_type = '6'
    if end.find('.') > -1:
        ip_type = '4'
    try:
        istart, iend, ipf_q = start_end_filter(start, end, ip_type)
    except (ValidationError, ipaddr.AddressValueError), e:
        raise BadDirective(str(e))
    return build_ipf_qsets(ipf_q)


def build_network_qsets(network_str):
    # Todo move these directive processors into functions.
    if network_str.find(':') > -1:
        Klass = ipaddr.IPv6Network
        ip_type = '6'
    if network_str.find('.') > -1:
        Klass = ipaddr.IPv4Network
        ip_type = '4'
    try:
        network = Klass(network_str)
        ipf = IPFilter(network.network, network.broadcast, ip_type)
    except (ipaddr.AddressValueError, ipaddr.NetmaskValueError):
        raise BadDirective("{0} isn't a valid "
                "network.".format(network_str))
    return build_ipf_qsets(ipf.Q)


def build_site_qsets(site_name):
    try:
        site = Site.objects.get(name=site_name)
    except ObjectDoesNotExist:
        raise BadDirective("{0} isn't a valid "
                "site.".format(site_name))
    return build_ipf_qsets(site.compile_Q())


def build_vlan_qsets(vlan_name):
    try:
        if vlan_name.isdigit():
            vlan = Vlan.objects.get(number=vlan_name)
        else:
            vlan = Vlan.objects.get(name=vlan_name)
    except ObjectDoesNotExist:
        raise BadDirective("{0} isn't a valid "
                "vlan identifier.".format(vlan_name))
    except MultipleObjectsReturned:
        raise BadDirective("{0} doesn't uniquely identify"
                "a vlan.".format(vlan_name))
    return build_ipf_qsets(vlan.compile_Q())


def build_zone_qsets(zone):
    """The point of this filter is to first find the root of a dns zone
    specified by zone and then build a query to return all records in this
    zone.
    """
    try:
        root_domain = Domain.objects.get(name=zone)
        # This might not actually be the root of a zone, but functionally we
        # don't really care.
    except ObjectDoesNotExist:
        raise BadDirective("'{0}' part of a valid zone.".format(zone))

    if not root_domain.soa:
        raise BadDirective("'{0}' part of a valid zone.".format(zone))

    def _get_zone_domains(domain):
        domains = [domain]
        for sub_domain in domain.domain_set.filter(soa=domain.soa):
            domains += _get_zone_domains(sub_domain)
        return domains

    domains = _get_zone_domains(root_domain)

    if root_domain.is_reverse:
        domains = [Q(reverse_domain=domain) for domain in domains]
    else:
        domains = [Q(domain=domain) for domain in domains]

    zone_query = reduce(operator.or_, domains, Q())

    result = []
    for name, Klass in searchables:
        if hasattr(Klass, 'domain') and not root_domain.is_reverse:
            result.append(zone_query)
        elif hasattr(Klass, 'reverse_domain') and root_domain.is_reverse:
            result.append(zone_query)
        elif name == 'SOA':
            result.append(Q(pk=root_domain.soa.pk))
        else:
            result.append(None)
    return result
