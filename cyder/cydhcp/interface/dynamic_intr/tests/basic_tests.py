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
        self.c = Ctnr(name='Test_container')
        self.c.save()

        d1 = Domain(name='com', )
        d1.save()
        self.c.domains.add(d1)

        d2 = Domain(name='example.com')
        d2.save()
        self.c.domains.add(d2)

        v, created = Vrf.objects.get_or_create(name='Legacy')

        n = Network(vrf=v, ip_type='4', network_str='192.168.0.0/24')
        n.save()

        self.r1 = Range(
            network=n, domain=d2, range_type='dy', start_str='192.168.0.2',
            end_str='192.168.0.20'
        )
        self.r1.save()
        self.c.ranges.add(self.r1)

        self.r2 = Range(
            network=n, domain=d2, range_type='dy', start_str='192.168.0.21',
            end_str='192.168.0.40'
        )
        self.r2.save()
        self.c.ranges.add(self.r2)

        self.s1 = System(name='foo')
        self.s1.save()

        self.s2 = System(name='bar')
        self.s2.save()

    def test_same_mac_different_range(self):
        i1 = DynamicInterface(
            ctnr=self.c, system=self.s1, range=self.r1, mac='12:34:56:78:9a:bc'
        )
        i1.save()

        i2 = DynamicInterface(
            ctnr=self.c, system=self.s2, range=self.r2, mac='12:34:56:78:9a:bc'
        )
        i2.save()

    def test_same_mac_same_range(self):
        i1 = DynamicInterface(
            ctnr=self.c, system=self.s1, range=self.r1, mac='12:34:56:78:9a:bc'
        )
        i1.save()

        with self.assertRaises(ValidationError):
            i2 = DynamicInterface(
                ctnr=self.c, system=self.s2, range=self.r1,
                mac='12:34:56:78:9a:bc'
            )
            i2.save()
