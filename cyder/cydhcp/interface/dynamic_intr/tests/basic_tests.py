from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf


class BasicDynamicInterfaceTests(TestCase):
    def setUp(self):
        self.c = Ctnr.objects.create(name='Test_container')

        d1 = Domain.objects.create(name='com')
        self.c.domains.add(d1)

        d2 = Domain.objects.create(name='example.com')
        self.c.domains.add(d2)

        v = Vrf.objects.get(name='Legacy')

        n = Network.objects.create(
            vrf=v, ip_type='4', network_str='192.168.0.0/24')

        self.r1 = Range.objects.create(
            network=n, domain=d2, range_type='dy', start_str='192.168.0.2',
            end_str='192.168.0.20')
        self.c.ranges.add(self.r1)

        self.r2 = Range.objects.create(
            network=n, domain=d2, range_type='dy', start_str='192.168.0.21',
            end_str='192.168.0.40')
        self.c.ranges.add(self.r2)

        self.s1 = System.objects.create(name='foo')

        self.s2 = System.objects.create(name='bar')

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            DynamicInterface.objects.create(
                ctnr=self.c, system=self.s1, range=self.r1,
                mac='11:11:22:22:33:33'),
            DynamicInterface.objects.create(
                ctnr=self.c, system=self.s2, range=self.r1,
                mac='44:44:55:55:66:66'),
        )

    def test_same_mac_different_range(self):
        DynamicInterface.objects.create(
            ctnr=self.c, system=self.s1, range=self.r1,
            mac='12:34:56:78:9a:bc')
        DynamicInterface.objects.create(
            ctnr=self.c, system=self.s2, range=self.r2,
            mac='12:34:56:78:9a:bc')

    def test_same_mac_same_range(self):
        DynamicInterface.objects.create(
            ctnr=self.c, system=self.s1, range=self.r1,
            mac='12:34:56:78:9a:bc')

        self.assertRaises(
            ValidationError, DynamicInterface.objects.create,
            ctnr=self.c, system=self.s2, range=self.r1,
            mac='12:34:56:78:9a:bc')
