from cyder.base.tests import ModelTestMixin, TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.tests.utils import create_zone
from cyder.cydns.view.models import View


class ViewTests(TestCase, ModelTestMixin):
    """
    Cases we need to cover:
    1) Give an A/PTR/StaticInterface private IP and the private view.
        * save, *no* ValidationError raised

    The following cases were determined to be an unnecessary feature:
    2) Give an A/PTR/StaticInterface private IP and the public view.
        * save, ValidationError raised
    3) Give an A/PTR/StaticInterface private IP and public and private view.
        * save, ValidationError raised
    """
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')

        self.o = Domain.objects.create(name="org")
        self.f_o = Domain.objects.create(name="foo.org")
        self.ctnr.domains.add(self.o, self.f_o)

        self.s = System.objects.create(name='foobar')

        Domain.objects.create(name="arpa")
        Domain.objects.create(name="in-addr.arpa")
        create_zone('10.in-addr.arpa')

        self.public = View.objects.create(name="public")
        self.private = View.objects.create(name="private")

        self.net = Network.objects.create(network_str='10.0.0.0/29')
        self.sr = Range.objects.create(
            network=self.net, range_type=STATIC, start_str='10.0.0.1',
            end_str='10.0.0.3')
        self.ctnr.ranges.add(self.sr)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            View.objects.create(name='blip'),
            View.objects.create(name='fork'),
            View.objects.create(name='eeeeeeeee'),
        )

    def test_private_view_case_1_addr(self):
        a = AddressRecord.objects.create(
            label="asf",
            ctnr=self.ctnr,
            domain=self.f_o,
            ip_str="10.0.0.1",
            ip_type="4",
        )
        a.views.add(self.private)

    def test_private_view_case_1_ptr(self):
        ptr = PTR.objects.create(
            fqdn="asf.org", ip_str="10.0.0.1", ctnr=self.ctnr, ip_type="4")
        ptr.views.add(self.private)

    def test_private_view_case_1_intr(self):
        intr = StaticInterface.objects.create(
            label="asf",
            domain=self.f_o,
            ip_str="10.0.0.1",
            ip_type="4",
            mac="00:11:22:33:44:55",
            system=self.s,
            ctnr=self.ctnr,
        )
        intr.views.add(self.private)
