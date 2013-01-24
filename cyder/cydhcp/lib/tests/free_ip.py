from django.test import TestCase

from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.lib.utils import calc_free_ips_str
from cyder.cydhcp.lib.utils import create_ipv4_intr_from_range
from cyder.cydns.domain.models import Domain
from cyder.cydns.soa.models import SOA

from cyder.core.system.models import System


class LibTestsFreeIP(TestCase):
    def setUp(self):
        self.system = System()
        Domain.objects.get_or_create(name="com")
        d1, _ = Domain.objects.get_or_create(name="mozilla.com")
        soa, _ = SOA.objects.get_or_create(
            primary="fo.bar", contact="foo.bar.com",
            description="foo bar")
        self.s = soa
        d1.soa = soa
        d1.save()

        v, _ = Vlan.objects.get_or_create(name="private", number=3)
        s, _ = Site.objects.get_or_create(name="phx1")
        s1, _ = Site.objects.get_or_create(name="corp", parent=s)
        d, _ = Domain.objects.get_or_create(name="phx1.mozilla.com")
        d.soa = soa
        d.save()
        d1, _ = Domain.objects.get_or_create(name="corp.phx1.mozilla.com")
        d1.soa = soa
        d1.save()
        d2, _ = Domain.objects.get_or_create(
            name="private.corp.phx1.mozilla.com")
        d2.soa = soa
        d2.save()

        d, _ = Domain.objects.get_or_create(name="arpa")
        d, _ = Domain.objects.get_or_create(name="in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="ip6.arpa")
        d, _ = Domain.objects.get_or_create(name="15.in-addr.arpa")
        d, _ = Domain.objects.get_or_create(name="2.in-addr.arpa")
        n = Network(network_str="15.0.0.0/8", ip_type="4")
        n.clean()
        n.site = s1
        n.vlan = v
        n.save()

        r = Range(start_str="15.0.0.0", end_str="15.0.0.10",
                  network=n)
        r.clean()
        r.save()

    def test1_free_ip_count(self):
        # Add a bunch of interfaces and make sure the calc_free_ips function is
        # working
        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 4)
        intr, errors = create_ipv4_intr_from_range("foo",
                "private.corp.phx1.mozilla.com", self.system,
                "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 3)

        intr, errors = create_ipv4_intr_from_range("foo",
                "private.corp.phx1.mozilla.com", self.system,
                "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 2)

        intr, errors = create_ipv4_intr_from_range("foo",
                "private.corp.phx1.mozilla.com", self.system,
                "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 1)

        intr, errors = create_ipv4_intr_from_range("foo",
                "private.corp.phx1.mozilla.com", self.system,
                "11:22:33:44:55:66", "15.0.0.200", "15.0.0.204")
        intr.save()
        self.assertEqual(errors, None)
        self.assertTrue(isinstance(intr, StaticInterface))

        count = calc_free_ips_str("15.0.0.200", "15.0.0.204")
        self.assertEqual(count, 0)
