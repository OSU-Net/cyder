from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.tests.utils import create_zone
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr


class V4RangeTests(TestCase, ModelTestMixin):
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')
        self.d = Domain.objects.create(name="com")
        self.ctnr.domains.add(self.d)

        Domain.objects.create(name="arpa")
        Domain.objects.create(name="in-addr.arpa")
        create_zone('10.in-addr.arpa')

        self.s = Network.objects.create(network_str="10.0.0.0/16", ip_type='4')
        self.s1 = Network.objects.create(
            network_str="10.2.1.0/24", ip_type='4')

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Range.objects.create(
                start_str="10.0.0.1",
                end_str="10.0.0.55",
                network=self.s,
                ip_type='4',
            ),
            Range.objects.create(
                start_str="10.0.1.1",
                end_str="10.0.1.55",
                network=self.s,
                ip_type='4',
            ),
        )

    def test_bad_create1(self):
        # start > end
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.0.2",
            end_str="10.0.0.1",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create2(self):
        # outside of network
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="11.0.0.2",
            end_str="10.0.0.88",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create3(self):
        # outside of network
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.2.0.0",
            end_str="10.2.1.88",
            network=self.s1,
            ip_type='4',
        )

    def test_bad_create4(self):
        def x():
            Range.objects.create(
                start_str="10.0.4.1",
                end_str="10.0.4.55",
                network=self.s,
                ip_type='4',
            )

        x()

        # duplicate
        self.assertRaises(ValidationError, x)

    def test_bad_create5(self):
        Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Partial overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.4.1",
            end_str="10.0.4.30",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create6(self):
        Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Partial overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.4.1",
            end_str="10.0.4.56",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create7(self):
        Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        # Full overlap
        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.4.2",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create8(self):
        # Full overlap
        Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.4.2",
            end_str="10.0.4.54",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create9(self):
        # More overlap tests
        Range.objects.create(
            start_str="10.0.4.5",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        Range.objects.create(
            start_str="10.0.4.60",
            end_str="10.0.4.63",
            network=self.s,
            ip_type='4',
        )

        Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.4",
            network=self.s,
            ip_type='4',
        )

        self.assertRaises(
            ValidationError, Range.objects.create,
            start_str="10.0.4.2",
            end_str="10.0.4.54",
            network=self.s,
            ip_type='4',
        )

    def test_bad_create10(self):
        # Update range to something outside of the subnet.
        Range.objects.create(
            start_str="10.0.4.5",
            end_str="10.0.4.55",
            network=self.s,
            ip_type='4',
        )

        Range.objects.create(
            start_str="10.0.4.60",
            end_str="10.0.4.63",
            network=self.s,
            ip_type='4',
        )

        r = Range.objects.create(
            start_str="10.0.4.1",
            end_str="10.0.4.4",
            network=self.s,
            ip_type='4',
        )

        r.end_str = "160.0.4.60"
        self.assertRaises(ValidationError, r.save)

    def test_duplicate(self):
        def x():
            Range.objects.create(
                start_str="10.0.4.5",
                end_str="10.0.4.55",
                network=self.s,
                ip_type='4',
            )

        x()
        self.assertRaises(ValidationError, x)

    def test_freeip(self):
        system = System(name='foobar')
        system.save()

        r = Range.objects.create(
            start_str="10.0.33.1",
            end_str="10.0.33.3",
            network=self.s,
            ip_type='4',
        )

        self.assertEqual(str(r.get_next_ip()), "10.0.33.1")
        self.assertEqual(str(r.get_next_ip()), "10.0.33.1")
        s = StaticInterface.objects.create(
            label="foo1", domain=self.d, ip_type='4',
            ip_str=str(r.get_next_ip()), system=system,
            mac="00:00:00:00:00:01", ctnr=self.ctnr)
        self.assertEqual(str(r.get_next_ip()), "10.0.33.2")
        s = StaticInterface.objects.create(
            label="foo2", domain=self.d, ip_type='4',
            ip_str=str(r.get_next_ip()), system=system,
            mac="00:00:00:00:00:01", ctnr=self.ctnr)
        self.assertEqual(str(r.get_next_ip()), "10.0.33.3")
        s = StaticInterface.objects.create(
            label="foo3", domain=self.d, ip_type='4',
            ip_str=str(r.get_next_ip()), system=system,
            mac="00:00:00:00:00:01", ctnr=self.ctnr)
        self.assertEqual(r.get_next_ip(), None)
