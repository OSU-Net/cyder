from django.test import TestCase

from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.lib.utils import calc_free_ips_str
from cyder.cydhcp.lib.utils import create_ipv4_intr_from_range
from cyder.cydns.domain.models import Domain

from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr

from cyder.cydns.tests.utils import create_fake_zone, create_zone


class LibTestsFreeIP(TestCase):

    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.system = System(name='test_system')
        self.system.save()

        d1 = create_fake_zone("oregonstate.com", suffix="")
        soa = d1.soa

        v, _ = Vlan.objects.get_or_create(name="private", number=3)
        s, _ = Site.objects.get_or_create(name="phx1")
        s1, _ = Site.objects.get_or_create(name="corp", parent=s)
        d, _ = Domain.objects.get_or_create(name="phx1.oregonstate.com")
        d.soa = soa
        d.save()
        d1, _ = Domain.objects.get_or_create(name="corp.phx1.oregonstate.com")
        d1.soa = soa
        d1.save()
        d2, _ = Domain.objects.get_or_create(
            name="private.corp.phx1.oregonstate.com")
        d2.soa = soa
        d2.save()
        self.ctnr.domains.add(d, d1, d2)

        for name in ("arpa", "in-addr.arpa", "ip6.arpa"):
            d, _ = Domain.objects.get_or_create(name=name)
            self.ctnr.domains.add(d)
        for name in ('2.in-addr.arpa', '15.in-addr.arpa'):
            d = create_zone(name)
            self.ctnr.domains.add(d)

        n = Network(network_str="15.0.0.0/8", ip_type="4")
        n.site = s1
        n.vlan = v
        n.save()

        self.net = Network(network_str='15.0.0.200/28')
        self.net.update_network()
        self.net.save()

        r = Range(start_str="15.0.0.200", end_str="15.0.0.204",
                  network=n, ip_type='4', range_type=STATIC)
        r.save()
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
