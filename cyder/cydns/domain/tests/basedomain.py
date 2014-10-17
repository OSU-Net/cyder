from django.test import TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydns.domain.models import Domain
from cyder.cydns.tests.utils import create_basic_dns_data, make_root

from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC


class BaseDomain(TestCase):
    def setUp(self):
        create_basic_dns_data()

        Domain.objects.create(name="128.in-addr.arpa")
        self.ctnr = Ctnr.objects.create(name="abloobloobloo")

        c = self.create_domain(name='poo')

        self.assertFalse(c.purgeable)
        self.f_c = self.create_domain(name='foo.poo')
        make_root(self.f_c)

        self.net = Network.objects.create(network_str='10.2.3.0/29')
        self.sr = Range.objects.create(
            network=self.net, range_type=STATIC, start_str='10.2.3.1',
            end_str='10.2.3.4')

    def create_domain(self, *args, **kwargs):
        d = Domain.objects.create(*args, **kwargs)
        self.ctnr.domains.add(d)
        return d
