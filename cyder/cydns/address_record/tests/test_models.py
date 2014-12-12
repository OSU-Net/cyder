import ipaddr

from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.tests.utils import create_reverse_domain, create_zone, DNSTest


class AddressRecordTests(DNSTest, ModelTestMixin):
    def setUp(self):
        super(AddressRecordTests, self).setUp()

        Vrf.objects.create(name='test_vrf')

        self.osu_block = "633:105:F000:"
        create_reverse_domain('0.6.3', ip_type='4')

        self.e = Domain.objects.create(name='edu')
        self.o_e = Domain.objects.create(name='oregonstate.edu')
        self.f_o_e = Domain.objects.create(name='fooz.oregonstate.edu')
        self.m_o_e = Domain.objects.create(name='max.oregonstate.edu')
        self.z_o_e = Domain.objects.create(name='zax.oregonstate.edu')
        self.g_o_e = Domain.objects.create(name='george.oregonstate.edu')

        self._128 = create_zone('128.in-addr.arpa')

        self._128_193 = create_reverse_domain('128.193', ip_type='4')

        for dom in (self.e, self.o_e, self.f_o_e, self.m_o_e, self.z_o_e,
                    self.g_o_e, self._128, self._128_193):
            self.ctnr.domains.add(dom)

    def create_ar(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        return AddressRecord.objects.create(**kwargs)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_ar(
                label='a', domain=self.e, ip_str='128.193.40.1', ip_type='4'),
            self.create_ar(
                label='bbbbbbbbbbbbbbbbbbbbbbbbbb', domain=self.o_e,
                ip_str='128.193.40.2', ip_type='4'),
            self.create_ar(
                label='c-c-c-c-c-c-c', domain=self.z_o_e,
                ip_str='128.193.40.3', ip_type='4'),
        )

    ######################
    ### Updating Tests ###
    ######################

    def test_invalid_update_to_existing(self):
        rec1 = self.create_ar(
            label='bar', domain=self.z_o_e, ip_str="128.193.40.1", ip_type='4')
        rec2 = self.create_ar(
            label='bar', domain=self.z_o_e, ip_str="128.193.40.2", ip_type='4')
        rec3 = self.create_ar(
            label='foo', domain=self.z_o_e, ip_str="128.193.40.1", ip_type='4')

        rec1.label = "foo"
        self.assertRaises(ValidationError, rec1.save)

        rec3.label = "bar"
        self.assertRaises(ValidationError, rec3.save)

        osu_block = "633:105:F000:"
        rec1 = self.create_ar(
            label='bar', domain=self.z_o_e, ip_str=osu_block + ":1",
            ip_type='6')
        rec2 = self.create_ar(
            label='bar', domain=self.z_o_e, ip_str=osu_block + ":2",
            ip_type='6')
        rec3 = self.create_ar(
            label='foo', domain=self.z_o_e, ip_str=osu_block + ":1",
            ip_type='6')

        rec2.ip_str = osu_block + ":1"
        self.assertRaises(ValidationError, rec2.save)

        rec3.label = 'bar'
        self.assertRaises(ValidationError, rec3.save)

    def test_update_v4(self):
        rec0 = self.create_ar(
            label='', domain=self.m_o_e, ip_str="128.193.0.1", ip_type='4')

        rec1 = self.create_ar(
            label='foo', domain=self.m_o_e, ip_str="128.193.0.1", ip_type='4')

        rec2 = self.create_ar(
            label='bar', domain=self.m_o_e, ip_str="128.193.0.1", ip_type='4')

        rec3 = self.create_ar(
            label='0123456780123456780123456780123456780123456789999901'
                  '234567891',
            domain=self.m_o_e, ip_str="128.193.0.1", ip_type='4')

        rec0.label = "whooooop1"
        rec0.ip_str = "128.193.23.1"
        rec0.save()

        rec1.label = "whoooasfdasdflasdfjoop3"
        rec1.ip_str = "128.193.23.2"
        rec1.save()

        rec2.label = "whsdflhjsafdohaosdfhsadooooop1"
        rec2.ip_str = "128.193.23.4"
        rec2.save()

        rec3.label = "wasdflsadhfaoshfuoiwehfjsdkfavbhooooop1"
        rec3.ip_str = "128.193.23.3"
        rec3.save()

        rec0.label = "liaslfdjsa8df09823hsdljf-whooooop1"
        rec0.ip_str = "128.193.25.17"
        rec0.save()

        rec1.label = "w"
        rec1.ip_str = "128.193.29.83"
        rec1.save()

        rec0.label = ''
        rec0.ip_str = "128.193.23.1"
        rec0.save()

        rec1.label = "whoooasfdasdflasdfjoop3"
        rec1.save()

    def test_update_v6(self):
        create_reverse_domain('8.6.2.0', ip_type='6')
        osu_block = "8620:105:F000:"
        rec0 = self.create_ar(
            label='', domain=self.z_o_e, ip_str=(osu_block + ":1"),
            ip_type='6')
        rec1 = self.create_ar(
            label='foo', domain=self.z_o_e, ip_str=(osu_block + ":1"),
            ip_type='6')
        rec2 = self.create_ar(
            label='bar', domain=self.z_o_e, ip_str=(osu_block + ":1"),
            ip_type='6')

        rec0.label = 'whoooooasfjsp1'
        rec0.ip_str = osu_block + '0:0:123:321::'
        rec0.save()

        rec1.label = "wasfasfsafdhooooop1"
        rec1.ip_str = osu_block + "0:0:123:321::"
        rec1.save()

        rec2.label = "whoooooasfdisafsap1"
        rec2.ip_str = osu_block + "0:24:123:322:1"
        rec2.save()

        rec0.label = "whooooop1"
        rec0.ip_str = osu_block + "0:aaa::1"
        rec0.save()

        rec0.label = "wasflasksdfhooooop1"
        rec0.ip_str = osu_block + "0:dead::"
        rec0.save()

        rec1.label = "whooooosf13fp1"
        rec1.ip_str = osu_block + "0:0::"
        rec1.save()

        rec1.label = "whooooodfijasf1"
        rec1.ip_str = osu_block + "0:1:23::"
        rec1.save()

        rec2.label = "lliasdflsafwhooooop1"
        rec2.ip_str = osu_block + ":"
        rec2.save()

        rec1.label = "whooooopsjafasf1"
        rec1.ip_str = osu_block + "0::"
        rec1.save()

        rec1.label = ""
        rec1.ip_str = osu_block + "0:0:123:321::"
        rec1.save()

    def test_invalid_name(self):
        osu_block = "7620:105:F000:"
        create_reverse_domain('7.6.2.0', ip_type='6')
        a_v4 = self.create_ar(
            label='bar', domain=self.m_o_e, ip_str="128.193.23.1", ip_type='4')
        a_v6 = self.create_ar(
            label='baz', domain=self.m_o_e, ip_str=(osu_block + ':1'),
            ip_type='6')

        for label in ('.', ' sdfsa ', 'asdf.', '%asdfsaf'):
            self.assertRaises(
                ValidationError, self.create_ar,
                label=label, domain=self.f_o_e, ip_str='128.193.23.2',
                ip_type='4')

            self.assertRaises(
                ValidationError, self.create_ar,
                label=label, domain=self.f_o_e, ip_str=(osu_block + ':2'),
                ip_type='6')

            a_v4.label = label
            self.assertRaises(ValidationError, a_v4.save)

            a_v6.label = label
            self.assertRaises(ValidationError, a_v6.save)

    def test_invalid_ip_v4(self):
        a_v4 = self.create_ar(
            label='bar', domain=self.m_o_e, ip_str="128.193.23.1", ip_type='4')

        bad_ips = (
            71134, '19.193.23.1.2', 12314123, 1214123, '1928.193.23.1')
        for ip_str in bad_ips:
            self.assertRaises(
                ValidationError, self.create_ar,
                label='baz', domain=self.m_o_e, ip_str=ip_str, ip_type='4')

            a_v4.ip_str = ip_str
            self.assertRaises(ValidationError, a_v4.save)

    def test_invalid_ip_v6(self):
        osu_block = "7620:105:F000:"
        create_reverse_domain('7.6.2.0', ip_type='6')
        a_v6 = self.create_ar(
            label='bar', domain=self.m_o_e, ip_str=(osu_block + ':1'),
            ip_type='6')

        bad_ips = (
            71134, osu_block + ':::', osu_block, 123981247293462847,
            '128.193.1.1')
        for ip_str in bad_ips:
            self.assertRaises(
                ValidationError, self.create_ar,
                label='baz', domain=self.m_o_e, ip_str=ip_str, ip_type='6')

            a_v6.ip_str = ip_str
            self.assertRaises(ValidationError, a_v6.save)

    ######################
    ### Removing Tests ###
    ######################

    def create_delete_A(self, label, domain, ip_str, ip_type='4'):
        a = self.create_ar(
            label=label, domain=domain, ip_str=ip_str, ip_type=ip_type)
        a.delete()

    def test_remove_A_address_records(self):
        self.create_delete_A(label="", domain=self.o_e, ip_str="128.193.10.1")
        self.create_delete_A(
            label="far", domain=self.o_e, ip_str="128.193.0.2")
        self.create_delete_A(
            label="fetched", domain=self.o_e, ip_str="128.193.1.1")
        self.create_delete_A(
            label="drum", domain=self.o_e, ip_str="128.193.2.1")
        self.create_delete_A(
            label="and", domain=self.o_e, ip_str="128.193.0.3")
        self.create_delete_A(
            label="bass", domain=self.o_e, ip_str="128.193.2.2")
        self.create_delete_A(
            label="dude", domain=self.o_e, ip_str="128.193.5.1")
        self.create_delete_A(
            label="man", domain=self.o_e, ip_str="128.193.1.4")
        self.create_delete_A(
            label="right", domain=self.o_e, ip_str="128.193.2.6")

    def test_remove_AAAA_address_records(self):
        osu_block = "4620:105:F000:"
        create_reverse_domain('4.6.2.0', ip_type='6')
        self.create_delete_A(
            label="", domain=self.o_e, ip_str=(osu_block + ":1"), ip_type='6')
        self.create_delete_A(
            label="please", domain=self.o_e, ip_str=(osu_block + ":2"),
            ip_type='6')
        self.create_delete_A(
            label="visit", domain=self.o_e, ip_str=(osu_block + ":4"),
            ip_type='6')
        self.create_delete_A(
            label="from", domain=self.o_e, ip_str=(osu_block + ":2"),
            ip_type='6')
        self.create_delete_A(
            label="either", domain=self.o_e, ip_str=(osu_block + ":1"),
            ip_type='6')
        self.create_delete_A(
            label="webpages", domain=self.o_e, ip_str=(osu_block + ":1"),
            ip_type='6')
        self.create_delete_A(
            label="read", domain=self.o_e, ip_str=(osu_block + ":1"),
            ip_type='6')

    ####################
    ### Adding Tests ###
    ####################

    ### GLOB * ### Records

    def test_add_A_address_glob_records(self):
        # Test the glob form: *.foo.com A 10.0.0.1
        rec = self.create_ar(
            label='', domain=self.o_e, ip_str="128.193.0.1", ip_type='4')
        self.assertEqual(str(rec), "oregonstate.edu A 128.193.0.1")

        self.create_ar(label='*', domain=self.f_o_e, ip_str='128.193.0.10')
        self.create_ar(label='*foo', domain=self.f_o_e, ip_str='128.193.0.10')

        self.create_ar(label='*foo', domain=self.o_e, ip_str='128.193.0.5')
        self.create_ar(label='*foo2', domain=self.f_o_e, ip_str='128.193.0.7')
        self.create_ar(label='*foo2', domain=self.o_e, ip_str='128.193.0.2')
        self.create_ar(label='*ba-r', domain=self.f_o_e, ip_str='128.193.0.9')
        self.create_ar(label='*ba-r', domain=self.o_e, ip_str='128.193.0.4')

    # Understore '_' tests
    def test_add_address_underscore_in_name_domain(self):
        d = Domain.objects.create(name="_mssucks.edu")
        self.ctnr.domains.add(d)

        self.create_ar(label='*', domain=d, ip_str='128.193.0.10')
        self.create_ar(label='foo', domain=d, ip_str='128.193.0.10')
        self.create_ar(label='noop', domain=d, ip_str='128.193.0.10')

    def test_add_A_address_records(self):
        rec = self.create_ar(
            label='', domain=self.o_e, ip_str="128.193.0.1")
        self.assertEqual(str(rec), "oregonstate.edu A 128.193.0.1")

        self.create_ar(label='foobar', domain=self.f_o_e, ip_str='128.193.0.10')
        self.create_ar(label='foob1ar', domain=self.o_e, ip_str='128.193.0.5')
        self.create_ar(label='foo2', domain=self.f_o_e, ip_str='128.193.0.7')
        self.create_ar(label='foo2', domain=self.o_e, ip_str='128.193.0.2')
        self.create_ar(label='ba-r', domain=self.f_o_e, ip_str='128.193.0.9')
        self.create_ar(label='ba-r', domain=self.o_e, ip_str='128.193.0.4')

    def test_add_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        create_reverse_domain('2.6.2.0', ip_type='6')

        self.create_ar(
            label='', domain=self.f_o_e, ip_str=(osu_block + ':4'),
            ip_type='6')
        self.create_ar(
            label='', domain=self.o_e, ip_str=(osu_block + ':1'), ip_type='6')
        self.create_ar(
            label='6ba-r', domain=self.o_e, ip_str=(osu_block + ':6'),
            ip_type='6')
        self.create_ar(
            label='6ba-r', domain=self.f_o_e, ip_str=(osu_block + ':7'),
            ip_type='6')
        self.create_ar(
            label='6foo', domain=self.f_o_e, ip_str=(osu_block + ':5'),
            ip_type='6')
        self.create_ar(
            label='6foo', domain=self.o_e, ip_str=(osu_block + ':3'),
            ip_type='6')
        self.create_ar(
            label='6ba3z', domain=self.o_e, ip_str=(osu_block + ':4'),
            ip_type='6')
        self.create_ar(
            label='6ba3z', domain=self.f_o_e, ip_str=(osu_block + ':6'),
            ip_type='6')
        self.create_ar(
            label='6foob1ar', domain=self.o_e, ip_str=(osu_block + ':5'),
            ip_type='6')
        self.create_ar(
            label='6foob1ar', domain=self.f_o_e, ip_str=(osu_block + ':8'),
            ip_type='6')
        self.create_ar(
            label='23412341253254243', domain=self.f_o_e,
            ip_str=(osu_block + ':8'), ip_type='6')

    def test_ip_type(self):
        # invalid ip_type
        self.assertRaises(
            ValidationError, self.create_ar,
            label='uuu', domain=self.f_o_e, ip_str='128.193.4.1', ip_type='x')

        # ip_type defaults to '4', but ip_str is IPv6
        self.assertRaises(
            ValidationError, self.create_ar,
            label='uuu', domain=self.f_o_e, ip_str='111:22:3::')

    def test_bad_A_ip(self):
        osu_block = "2620:105:F000:"

        ### IPv4 ###

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf0', domain=self.o_e, ip_str=(osu_block + ':1'))

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf1', domain=self.o_e, ip_str=123142314)

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf1', domain=self.o_e, ip_str='128.193.0.1.22',
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf2', domain=self.o_e, ip_str='128.193.8')

        ### IPv6 ###

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf5', domain=self.o_e, ip_str='128.193.8.1', ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf4', domain=self.o_e, ip_str=(osu_block + ':::'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='asdf4', domain=self.o_e, ip_str=123213487823762347612346,
            ip_type='6')

    def test_duplicate(self):
        ### IPv4 ###

        def a1():
            self.create_ar(label='', domain=self.f_o_e, ip_str='128.193.0.2')

        a1()
        self.assertRaises(ValidationError, a1)

        def a2():
            self.create_ar(label='a2', domain=self.f_o_e, ip_str='128.193.0.2')

        a2()
        self.assertRaises(ValidationError, a2)

        ### IPv6 ###

        osu_block = "9620:105:F000:"
        create_reverse_domain('9.6.2.0', ip_type='6')

        def a3():
            self.create_ar(
                label='a3', domain=self.f_o_e, ip_str=(osu_block + ':2'),
                ip_type='6')

        a3()
        self.assertRaises(ValidationError, a3)

        def a4():
            self.create_ar(
                label='a4', domain=self.f_o_e, ip_str=(osu_block + ':0:9'),
                ip_type='6')

        a4()
        self.assertRaises(ValidationError, a4)

        def a5():
            self.create_ar(
                label='nope', domain=self.o_e, ip_str=(osu_block + ':4'),
                ip_type='6')

        a5()
        self.assertRaises(ValidationError, a5)

    def test_add_A_invalid_address_records(self):
        self.assertRaises(
            ValidationError, self.create_ar,
            label='', domain=self.e, ip_str='128.193.0.2')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='foo.baz.bar.nas', domain=self.o_e, ip_str='128.193.0.2')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n%as', domain=self.o_e, ip_str='128.193.0.2')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n+as', domain=self.o_e, ip_str='128.193.0.2')

    def test_add_AAAA_invalid_address_records(self):
        osu_block = "3620:105:F000:"
        create_reverse_domain('3.6.2.0', ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='foo.nas', domain=self.o_e, ip_str=(osu_block + ':1'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='foo.bar.nas', domain=self.o_e, ip_str=(osu_block + ':2'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='foo.baz.bar.nas', domain=self.o_e,
            ip_str=(osu_block + ':3'), ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n as', domain=self.o_e, ip_str=(osu_block + ':4'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n!+/*&#@as', domain=self.o_e, ip_str=(osu_block + ':5'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n%as', domain=self.o_e, ip_str=(osu_block + ':6'),
            ip_type='6')

        self.assertRaises(
            ValidationError, self.create_ar,
            label='n+as', domain=self.o_e, ip_str=(osu_block + ':7'),
            ip_type='6')

    def test_no_update_when_glue(self):
        """A record shouldn't update its label or domain when it is a glue
        record"""

        glue = self.create_ar(
            label='ns99', domain=self.o_e, ip_str='128.193.1.10')

        ns = Nameserver.objects.create(
            domain=self.o_e, server='ns99.oregonstate.edu')

        self.assertTrue(ns.glue == glue)

        # Shouldn't be able to edit label or domain.
        glue.label = 'ns100'
        self.assertRaises(ValidationError, glue.save)
        glue.domain = self.m_o_e
        self.assertRaises(ValidationError, glue.save)

        glue = glue.reload()

        glue.label = 'ns101'
        glue.domain = self.e
        self.assertRaises(ValidationError, glue.save)

        glue = glue.reload()

        glue.ip_str = '192.192.12.12'
        glue.save()

    def test_delete_with_cname_pointing_to_a(self):
        a = self.create_ar(
            label='foo100', domain=self.o_e, ip_str='128.193.1.10')
        cn = CNAME.objects.create(
            label="foomom", domain=self.o_e,
            target='foo100.oregonstate.edu', ctnr=self.ctnr)

        self.assertRaises(ValidationError, a.delete)
        a.delete(check_cname=False)

    def test_domain_ctnr(self):
        """Test that an AR's domain must be in the AR's ctnr"""
        c1 = Ctnr.objects.create(name='test_ctnr1')
        c2 = Ctnr.objects.create(name='test_ctnr2')

        c1.domains.add(self.o_e)

        AddressRecord.objects.create(
            label='foo2', domain=self.o_e, ip_str='128.193.0.2', ctnr=c1)

        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label='foo3', domain=self.o_e, ip_str='128.193.0.3', ctnr=c2)

    def test_duplicate_names(self):
        """Test that AddressRecords can have the same name iff in the same Ctnr
        """
        c1 = self.ctnr
        c2 = Ctnr.objects.create(name='test_ctnr2')
        c2.domains.add(self.o_e)

        def create_ar1():
            return AddressRecord.objects.create(
                label='foo', domain=self.o_e, ip_str='128.193.0.2', ctnr=c1)
        create_ar1.name = "AddressRecord 1"

        def create_ar2():
            return AddressRecord.objects.create(
                label='foo', domain=self.o_e, ip_str='128.193.0.3', ctnr=c1)
        create_ar2.name = "AddressRecord 2"

        def create_ar3():
            return AddressRecord.objects.create(
                label='foo', domain=self.o_e, ip_str='128.193.0.4', ctnr=c2)
        create_ar3.name = "AddressRecord 3"

        self.assertObjectsDontConflict((create_ar1, create_ar2))
        self.assertObjectsConflict((create_ar1, create_ar3))
        self.assertObjectsConflict((create_ar2, create_ar3))

    def test_address_record_conflicts_with_cname(self):
        """Test that an AddressRecord and a CNAME can't have the same name"""
        def create_cname():
            return CNAME.objects.create(
                label='bar', domain=self.o_e, target='foo.oregonstate.edu',
                ctnr=self.ctnr)
        create_cname.name = 'CNAME'

        def create_ar():
            return AddressRecord.objects.create(
                label='bar', domain=self.o_e, ip_str='128.193.0.2',
                ctnr=self.ctnr)
        create_ar.name = 'AddressRecord'

        self.assertObjectsConflict((create_cname, create_ar))

    def test_same_name_as_static_interface(self):
        """Test that ARs and SIs can share a name iff they have the same ctnr
        """
        n = Network.objects.create(
            vrf=Vrf.objects.get(name='test_vrf'), network_str='128.193.0.0/24',
            ip_type='4')

        r = Range.objects.create(
            network=n, range_type='st', start_str='128.193.0.2',
            end_str='128.193.0.100')

        c1 = self.ctnr
        c2 = Ctnr.objects.create(name='test_ctnr2')
        c2.domains.add(self.o_e)

        def create_si():
            s = System.objects.create(name='test_system')

            return StaticInterface.objects.create(
                mac='be:ef:fa:ce:11:11', label='foo1', domain=self.o_e,
                ip_str='128.193.0.2', ip_type='4', system=s, ctnr=c1)
        create_si.name = 'StaticInterface'

        def create_ar_same_ctnr():
            return AddressRecord.objects.create(
                label='foo1', domain=self.o_e, ip_str='128.193.0.3', ctnr=c1)
        create_ar_same_ctnr.name = 'AddressRecord with same ctnr'

        def create_ar_different_ctnr():
            return AddressRecord.objects.create(
                label='foo1', domain=self.o_e, ip_str='128.193.0.3', ctnr=c2)
        create_ar_different_ctnr.name = 'AddressRecord with different ctnr'

        self.assertObjectsDontConflict((create_si, create_ar_same_ctnr))
        self.assertObjectsConflict((create_si, create_ar_different_ctnr))

    def test_target_validation(self):
        """Test that the target must be an IP address"""
        valid_ips = (
            ('10.234.30.253', '4'),
            ('128.193.0.3', '4'),
            ('fe80::e1c9:1:228d:d8', '6'),
        )

        for ip_str, ip_type in valid_ips:
            self.create_delete_A(
                label='foo', domain=self.o_e, ip_str=ip_str, ip_type=ip_type)

        invalid_ips = (
            ('fe80::e1c9:1:228d:d8', '4'),
            ('10.234,30.253', '4'),
            ('10.234.30', '4'),
            ('128.193', '4'),
            ('10.234.30.253', '6'),
            ('fe80:e1c9:1:228d:d8', '6'),
            ('fe80::e1c9:1:228d:d8::91c2', '6'),
            ('fe801::e1c9:1:228d:d8', '6'),
        )

        for ip_str, ip_type in invalid_ips:
            self.assertRaises(
                ValidationError, self.create_ar,
                label='foo', domain=self.o_e, ip_str=ip_str, ip_type=ip_type)
