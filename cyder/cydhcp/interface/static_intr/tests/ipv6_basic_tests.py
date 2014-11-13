from django.core.exceptions import ValidationError
from functools import partial

from cyder.base.tests import ModelTestMixin
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.domain.models import Domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.tests.utils import create_reverse_domain, create_zone

from .basestatic import BaseStaticTests


class V6StaticInterTests(BaseStaticTests, ModelTestMixin):
    def setUp(self):
        super(V6StaticInterTests, self).setUp(ip_type='6')

        create_reverse_domain('0', ip_type='6')
        create_zone('1.ip6.arpa')

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_si(
                mac="11:22:33:44:55:66", label="foo0", domain=self.f_c,
                ip_str='1000:12:11:22:33:44:55:66', ip_type='6'),
            self.create_si(
                mac="22:33:44:55:66:77", label="foo1", domain=self.f_c,
                ip_str='1000:123:11:22:33:44:55:66', ip_type='6'),
            self.create_si(
                mac="33:44:55:66:77:88", label="foo2", domain=self.f_c,
                ip_str='1000:1234:11:22:33:44:55:66', ip_type='6'),
            self.create_si(
                mac="99:AA:Bb:cC:dd:ee", label="foo3", domain=self.f_c,
                ip_str='1000:11:11:22:33:44:55:66', ip_type='6'),
            self.create_si(
                mac="aa:bB:Cc:DD:EE:FF", label="foo4", domain=self.f_c,
                ip_str='1000:112:11:22:33:44:55:66', ip_type='6'),
        )

    def test_dup_create_basic(self):
        def x():
            self.create_si(
                mac="11:22:33:44:55:66",
                label="foo3",
                domain=self.f_c,
                ip_str="1000:1123:11:22:33:44:55:66",
                ip_type='6',
            )

        x()
        self.assertRaises(ValidationError, x)

    def test1_bad_add_for_a_ptr(self):
        # Intr exists, then try ptr and A

        ip_str = '1000:111:11:22:33:44:55:6e'
        self.create_si(
            mac="11:22:33:44:55:6e",
            label="9988fooddfdf",
            domain=self.c,
            ip_str=ip_str,
            ip_type='6',
        )

        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label='9988fooddfdf', domain=self.c, ip_str=ip_str, ip_type='6',
            ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, PTR.objects.create,
            ip_str=ip_str, ip_type='6', fqdn='9988fooddfdf.ccc',
            ctnr=self.ctnr)

    def test2_bad_add_for_a_ptr(self):
        # PTR and A exist, then try add intr
        mac = "11:22:33:44:55:6e"
        label = "9988fooddfdf"
        domain = self.c
        ip_str = "1000:111:" + mac

        AddressRecord.objects.create(
            label=label, domain=domain, ip_str=ip_str, ip_type='6',
            ctnr=self.ctnr)

        PTR.objects.create(
            ip_str=ip_str, ip_type='6', fqdn=(label + '.' + domain.name),
            ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, self.create_si,
            mac=mac, label=label, domain=domain, ip_str=ip_str, ip_type='6')

    def test1_bad_reverse_domain(self):
        mac = "11:22:33:44:55:66"

        i = self.create_si(
            mac=mac,
            label="8888foo",
            domain=self.f_c,
            ip_str=("1000:115:" + mac),
            ip_type='6',
        )

        i.ip_str = "9111::"
        self.assertRaises(ValidationError, i.save)

    def test1_no_system(self):
        mac = "15:22:33:44:55:66"

        self.assertRaises(
            ValueError, StaticInterface.objects.create,
            mac=mac,
            label="8888foo",
            domain=self.f_c,
            ip_str=("1000:188:" + mac),
            ip_type='6',
            system=None,
            ctnr=self.ctnr,
        )
