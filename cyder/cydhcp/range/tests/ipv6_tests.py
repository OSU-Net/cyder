from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range

import ipaddr


class V6RangeTests(TestCase):
    def setUp(self):
        self.s = Network.objects.create(
            network_str="1234:1234:1234::/16", ip_type='6')
        self.s1 = Network.objects.create(
            network_str="1234:1134:1234::/32", ip_type='6')
        self.s2 = Network.objects.create(network_str="fff::/4", ip_type='6')
        self.s3 = Network.objects.create(network_str="ffff::/4", ip_type='6')

    def do_add(self, start_str, end_str, network, ip_type):
        r = Range.objects.create(
            start_str=start_str, end_str=end_str, network=network,
            ip_type=ip_type)
        r.__repr__()
        return r

    def test1_create(self):
        self.do_add(
            start_str="1234:1234:1234:1::",
            end_str="1234:1234:1234:1234:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test2_create(self):
        self.do_add(
            start_str="1234:1234:1234:1234::",
            end_str="1234:1234:1235:1234:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test3_create(self):
        r = self.do_add(
            start_str="ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0",
            end_str="ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe",
            network=self.s3,
            ip_type='6',
        )
        self.assertEqual(r.start_upper, 0xffffffffffffffff)
        self.assertEqual(r.start_lower, 0xfffffffffffffff0)
        self.assertEqual(r.end_upper, 0xffffffffffffffff)
        self.assertEqual(r.end_lower, 0xfffffffffffffffe)

    def test1_bad_create(self):
        def x():
            self.do_add(
                start_str="fe8:4:5::",
                end_str="fe8:4:55::",
                network=self.s2,
                ip_type='6',
            )

        x()

        self.assertRaises(ValidationError, x)

    def test2_bad_create(self):
        # start > end
        self.assertRaises(ValidationError, self.do_add,
            start_str="1234:1235:1234:1235::",
            end_str="1234:1235:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test3_bad_create(self):
        # outside of network
        self.assertRaises(ValidationError, self.do_add,
            start_str="2235:1235:1234:1233::",
            end_str="2235:1235:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test4_bad_create(self):
        # outside of network
        self.assertRaises(ValidationError, self.do_add,
            start_str="1234:1234:1234:1::",
            end_str="1234:1234:1234:1234:1234:1234::",
            network=self.s1,
            ip_type='6',
        )

    def test5_bad_create(self):
        self.do_add(
            start_str="1234:123e:1234:1234::",
            end_str="1234:123e:1235:1234:1234:1234::",
            network=self.s,
            ip_type='6',
        )

        # duplicate
        self.assertRaises(ValidationError, self.do_add,
            start_str="1234:123e:1234:1234::",
            end_str="1234:123e:1235:1234:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test6_bad_create(self):
        self.do_add(
            start_str="fe:1::",
            end_str="fe:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Partial overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="fe:1::",
            end_str="fe:1:3::",
            network=self.s2,
            ip_type='6',
        )

    def test7_bad_create(self):
        self.do_add(
            start_str="fe1:1::",
            end_str="fe1:1:3::",
            network=self.s2,
            ip_type='6',
        )

        # Partial overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="fe1:1::",
            end_str="fe1:1:4::",
            network=self.s2,
            ip_type='6',
        )

    def test8_bad_create(self):
        self.do_add(
            start_str="fe2:1::",
            end_str="fe2:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Full overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="fe2:1:2::",
            end_str="fe2:1:4::",
            network=self.s2,
            ip_type='6',
        )

    def test9_bad_create(self):
        self.do_add(
            start_str="fe3:1:1::",
            end_str="fe3:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Full overlap
        self.assertRaises(ValidationError, self.do_add,
            start_str="fe3:1:2::",
            end_str="fe3:1:3::",
            network=self.s2,
            ip_type='6',
        )

    def test10_bad_create(self):
        def x():
            self.do_add(
                start_str="fe5:1:56::",
                end_str="fe5:1:57::",
                network=self.s2,
                ip_type='6',
            )

        x()

        # Duplicate add
        self.assertRaises(ValidationError, x)

    def test11_bad_create(self):
        # More overlap tests
        self.do_add(
            start_str="fe6:4:5::",
            end_str="fe6:4:55::",
            network=self.s2,
            ip_type='6',
        )

        self.do_add(
            start_str="fe6:4:60::",
            end_str="fe6:4:63::",
            network=self.s2,
            ip_type='6',
        )

        self.do_add(
            start_str="fe6:4:1::",
            end_str="fe6:4:4::",
            network=self.s2,
            ip_type='6',
        )

        self.assertRaises(ValidationError, self.do_add,
            start_str="fe6:4:2::",
            end_str="fe6:4:54::",
            network=self.s2,
            ip_type='6',
        )

    def test12_bad_create(self):
        self.do_add(
            start_str="fe7:4:5::",
            end_str="fe7:4:55::",
            network=self.s2,
            ip_type='6',
        )

        self.do_add(
            start_str="fe7:4:60::",
            end_str="fe7:4:63::",
            network=self.s2,
            ip_type='6',
        )

        r = self.do_add(
            start_str="fe7:4:1::",
            end_str="fe7:4:4::",
            network=self.s2,
            ip_type='6',
        )

        # Update range to something outside of the subnet.
        r.end_str = "ffff:ffff:ffff::"
        self.assertRaises(ValidationError, r.save)
