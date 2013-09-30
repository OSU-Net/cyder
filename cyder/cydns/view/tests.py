from django.test import TestCase

from cyder.cydns.view.models import View
from cyder.cydns.domain.models import Domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.address_record.models import AddressRecord
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network


class ViewTests(TestCase):
    """
    Cases we need to cover:
    1) Give an A/PTR/StaticInterface private IP and the private view.
        * clean, save, *no* ValidationError raised

    The following cases were determined to be an unnecessary feature:
    2) Give an A/PTR/StaticInterface private IP and the public view.
        * clean, save, ValidationError raised
    3) Give an A/PTR/StaticInterface private IP and public and private view.
        * clean, save, ValidationError raised
    """
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()

        self.o = Domain(name="org")
        self.o.save()
        self.f_o = Domain(name="foo.org")
        self.f_o.save()
        self.s = System(name='foobar')
        self.s.save()

        Domain.objects.get_or_create(name="arpa")
        Domain.objects.get_or_create(name="in-addr.arpa")
        Domain.objects.get_or_create(name="10.in-addr.arpa")
        Domain.objects.get_or_create(name="172.in-addr.arpa")
        Domain.objects.get_or_create(name="192.in-addr.arpa")

        self.public, _ = View.objects.get_or_create(name="public")
        self.private, _ = View.objects.get_or_create(name="private")

        self.net = Network(network_str='10.0.0.0/29')
        self.net.update_network()
        self.net.save()
        self.sr = Range(network=self.net, range_type=STATIC,
                        start_str='10.0.0.1', end_str='10.0.0.3')
        self.sr.save()

    def test_private_view_case_1_addr(self):
        a = AddressRecord(label="asf", domain=self.f_o, ip_str="10.0.0.1",
                          ip_type="4")
        a.clean()
        a.save()
        # Object has to exist before views can be assigned.
        a.views.add(self.private)
        a.save()

    def test_private_view_case_1_ptr(self):
        ptr = PTR(fqdn="asf", ip_str="10.0.0.1",
                  ip_type="4")
        ptr.clean()
        ptr.save()
        # Object has to exist before views can be assigned.
        ptr.views.add(self.private)
        ptr.save()

    def test_private_view_case_1_intr(self):
        intr = StaticInterface(label="asf", domain=self.f_o, ip_str="10.0.0.1",
                               ip_type="4", mac="00:11:22:33:44:55",
                               system=self.s, ctnr=self.ctnr)
        intr.clean()
        intr.save()
        # Object has to exist before views can be assigned.
        intr.views.add(self.private)
        intr.save()
