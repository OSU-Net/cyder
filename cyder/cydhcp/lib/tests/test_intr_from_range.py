from django.test import TestCase

from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.lib.utils import create_ipv4_intr_from_range

from cyder.cydns.domain.models import Domain

from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr

from cyder.cydns.tests.utils import create_fake_zone, create_zone


class LibTestsRange(TestCase):

    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.system = System(name='test_system')
        self.system.save()
        d1 = create_fake_zone("oregonstate.com", suffix="")
        soa = d1.soa
        self.soa = soa

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

        for name in ("arpa", "in-addr.arpa"):
            d, _ = Domain.objects.get_or_create(name=name)
            self.ctnr.domains.add(d)
        d = create_zone("15.in-addr.arpa")
        self.ctnr.domains.add(d)

        n = Network(network_str="15.0.0.0/8", ip_type="4")
        n.site = s1
        n.vlan = v
        n.save()

        r1 = Range(start_str="15.0.0.0", end_str="15.0.0.10",
                   network=n, ip_type='4', range_type=STATIC)
        r1.save()

        r2 = Range(start_str="15.0.0.20", end_str="15.0.0.22",
                   network=n, ip_type='4', range_type=STATIC)
        r2.save()

        self.ctnr.ranges.add(r1, r2)

    def test1_create_ipv4_interface_from_range(self):
        intr, errors = create_ipv4_intr_from_range(
            label="foo", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.1", range_end_str="15.0.0.3")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.1")

    def test2_create_ipv4_interface_from_range(self):
        # test soa inherit
        intr, errors = create_ipv4_intr_from_range(
            label="foo", system=self.system, mac="11:22:33:44:55:66",
            domain_name="superprivate.foo.corp.phx1.oregonstate.com",
            range_start_str="15.0.0.20", range_end_str="15.0.0.22",
            ctnr=self.ctnr)
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.20")
        self.assertEqual(intr.domain.soa, self.soa)
        self.assertEqual(
            intr.domain.name, "superprivate.foo.corp.phx1.oregonstate.com")
        self.assertEqual(
            intr.domain.master_domain.name, "foo.corp.phx1.oregonstate.com")
        self.assertEqual(intr.domain.master_domain.soa, self.soa)

    def test3_create_ipv4_interface_from_range(self):
        # Test for an error when all the IP's are in use.
        intr, errors = create_ipv4_intr_from_range(
            label="foo1", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.2", range_end_str="15.0.0.5")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.2")

        intr, errors = create_ipv4_intr_from_range(
            label="foo2", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.2", range_end_str="15.0.0.5")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.3")

        intr, errors = create_ipv4_intr_from_range(
            label="foo3", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.2", range_end_str="15.0.0.5")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.4")

        intr, errors = create_ipv4_intr_from_range(
            label="foo4", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.2", range_end_str="15.0.0.5")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))
        self.assertEqual(intr.ip_str, "15.0.0.5")

        intr, errors = create_ipv4_intr_from_range(
            label="foo5", domain_name="private.corp.phx1.oregonstate.com",
            system=self.system, mac="11:22:33:44:55:66", ctnr=self.ctnr,
            range_start_str="15.0.0.2", range_end_str="15.0.0.5")
        self.assertEqual(intr, None)
        self.assertTrue("ip" in errors)
