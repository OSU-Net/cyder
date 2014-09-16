from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.tests.utils import create_zone
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr


class V4RangeTests(TestCase):

    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.d = Domain(name="com")
        self.d.save()
        self.ctnr.domains.add(self.d)
        Domain(name="arpa").save()
        Domain(name="in-addr.arpa").save()
        create_zone('10.in-addr.arpa')
        self.s = Network(network_str="10.0.0.0/16", ip_type='4')
        self.s.update_network()
        self.s.save()

        self.s1 = Network(network_str="10.2.1.0/24", ip_type='4')
        self.s1.update_network()
        self.s1.save()

    def do_add(self, start_str, end_str, network, ip_type):
        r = Range(start_str=start_str, end_str=end_str, network=network,
                  ip_type=ip_type)
        r.__repr__()
        r.save()
        return r

    def test1_create(self):
        self.do_add(
            start_str="10.0.0.1",
            end_str="10.0.0.55",
            network=self.s,
            ip_type='4',
        )

    def test2_create(self):
        self.do_add(
            start_str="10.0.1.1",
            end_str="10.0.1.55",
            network=self.s,
            ip_type='4',
        )

    def test1_bad_create(self):
        # start == end
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.0.0",
            end_str="10.1.0.0",
            network=self.s,
            ip_type='4',
        )

    def test2_bad_create(self):
        # start > end
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.0.2",
            end_str="10.0.0.1",
            network=self.s,
            ip_type='4',
        )

    def test3_bad_create(self):
        # outside of network
        self.assertRaises(ValidationError, self.do_add,
            start_str="11.0.0.2",
            end_str="10.0.0.88",
            network=self.s,
            ip_type='4',
        )

    def test4_bad_create(self):
        # outside of network
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.2.0.0",
            end_str="10.2.1.88",
            network=self.s1,
            ip_type='4',
        )

    def test5_bad_create(self):
        def x():
            self.do_add(
                start_str="10.0.4.1",
                end_str="10.0.4.55",
                network=self.s,
                ip_type='4',
            )

        x()

        # duplicate
        self.assertRaises(ValidationError, x)

    def test6_bad_create(self):
        self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Partial overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.4.1",
            end_str="10.0.4.30",
            network=self.s,
            ip_type='4',
        )

    def test7_bad_create(self):
        self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Partial overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.4.1",
            end_str="10.0.4.56",
            network=self.s,
            ip_type='4',
        )

    def test8_bad_create(self):
        self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Full overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.4.2",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

    def test9_bad_create(self):
        # Full overlap
        self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.4.2",
            end_str="10.0.4.54",
            network=self.s,
            ip_type='4',
        )

    def test10_bad_create(self):
        def x():
            self.do_add(
                start_str="10.0.5.2",
                end_str="10.0.5.56",
                network=self.s,
                ip_type='4',
            )

        x()

        # Duplicate add
        self.assertRaises(ValidationError, x)

    def test11_bad_create(self):
        # More overlap tests
        self.do_add(
            start_str="10.0.4.5",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        self.do_add(
            start_str="10.0.4.60",
            end_str="10.0.4.63",
            network=self.s,
            ip_type='4',
        )

        self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.4",
            network=self.s,
            ip_type='4',
        )

        self.assertRaises(ValidationError, self.do_add,
            start_str="10.0.4.2",
            end_str="10.0.4.54",
            network=self.s,
            ip_type='4',
        )

    def test12_bad_create(self):
        # Update range to something outside of the subnet.
        self.do_add(
            start_str="10.0.4.5",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        self.do_add(
            start_str="10.0.4.60",
            end_str="10.0.4.63",
            network=self.s,
            ip_type='4',
        )

        r = self.do_add(
            start_str="10.0.4.1",
            end_str="10.0.4.4",
            network=self.s,
            ip_type='4',
        )

        r.end_str = "160.0.4.60"
        self.assertRaises(ValidationError, r.save)

    def test13_bad_create(self):
        def x():
            self.do_add(
                start_str="10.0.4.5",
                end_str="10.0.4.55",
                network=self.s,
                ip_type='4',
            )

        x()

        self.assertRaises(ValidationError, x)

    def test1_freeip(self):
        system = System(name='foobar')
        system.save()

        r = self.do_add(
            start_str="10.0.33.1",
            end_str="10.0.33.3",
            network=self.s,
            ip_type='4',
        )

        self.assertEqual(str(r.get_next_ip()), "10.0.33.1")
        self.assertEqual(str(r.get_next_ip()), "10.0.33.1")
        s = StaticInterface(
            label="foo1", domain=self.d, ip_type='4',
            ip_str=str(r.get_next_ip()), system=system,
            mac="00:00:00:00:00:01", ctnr=self.ctnr)
        s.save()
        self.assertEqual(str(r.get_next_ip()), "10.0.33.2")
        s = StaticInterface(
            label="foo2", domain=self.d, ip_type='4',
            ip_str=str(r.get_next_ip()), system=system,
            mac="00:00:00:00:00:01", ctnr=self.ctnr)
        s.save()
        self.assertEqual(str(r.get_next_ip()), "10.0.33.3")
        s = StaticInterface(
                label="foo3", domain=self.d, ip_type='4',
                ip_str=str(r.get_next_ip()), system=system,
                mac="00:00:00:00:00:01", ctnr=self.ctnr)
        s.save()
        self.assertEqual(r.get_next_ip(), None)
