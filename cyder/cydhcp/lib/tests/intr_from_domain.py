from django.test import TestCase

from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.lib.utils import *

from cyder.cydns.domain.models import Domain

from cyder.core.system.models import System


class LibTestsDomain(TestCase):

    def setUp(self):
        self.system = System()
        Domain.objects.get_or_create(name="com")
        Domain.objects.get_or_create(name="mozilla.com")

    def test0_create_ipv4_interface(self):
        intr, errors = create_ipv4_interface(
            label="", vlan_str="db", site_str="scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("label" in errors)

    def test1_create_ipv4_interface(self):
        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="db", site_str="scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("site" in errors)

    def test2_create_ipv4_interface(self):
        s, _ = Site.objects.get_or_create(name="scl3")
        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="db", site_str="scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("site" not in errors)
        self.assertTrue("vlan" in errors)

    def test3_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="db3", number=3)
        s, _ = Site.objects.get_or_create(name="scl33")
        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="db3", site_str="scl33",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("vlan" not in errors)
        self.assertTrue("site" not in errors)
        self.assertTrue("domain" in errors)

    def test4_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="db4", number=3)
        s, _ = Site.objects.get_or_create(name="scl34")
        d, _ = Domain.objects.get_or_create(name="scl34.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="db4.scl34.mozilla.com")
        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="db4", site_str="scl34",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("vlan" not in errors)
        self.assertTrue("site" not in errors)
        self.assertTrue("domain" not in errors)
        self.assertTrue("network" in errors)

    def test5_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="5db", number=3)
        s, _ = Site.objects.get_or_create(name="5scl3")
        d, _ = Domain.objects.get_or_create(name="5scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="5db.5scl3.mozilla.com")
        n = Network(network_str="10.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s
        n.vlan = v
        n.save()
        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="5db", site_str="5scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("vlan" not in errors)
        self.assertTrue("site" not in errors)
        self.assertTrue("domain" not in errors)
        self.assertTrue("network" not in errors)
        self.assertTrue("range" in errors)

    def test6_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="6db", number=3)
        s, _ = Site.objects.get_or_create(name="6scl3")
        d, _ = Domain.objects.get_or_create(name="6scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="6db.6scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="11.in-addr.arpa")
        n = Network(network_str="11.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s
        n.vlan = v
        n.save()

        r = Range(start_str="11.0.0.0", end_str="11.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        s = StaticInterface(label="fab", domain=d, ip_type="4",
                            ip_str="11.0.0.0", system=self.system,
                            mac="00:00:00:00:00:00")
        s.clean()
        s.save()

        s = StaticInterface(label="fab", domain=d, ip_type="4",
                            ip_str="11.0.0.1", system=self.system,
                            mac="00:00:00:00:00:00")
        s.clean()
        s.save()

        s = StaticInterface(label="fab", domain=d, ip_type="4",
                            ip_str="11.0.0.2", system=self.system,
                            mac="00:00:00:00:00:00")
        s.clean()
        s.save()

        intr, errors = create_ipv4_interface(
            "foo", "6db", "6scl3", self.system,
            "11:22:33:44:55:66", "mozilla.com")
        self.assertEqual(intr, None)
        self.assertTrue("vlan" not in errors)
        self.assertTrue("site" not in errors)
        self.assertTrue("domain" not in errors)
        self.assertTrue("network" not in errors)
        self.assertTrue("range" not in errors)
        self.assertTrue("ip" in errors)

    def test7_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="7db", number=3)
        s, _ = Site.objects.get_or_create(name="7scl3")
        d, _ = Domain.objects.get_or_create(name="7scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="7db.7scl3.mozilla.com")

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="12.in-addr.arpa")
        n = Network(network_str="12.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s
        n.vlan = v
        n.save()

        r = Range(start_str="12.0.0.0", end_str="12.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="7db", site_str="7scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

    def test8_create_ipv4_interface(self):
        v, _ = Vlan.objects.get_or_create(name="8db", number=3)
        s, _ = Site.objects.get_or_create(name="8scl3")
        s1, _ = Site.objects.get_or_create(name="8dmz", parent=s)
        d, _ = Domain.objects.get_or_create(name="8scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="8dmz.8scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="8db.8dmz.8scl3.mozilla.com")

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="15.in-addr.arpa")
        n = Network(network_str="15.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s1
        n.vlan = v
        n.save()

        r = Range(start_str="15.0.0.0", end_str="15.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        intr, errors = create_ipv4_interface(
            label="foo", vlan_str="8db", site_str="8dmz.8scl3",
            system=self.system, mac="11:22:33:44:55:66",
            domain_suffix="mozilla.com")
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

    def test1_create_ipv4_interface_from_domain(self):

        v, _ = Vlan.objects.get_or_create(name="private", number=3)
        s, _ = Site.objects.get_or_create(name="phx1")
        d, _ = Domain.objects.get_or_create(name="phx1.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="private.phx1.mozilla.com")

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="13.in-addr.arpa")
        n = Network(network_str="13.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s
        n.vlan = v
        n.save()

        r = Range(start_str="13.0.0.0", end_str="13.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        intr, errors = create_ipv4_intr_from_domain(
            label="foo", domain_name="private.phx1", system=self.system,
            mac="11:22:33:44:55:66")
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

    def test2_create_ipv4_interface_from_domain(self):

        v, _ = Vlan.objects.get_or_create(name="private", number=3)
        s, _ = Site.objects.get_or_create(name="phx1")
        s1, _ = Site.objects.get_or_create(name="corp", parent=s)
        d, _ = Domain.objects.get_or_create(name="phx1.mozilla.com")
        d1, _ = Domain.objects.get_or_create(name="corp.phx1.mozilla.com")
        d2, _ = Domain.objects.get_or_create(
            name="private.corp.phx1.mozilla.com")

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="14.in-addr.arpa")
        n = Network(network_str="14.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s1
        n.vlan = v
        n.save()

        r = Range(start_str="14.0.0.0", end_str="14.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        intr, errors = create_ipv4_intr_from_domain(
            "foo", "private.corp.phx1", self.system,
            "11:22:33:44:55:66")
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

    def test1_create_ipv4_interface_network_str(self):
        v, _ = Vlan.objects.get_or_create(name="12db", number=3)
        s, _ = Site.objects.get_or_create(name="12scl3")
        d, _ = Domain.objects.get_or_create(name="12scl3.mozilla.com")
        d, _ = Domain.objects.get_or_create(name="12db.12scl3.mozilla.com")

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="12.in-addr.arpa")
        n = Network(network_str="12.0.0.0/24", ip_type="4")
        n.clean()
        n.site = s
        n.vlan = v
        n.save()

        n1 = Network(network_str="12.0.1.0/24", ip_type="4")
        n1.clean()
        n1.site = s
        n1.vlan = v
        n1.save()

        r = Range(start_str="12.0.0.0", end_str="12.0.0.2",
                  network=n, ip_type='4')
        r.clean()
        r.save()

        r1 = Range(start_str="12.0.1.0", end_str="12.0.1.2",
                   network=n1, ip_type='4')
        r1.clean()
        r1.save()

        intr, errors = create_ipv4_interface(
            "foo", "12db", "12scl3", self.system,
            "11:22:33:4e:55:66", "mozilla.com")
        self.assertTrue('network' in errors)
        self.assertTrue(
            errors['network'][0].find("too many networks associated") != -1)
        # Look for a non-existant network
        intr, errors = create_ipv4_interface(
            "foo", "12db", "12scl3", self.system,
            "11:22:33:4e:55:66", "mozilla.com", network_str="12.0.99.0/24")
        self.assertTrue('network' in errors)
        intr, errors = create_ipv4_interface(
            "foo", "12db", "12scl3", self.system,
            "11:22:33:4e:55:66", "mozilla.com", network_str="12.0.0.0/24")
        self.assertFalse(errors)
        self.assertTrue(isinstance(intr, StaticInterface))
