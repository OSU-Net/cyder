from gettext import gettext as gt
import random
import simplejson as json
import string
import time

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory

from cyder.base.tests import TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_prefix_to_reverse_name
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.view.models import View
from cyder.cydns.utils import ensure_domain, prune_tree


class DNSTest(TestCase):
    def setUp(self):
        Domain.objects.create(name='arpa')
        Domain.objects.create(name='in-addr.arpa')
        Domain.objects.create(name='ip6.arpa')

        self.ctnr = Ctnr.objects.create(name='test_ctnr')


def get_post_data(random_str, suffix):
    """Return a valid set of data"""
    return {
        'root_domain': '{0}{1}'.format(random_str, suffix),
        'soa_primary': 'ns1.mozilla.com',
        'soa_contact': 'noc.mozilla.com',
        'nameserver_1': 'ns1.mozilla.com',
        'ttl_1': '1234'
    }


def create_reverse_domain(ip, ip_type):
    return Domain.create_recursive(name=ip_prefix_to_reverse_name(ip, ip_type))


def create_zone(name):
    domain = Domain.objects.create(name=name)
    return make_root(domain)


def make_root(domain):
    Nameserver.objects.create(domain=domain, server='ns1.unused')
    SOA.objects.create(
        primary='ns1.unused', contact='webmaster.unused', root_domain=domain)
    return domain.reload()
