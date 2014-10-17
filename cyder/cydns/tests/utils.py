from gettext import gettext as gt
import random
import simplejson as json
import string
import time

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory

from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.view.models import View
from cyder.cydns.utils import ensure_domain, prune_tree
from cyder.cydhcp.vrf.models import Vrf


def get_post_data(random_str, suffix):
    """Return a valid set of data"""
    return {
        'root_domain': '{0}{1}'.format(random_str, suffix),
        'soa_primary': 'ns1.mozilla.com',
        'soa_contact': 'noc.mozilla.com',
        'nameserver_1': 'ns1.mozilla.com',
        'ttl_1': '1234'
    }


def create_basic_dns_data(dhcp=False):
    for name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
        Domain.objects.create(name=name)

    if dhcp:
        Vrf.objects.create(name='test_vrf')


def create_zone(name):
    domain = Domain.objects.create(name=name)
    return make_root(domain)


def make_root(domain):
    Nameserver.objects.create(domain=domain, server='ns1.unused')
    SOA.objects.create(
        primary='ns1.unused', contact='webmaster.unused', root_domain=domain)
    return Domain.objects.get(pk=domain.pk)  # Reload it.
