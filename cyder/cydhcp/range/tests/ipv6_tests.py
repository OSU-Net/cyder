import ipaddr
from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range


class V6RangeTests(TestCase, ModelTestMixin):
    def setUp(self):
        self.s = Network.objects.create(
            network_str="1234:1234:1234::/16", ip_type='6')
        self.s1 = Network.objects.create(
            network_str="eeee:eeee:eeee::/32", ip_type='6')
        self.s2 = Network.objects.create(network_str="fff::/4", ip_type='6')
        self.s3 = Network.objects.create(network_str="ffff::/4", ip_type='6')

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Range.objects.create(
                start_str="1234:1234:1234:1::",
                end_str="1234:1234:1234:1234:1234:1234::",
                network=self.s,
                ip_type='6',
            ),
            Range.objects.create(
                start_str="1234:1234:1234:cdEf::",
                end_str="1234:1234:1234:CDeF:cDeF:CDEF::",
                network=self.s,
                ip_type='6',
            ),
            Range.objects.create(
                start_str="Ffff:fffF:ffff:ffff:fFFF:FFFf:fFFf:fff0",
                end_str="fFFF:FFFf:ffff:ffff:Ffff:fffF:FffF:fffe",
                network=self.s3,
                ip_type='6',
            ),
        )

    def test_upper_lower(self):
        r = Range.objects.create(
            start_str="ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0",
            end_str="ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe",
            network=self.s3,
            ip_type='6',
        )
        self.assertEqual(r.start_upper, 0xffffffffffffffff)
        self.assertEqual(r.start_lower, 0xfffffffffffffff0)
        self.assertEqual(r.end_upper, 0xffffffffffffffff)
        self.assertEqual(r.end_lower, 0xfffffffffffffffe)

    def test_bad_create1(self):
        # start > end
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="1234:1235:1234:1235::",
            end_str="1234:1235:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test_bad_create2(self):
        # outside of network
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="2235:1235:1234:1233::",
            end_str="2235:1235:1234:1234::",
            network=self.s,
            ip_type='6',
        )

    def test_bad_create3(self):
        # outside of network
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="1234:1234:1234:1::",
            end_str="1234:1234:1234:1234:1234:1234::",
            network=self.s1,
            ip_type='6',
        )


    def test_bad_create4(self):
        Range.objects.create(
            start_str="fe:1::",
            end_str="fe:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Partial overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="fe:1::",
            end_str="fe:1:3::",
            network=self.s2,
            ip_type='6',
        )

    def test_bad_create5(self):
        Range.objects.create(
            start_str="fe1:1::",
            end_str="fe1:1:3::",
            network=self.s2,
            ip_type='6',
        )

        # Partial overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="fe1:1::",
            end_str="fe1:1:4::",
            network=self.s2,
            ip_type='6',
        )

    def test_bad_create6(self):
        Range.objects.create(
            start_str="fe2:1::",
            end_str="fe2:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Full overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="fe2:1:2::",
            end_str="fe2:1:4::",
            network=self.s2,
            ip_type='6',
        )

    def test_bad_create7(self):
        Range.objects.create(
            start_str="fe3:1:1::",
            end_str="fe3:1:4::",
            network=self.s2,
            ip_type='6',
        )

        # Full overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="fe3:1:2::",
            end_str="fe3:1:3::",
            network=self.s2,
            ip_type='6',
        )

    def test_bad_create8(self):
        def x():
            Range.objects.create(
                start_str="fe5:1:56::",
                end_str="fe5:1:57::",
                network=self.s2,
                ip_type='6',
            )

        x()

        # Duplicate add
        self.assertRaises(ValidationError, x)

    def test_bad_create9(self):
        # More overlap tests
        Range.objects.create(
            start_str="fe6:4:5::",
            end_str="fe6:4:55::",
            network=self.s2,
            ip_type='6',
        )

        Range.objects.create(
            start_str="fe6:4:60::",
            end_str="fe6:4:63::",
            network=self.s2,
            ip_type='6',
        )

        Range.objects.create(
            start_str="fe6:4:1::",
            end_str="fe6:4:4::",
            network=self.s2,
            ip_type='6',
        )

        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="fe6:4:2::",
            end_str="fe6:4:54::",
            network=self.s2,
            ip_type='6',
        )

    def test_bad_create10(self):
        Range.objects.create(
            start_str="fe7:4:5::",
            end_str="fe7:4:55::",
            network=self.s2,
            ip_type='6',
        )

        Range.objects.create(
            start_str="fe7:4:60::",
            end_str="fe7:4:63::",
            network=self.s2,
            ip_type='6',
        )

        r = Range.objects.create(
            start_str="fe7:4:1::",
            end_str="fe7:4:4::",
            network=self.s2,
            ip_type='6',
        )

        # Update range to something outside of the subnet.
        r.end_str = "ffff:ffff:ffff::"
        self.assertRaises(ValidationError, r.save)

    def test_duplicate(self):
        def x():
            Range.objects.create(
                start_str="1234:123e:1234:1234::",
                end_str="1234:123e:1235:1234:1234:1234::",
                network=self.s,
                ip_type='6',
            )

        x()
        self.assertRaises(ValidationError, x)
