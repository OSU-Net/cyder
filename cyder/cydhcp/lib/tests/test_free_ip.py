from django.test import TestCase

from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.lib.utils import (
    calc_free_ips_str, create_ipv4_intr_from_range)
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydns.domain.models import Domain
from cyder.cydns.tests.utils import create_zone


class LibTestsFreeIP(TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.system = System(name='test_system')
        self.system.save()

        Domain.objects.create(name='com')
        d1 = create_zone('oregonstate.com')
        soa = d1.soa

        v = Vlan.objects.create(name="private", number=3)
        s = Site.objects.create(name="phx1")
        s1 = Site.objects.create(name="corp", parent=s)

        names = (
            'phx1.oregonstate.com', 'corp.phx1.oregonstate.com',
            'private.corp.phx1.oregonstate.com', 'arpa', 'in-addr.arpa',
            'ip6.arpa')
        for name in names:
            d = Domain.objects.create(name=name)
            self.ctnr.domains.add(d)

        for name in ('2.in-addr.arpa', '15.in-addr.arpa'):
            d = create_zone(name)
            self.ctnr.domains.add(d)

        n = Network.objects.create(
            network_str="15.0.0.0/8", ip_type="4", site=s1, vlan=v)

        self.net = Network.objects.create(network_str='15.0.0.200/28')

        r = Range.objects.create(
            start_str="15.0.0.200", end_str="15.0.0.204", network=n,
            ip_type='4', range_type=STATIC)
        self.ctnr.ranges.add(r)

    def test1_free_ip_count(self):
        # Add a bunch of interfaces and make sure the calc_free_ips function is
        # working
        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 4)
        intr, errors = create_ipv4_intr_from_range(
            "foo1", "private.corp.phx1.oregonstate.com", self.system,
            "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204", ctnr=self.ctnr)
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 3)

        intr, errors = create_ipv4_intr_from_range(
            "foo2", "private.corp.phx1.oregonstate.com", self.system,
            "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204", ctnr=self.ctnr)
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 2)

        intr, errors = create_ipv4_intr_from_range(
            "foo3", "private.corp.phx1.oregonstate.com", self.system,
            "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204", ctnr=self.ctnr)
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 1)

        intr, errors = create_ipv4_intr_from_range(
            "foo4", "private.corp.phx1.oregonstate.com", self.system,
            "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204", ctnr=self.ctnr)
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 0)
