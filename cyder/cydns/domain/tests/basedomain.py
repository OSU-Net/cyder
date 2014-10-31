from django.test import TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.tests.utils import DNSTest, make_root


class BaseDomain(DNSTest):
    def setUp(self):
        super(BaseDomain, self).setUp()

        Domain.objects.create(name="128.in-addr.arpa")

        self.f_c = Domain.create_recursive(name='foo.poo')
        make_root(self.f_c)

        self.net = Network.objects.create(network_str='10.2.3.0/29')
        self.sr = Range.objects.create(
            network=self.net, range_type=STATIC, start_str='10.2.3.1',
            end_str='10.2.3.4')
