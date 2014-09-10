import ipaddr

from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain, boot_strap_ipv6_reverse_domain
from cyder.cydns.ip.models import ipv6_to_longs
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.tests.utils import create_basic_dns_data, create_zone


class AddressRecordTests(cyder.base.tests.TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain.objects.create(name=name, delegated=delegated)
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        self.ctnr, _ = Ctnr.objects.get_or_create(name='abloobloobloo')

        create_basic_dns_data(dhcp=True)

        self.osu_block = "633:105:F000:"
        boot_strap_ipv6_reverse_domain("0.6.3")
        self.e = Domain(name='edu')
        self.e.save()
        self.o_e = Domain(name='oregonstate.edu')
        self.o_e.save()

        self.f_o_e = Domain(name='fooz.oregonstate.edu')
        self.f_o_e.save()

        self.m_o_e = Domain(name='max.oregonstate.edu')
        self.m_o_e.save()

        self.z_o_e = Domain(name='zax.oregonstate.edu')
        self.z_o_e.save()
        self.g_o_e = Domain(name='george.oregonstate.edu')
        self.g_o_e.save()

        self._128 = create_zone('128.in-addr.arpa')

        self._128_193 = self.create_domain(name='128.193')

        for dom in [self.e, self.o_e, self.f_o_e, self.m_o_e, self.z_o_e,
                    self.g_o_e, self._128, self._128_193]:
            self.ctnr.domains.add(dom)

    def build_ar(self, *args, **kwargs):
        kwargs['ctnr'] = self.ctnr
        return AddressRecord(*args, **kwargs)

    ######################
    ### Updating Tests ###
    ######################
    def test_invalid_update_to_existing(self):
        rec1 = self.build_ar(label='bar', domain=self.z_o_e,
                             ip_str="128.193.40.1", ip_type='4')
        rec2 = self.build_ar(label='bar', domain=self.z_o_e,
                             ip_str="128.193.40.2", ip_type='4')
        rec3 = self.build_ar(label='foo', domain=self.z_o_e,
                             ip_str="128.193.40.1", ip_type='4')
        rec3.save()
        rec2.save()
        rec1.save()

        rec1.label = "foo"
        self.assertRaises(ValidationError, rec1.save)

        rec3.label = "bar"
        self.assertRaises(ValidationError, rec3.save)

        osu_block = "633:105:F000:"
        rec1 = self.build_ar(label='bar', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')
        rec2 = self.build_ar(label='bar', domain=self.z_o_e,
                             ip_str=osu_block + ":2", ip_type='6')
        rec3 = self.build_ar(label='foo', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')
        rec1.save()
        rec2.save()
        rec3.save()

        rec2.ip_str = osu_block + ":1"
        self.assertRaises(ValidationError, rec2.save)

        rec3.label = 'bar'
        self.assertRaises(ValidationError, rec3.save)

    """
    Things that could go wrong.
    1) Update to an invalid ip.
    2) Update to an invalid name.
    """
    def _do_generic_update_test(self, record, new_name, new_ip, ip_type):
        if new_ip:
            if ip_type == '4':
                ip_upper, ip_lower = 0, ipaddr.IPv4Address(new_ip).__int__()
            else:
                ip_upper, ip_lower = ipv6_to_longs(new_ip)
        else:
            ip_upper, ip_lower = record.ip_upper, record.ip_lower

        if new_name is not None and new_ip is not None:
            aret = AddressRecord.objects.filter(label=new_name,
                                                ip_upper=ip_upper,
                                                ip_lower=ip_lower,
                                                ip_type=ip_type)[0]
        elif new_name is not None:
            # Just new_name
            aret = AddressRecord.objects.filter(label=new_name,
                                                ip_upper=ip_upper,
                                                ip_lower=ip_lower,
                                                ip_type=ip_type)[0]
        else:
            # Just new_ip
            aret = AddressRecord.objects.filter(label=new_name,
                                                ip_upper=ip_upper,
                                                ip_lower=ip_lower,
                                                ip_type=ip_type)[0]
        if new_name:
            self.assertEqual(aret.label, new_name)
        if new_ip:
            if ip_type == '4':
                self.assertEqual(aret.ip_str,
                                 ipaddr.IPv4Address(new_ip).__str__())
            else:
                self.assertEqual(aret.ip_str,
                                 ipaddr.IPv6Address(new_ip).__str__())

    def do_update_A_record(self, record, new_name, new_ip):
        if new_name is not None:
            record.label = new_name
        if new_ip is not None:
            record.ip_str = new_ip
        record.save()
        self._do_generic_update_test(record, new_name, new_ip, '4')

    def do_update_AAAA_record(self, record, new_name, new_ip):
        if new_name is not None:
            record.label = new_name
        if new_ip is not None:
            record.ip_str = new_ip
        record.save()
        self._do_generic_update_test(record, new_name, new_ip, '6')

    def test_update_A_record(self):
        rec0 = self.build_ar(label='', domain=self.m_o_e,
                             ip_str="128.193.0.1", ip_type='4')
        rec0.save()

        rec1 = self.build_ar(label='foo', domain=self.m_o_e,
                             ip_str="128.193.0.1", ip_type='4')
        rec1.save()

        rec2 = self.build_ar(label='bar', domain=self.m_o_e,
                             ip_str="128.193.0.1", ip_type='4')
        rec2.save()

        rec3 = self.build_ar(
            label='0123456780123456780123456780123456780123456789999901'
                  '234567891',
            domain=self.m_o_e, ip_str="128.193.0.1", ip_type='4')
        rec3.save()

        self.do_update_A_record(rec0, "whooooop1", "128.193.23.1")
        self.do_update_A_record(rec1, "whoooasfdasdflasdfjoop3",
                                "128.193.23.2")
        self.do_update_A_record(rec2, "whsdflhjsafdohaosdfhsadooooop1",
                                "128.193.23.4")
        self.do_update_A_record(rec3,
                                "wasdflsadhfaoshfuoiwehfjsdkfavbhooooop1",
                                "128.193.23.3")
        self.do_update_A_record(rec0, "liaslfdjsa8df09823hsdljf-whooooop1",
                                "128.193.25.17")
        self.do_update_A_record(rec1, "w", "128.193.29.83")
        self.do_update_A_record(rec0, '', "128.193.23.1")
        self.do_update_A_record(rec1, "whoooasfdasdflasdfjoop3", None)

    def test_update_AAAA_record(self):
        boot_strap_ipv6_reverse_domain("8.6.2.0")
        osu_block = "8620:105:F000:"
        rec0 = self.build_ar(label='', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')
        rec1 = self.build_ar(label='foo', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')
        rec2 = self.build_ar(label='bar', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')

        self.do_update_AAAA_record(rec0, "whoooooasfjsp1", osu_block +
                                   "0:0:123:321::")
        self.do_update_AAAA_record(rec1, "wasfasfsafdhooooop1", osu_block +
                                   "0:0:123:321::")
        self.do_update_AAAA_record(rec2, "whoooooasfdisafsap1", osu_block +
                                   "0:24:123:322:1")
        self.do_update_AAAA_record(rec0, "whooooop1", osu_block + "0:aaa::1")
        self.do_update_AAAA_record(rec0, "wasflasksdfhooooop1", osu_block +
                                   "0:dead::")
        self.do_update_AAAA_record(rec1, "whooooosf13fp1", osu_block + "0:0::")
        self.do_update_AAAA_record(rec1, "whooooodfijasf1", osu_block +
                                   "0:1:23::")
        self.do_update_AAAA_record(rec2, "lliasdflsafwhooooop1", osu_block +
                                   ":")
        self.do_update_AAAA_record(rec1, "whooooopsjafasf1", osu_block + "0::")
        self.do_update_AAAA_record(rec1, "", osu_block + "0:0:123:321::")

    def test_update_invalid_ip_A_record(self):
        rec0 = self.build_ar(label='', domain=self.m_o_e,
                             ip_str="128.193.23.1", ip_type='4')

        rec1 = self.build_ar(label='foo', domain=self.m_o_e,
                             ip_str="128.193.26.7", ip_type='4')
        # BAD Names
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec1, 'new_name': ".", "new_ip": None})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': " sdfsa ",
                             "new_ip": None})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': "asdf.",
                             "new_ip": None})

        # BAD IPs
        self.assertRaises(ValidationError, self.do_update_A_record, **{
                          'record': rec0, 'new_name': None, "new_ip": 71134})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': None,
                             "new_ip": "19.193.23.1.2"})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': None,
                             "new_ip": 12314123})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': "narf",
                             "new_ip": 1214123})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': "%asdfsaf",
                             "new_ip": "1928.193.23.1"})
        self.assertRaises(ValidationError, self.do_update_A_record,
                          **{'record': rec0, 'new_name': None,
                             "new_ip": "1928.193.23.1"})

    def test_update_invalid_ip_AAAA_record(self):
        osu_block = "7620:105:F000:"
        boot_strap_ipv6_reverse_domain("7.6.2.0")
        rec0 = self.build_ar(label='foo', domain=self.z_o_e,
                             ip_str=osu_block + ":1", ip_type='6')

        self.assertRaises(ValidationError, self.do_update_AAAA_record, **{
                          'record': rec0, 'new_name': None, 'new_ip': 71134})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': None,
                             'new_ip': osu_block + ":::"})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': "%asdfsaf",
                             'new_ip': osu_block})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': "sdfsa",
                             'new_ip': 1239812472934623847})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': None,
                             'new_ip': "128.193.1.1"})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': "%asdfsaf",
                             'new_ip': osu_block + ":1"})
        self.assertRaises(ValidationError, self.do_update_AAAA_record,
                          **{'record': rec0, 'new_name': " sdfsa ",
                             'new_ip': None})

    ######################
    ### Removing Tests ###
    ######################
    def do_remove_A_record(self, aname, domain, ip):
        aret = self.build_ar(label=aname, domain=domain, ip_str=ip,
                             ip_type='4')
        aret.save()
        self.assertTrue(aret)

        aret.delete()

        aret = AddressRecord.objects.filter(label=aname, domain=domain,
                                            ip_str=ip)
        self.assertFalse(aret)

    def do_remove_AAAA_record(self, aname, domain, ip):
        aret = self.build_ar(label=aname, domain=domain, ip_str=ip,
                             ip_type='6')
        aret.save()
        self.assertTrue(aret)

        aret.delete()

        nret = AddressRecord.objects.filter(label=aname, domain=domain,
                                            ip_str=ip)
        self.assertFalse(nret)

    def test_remove_A_address_records(self):
        self.do_remove_A_record("", self.o_e, "128.193.10.1")
        self.do_remove_A_record("far", self.o_e, "128.193.0.2")
        self.do_remove_A_record("fetched", self.o_e, "128.193.1.1")
        self.do_remove_A_record("drum", self.o_e, "128.193.2.1")
        self.do_remove_A_record("and", self.o_e, "128.193.0.3")
        self.do_remove_A_record("bass", self.o_e, "128.193.2.2")
        self.do_remove_A_record("dude", self.o_e, "128.193.5.1")
        self.do_remove_A_record("man", self.o_e, "128.193.1.4")
        self.do_remove_A_record("right", self.o_e, "128.193.2.6")
        self.do_remove_A_record("", self.f_o_e, "128.193.0.1")
        self.do_remove_A_record("far", self.f_o_e, "128.193.0.2")
        self.do_remove_A_record("fetched", self.f_o_e, "128.193.1.1")
        self.do_remove_A_record("drum", self.f_o_e, "128.193.2.1")
        self.do_remove_A_record("and", self.f_o_e, "128.193.0.3")
        self.do_remove_A_record("bass", self.f_o_e, "128.193.2.2")
        self.do_remove_A_record("dude", self.f_o_e, "128.193.5.1")
        self.do_remove_A_record("man", self.f_o_e, "128.193.1.4")
        self.do_remove_A_record("right", self.f_o_e, "128.193.2.6")

    def test_remove_AAAA_address_records(self):
        osu_block = "4620:105:F000:"
        boot_strap_ipv6_reverse_domain("4.6.2.0")
        self.do_remove_AAAA_record("", self.o_e, osu_block + ":1")
        self.do_remove_AAAA_record("please", self.o_e, osu_block + ":2")
        self.do_remove_AAAA_record("visit", self.o_e, osu_block + ":4")
        self.do_remove_AAAA_record("from", self.o_e, osu_block + ":2")
        self.do_remove_AAAA_record("either", self.o_e, osu_block + ":1")
        self.do_remove_AAAA_record("webpages", self.o_e, osu_block + ":1")
        self.do_remove_AAAA_record("read", self.o_e, osu_block + ":1")
        self.do_remove_AAAA_record("", self.f_o_e, osu_block + ":1")
        self.do_remove_AAAA_record("please", self.f_o_e, osu_block + ":2")
        self.do_remove_AAAA_record("visit", self.f_o_e, osu_block + ":4")
        self.do_remove_AAAA_record("from", self.f_o_e, osu_block + ":2")
        self.do_remove_AAAA_record("either", self.f_o_e, osu_block + ":1")
        self.do_remove_AAAA_record("webpages", self.f_o_e, osu_block + ":1")
        self.do_remove_AAAA_record("read", self.f_o_e, osu_block + ":1")

    ####################
    ### Adding Tests ###
    ####################
    def do_add_record(self, data):
        rec = self.build_ar(label=data['label'], domain=data['domain'],
                            ip_str=data['ip'], ip_type='4')
        rec.save()
        self.assertTrue(rec.__repr__())
        self.assertTrue(rec.details())

        search = AddressRecord.objects.filter(
            label=data['label'], domain=data['domain'], ip_type='4',
            ip_str=data['ip'])
        found = False
        for record in search:
            if record.ip_str == data['ip']:
                found = True
        self.assertTrue(found)
        return rec

    def do_add_record6(self, data):
        rec = self.build_ar(label=data['label'], domain=data['domain'],
                            ip_str=data['ip'], ip_type='6')
        rec.save()
        self.assertTrue(rec.__repr__())
        self.assertTrue(rec.details())

    ### GLOB * ### Records

    def test_add_A_address_glob_records(self):
        # Test the glob form: *.foo.com A 10.0.0.1
        rec = self.build_ar(label='', domain=self.o_e,
                            ip_str="128.193.0.1", ip_type='4')
        rec.save()
        self.assertEqual(rec.__str__(), "oregonstate.edu A 128.193.0.1")

        data = {'label': '*', 'domain': self.f_o_e, 'ip': "128.193.0.10"}
        self.do_add_record(data)
        data = {'label': '*foob1ar', 'domain': self.f_o_e, 'ip':
                "128.193.0.10"}
        self.do_add_record(data)

        data = {'label': '*foob1ar', 'domain': self.o_e, 'ip': "128.193.0.5"}
        self.do_add_record(data)
        data = {'label': '*foo2', 'domain': self.f_o_e, 'ip': "128.193.0.7"}
        self.do_add_record(data)
        data = {'label': '*foo2', 'domain': self.o_e, 'ip': "128.193.0.2"}
        self.do_add_record(data)
        data = {'label': '*ba-r', 'domain': self.f_o_e, 'ip': "128.193.0.9"}
        self.do_add_record(data)
        data = {'label': '*ba-r', 'domain': self.o_e, 'ip': "128.193.0.4"}
        self.do_add_record(data)

    # Understore '_' tests
    def test_add_address_underscore_in_name_domain(self):
        d = Domain(name="_mssucks.edu")
        d.save()
        self.ctnr.domains.add(d)
        data = {'label': '*', 'domain': d, 'ip': "128.193.0.10"}
        self.do_add_record(data)
        data = {'label': 'foo', 'domain': d, 'ip': "128.193.0.10"}
        a = self.do_add_record(data)
        a.save()

        data = {'label': 'noop', 'domain': d, 'ip': "128.193.0.10"}
        self.do_add_record(data)

    def test_add_A_address_records(self):
        rec = self.build_ar(label='', domain=self.o_e,
                            ip_str="128.193.0.1", ip_type='4')
        rec.save()
        self.assertEqual(rec.__str__(), "oregonstate.edu A 128.193.0.1")

        data = {'label': 'foob1ar', 'domain': self.f_o_e, 'ip':
                "128.193.0.10"}
        self.do_add_record(data)

        data = {'label': 'foob1ar', 'domain': self.o_e, 'ip': "128.193.0.5"}
        self.do_add_record(data)
        data = {'label': 'foo2', 'domain': self.f_o_e, 'ip': "128.193.0.7"}
        self.do_add_record(data)
        data = {'label': 'foo2', 'domain': self.o_e, 'ip': "128.193.0.2"}
        self.do_add_record(data)
        data = {'label': 'ba-r', 'domain': self.f_o_e, 'ip': "128.193.0.9"}
        self.do_add_record(data)
        data = {'label': 'ba-r', 'domain': self.o_e, 'ip': "128.193.0.4"}
        self.do_add_record(data)

    def test_add_AAAA_address_records(self):
        osu_block = "2620:105:F000:"
        boot_strap_ipv6_reverse_domain("2.6.2.0")
        data = {'label': '', 'domain': self.f_o_e, 'ip': osu_block + ":4"}
        self.do_add_record6(data)
        data = {'label': '', 'domain': self.o_e, 'ip': osu_block + ":1"}
        self.do_add_record6(data)
        data = {'label': '6ba-r', 'domain': self.o_e, 'ip': osu_block + ":6"}
        self.do_add_record6(data)
        data = {'label': '6ba-r', 'domain': self.f_o_e, 'ip':
                osu_block + ":7"}
        self.do_add_record6(data)
        data = {'label': '6foo', 'domain': self.f_o_e, 'ip': osu_block + ":5"}
        self.do_add_record6(data)
        data = {'label': '6foo', 'domain': self.o_e, 'ip': osu_block + ":3"}
        self.do_add_record6(data)
        data = {'label': '6ba3z', 'domain': self.o_e, 'ip': osu_block + ":4"}
        self.do_add_record6(data)
        data = {'label': '6ba3z', 'domain': self.f_o_e, 'ip':
                osu_block + ":6"}
        self.do_add_record6(data)
        data = {'label': '6foob1ar', 'domain': self.o_e, 'ip':
                osu_block + ":5"}
        self.do_add_record6(data)
        data = {'label': '6foob1ar', 'domain': self.f_o_e, 'ip':
                osu_block + ":8"}
        self.do_add_record6(data)
        data = {'label': '23412341253254243', 'domain':
                self.f_o_e, 'ip': osu_block + ":8"}
        self.do_add_record6(data)

    def test_ip_type(self):
        data = {'label': 'uuu', 'domain': self.f_o_e, 'ip': '128.193.4.1'}
        rec = self.build_ar(label=data['label'], domain=data[
                            'domain'], ip_str=data['ip'], ip_type='x')
        # invalid ip_type
        self.assertRaises(ValidationError, rec.save)

        data = {'label': 'uuu', 'domain': self.f_o_e, 'ip': '111:22:3::'}
        rec = self.build_ar(
            label=data['label'], domain=data['domain'], ip_str=data['ip'])
        # ip_type defaults to '4', but ip_str is IPv6
        self.assertRaises(ValidationError, rec.save)

    def test_bad_A_ip(self):
        #IPv4 Tests
        osu_block = "2620:105:F000:"
        data = {'label': 'asdf0', 'domain': self.o_e, 'ip': osu_block + ":1"}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'asdf1', 'domain': self.o_e, 'ip': 123142314}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'asdf1', 'domain': self.o_e, 'ip': "128.193.0.1.22"}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'asdf2', 'domain': self.o_e, 'ip': "128.193.8"}
        self.assertRaises(ValidationError, self.do_add_record, data)

    def test_bad_AAAA_ip(self):
        # IPv6 Tests
        osu_block = "2620:105:F000:"
        data = {'label': 'asdf5', 'domain': self.o_e, 'ip': "128.193.8.1"}
        self.assertRaises(ValidationError, self.do_add_record6, data)
        data = {'label': 'asdf4', 'domain': self.o_e, 'ip': osu_block + ":::"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'asdf4', 'domain': self.o_e, 'ip':
                123213487823762347612346}
        self.assertRaises(ValidationError, self.do_add_record6, data)

    def test_add_A_records_exist(self):
        data = {'label': '', 'domain': self.f_o_e, 'ip': "128.193.0.2"}
        self.do_add_record(data)
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'new', 'domain': self.f_o_e, 'ip': "128.193.0.2"}
        self.do_add_record(data)
        self.assertRaises(ValidationError, self.do_add_record, data)

    def test_add_AAAA_records_exist(self):
        osu_block = "9620:105:F000:"
        boot_strap_ipv6_reverse_domain("9.6.2.0")

        data = {'label': 'new', 'domain': self.f_o_e, 'ip': osu_block + ":2"}
        self.do_add_record6(data)
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'new', 'domain': self.f_o_e, 'ip':
                osu_block + ":0:9"}
        self.do_add_record6(data)
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'nope', 'domain': self.o_e, 'ip': osu_block + ":4"}
        self.do_add_record6(data)
        self.assertRaises(ValidationError, self.do_add_record6, data)

    def test_add_A_invalid_address_records(self):

        data = {'label': "", 'domain': self.e, 'ip': "128.193.0.2"}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'foo.baz.bar.nas', 'domain': self.o_e,
                'ip': "128.193.0.2"}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'n%as', 'domain': self.o_e, 'ip': "128.193.0.2"}
        self.assertRaises(ValidationError, self.do_add_record, data)

        data = {'label': 'n+as', 'domain': self.o_e, 'ip': "128.193.0.2"}
        self.assertRaises(ValidationError, self.do_add_record, data)

    def test_add_AAAA_invalid_address_records(self):
        osu_block = "3620:105:F000:"
        boot_strap_ipv6_reverse_domain("3.6.2.0")

        data = {'label': 'foo.nas', 'domain': self.o_e, 'ip':
                osu_block + ":1"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'foo.bar.nas', 'domain': self.o_e, 'ip':
                osu_block + ":2"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'foo.baz.bar.nas', 'domain': self.o_e,
                'ip': osu_block + ":3"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'n as', 'domain': self.o_e, 'ip': osu_block + ":4"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'n!+/*&%$#@as', 'domain': self.o_e, 'ip':
                osu_block + ":5"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'n%as', 'domain': self.o_e, 'ip': osu_block + ":6"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

        data = {'label': 'n+as', 'domain': self.o_e, 'ip': osu_block + ":7"}
        self.assertRaises(ValidationError, self.do_add_record6, data)

    def test_no_update_when_glue(self):
        """A record shouldn't update it's label or domain when it is a glue
        record"""
        label = 'ns99'
        glue = self.build_ar(label=label, domain=self.o_e,
                             ip_str='128.193.1.10', ip_type='4')
        glue.save()

        server = "%s.%s" % (label, self.o_e)
        ns = Nameserver(domain=self.o_e, server=server)
        ns.save()
        self.assertTrue(ns.glue == glue)

        # Shouldn't be able to edit label or domain.
        glue.label = "ns100"
        self.assertRaises(ValidationError, glue.save)
        glue.domain = self.m_o_e
        self.assertRaises(ValidationError, glue.save)

        glue = AddressRecord.objects.get(pk=glue.pk)
        glue.label = "ns101"
        glue.domain = self.e
        self.assertRaises(ValidationError, glue.save)

        # Ip can change.
        glue = AddressRecord.objects.get(pk=glue.pk)
        glue.ip_str = "192.192.12.12"
        glue.save()

    def test_delete_with_cname_pointing_to_a(self):
        label = 'foo100'
        a = self.build_ar(label=label, domain=self.o_e,
                          ip_str='128.193.1.10', ip_type='4')
        a.save()
        cn = CNAME(label="foomom", domain=self.o_e, target=label + "." +
                   self.o_e.name, ctnr=self.ctnr)
        cn.save()
        self.assertRaises(ValidationError, a.delete)
        a.delete(check_cname=False)

    def test_domain_ctnr(self):
        """Test that an AR's domain must be in the AR's ctnr"""
        c1 = Ctnr(name='test_ctnr1')
        c1.save()
        c2 = Ctnr(name='test_ctnr2')
        c2.save()

        c1.domains.add(self.o_e)

        a1 = AddressRecord(label='foo2', domain=self.o_e, ip_str='128.193.0.2',
                           ctnr=c1)
        a1.save()

        with self.assertRaises(ValidationError):
            a2 = AddressRecord(label='foo3', domain=self.o_e,
                               ip_str='128.193.0.3', ctnr=c2)
            a2.save()

    def test_duplicate_names(self):
        """Test that AddressRecords can have the same name iff in the same Ctnr
        """
        c1 = self.ctnr
        c2 = Ctnr(name='test_ctnr2')
        c2.save()
        c2.domains.add(self.o_e)

        def create_ar1():
            a = AddressRecord(label='foo', domain=self.o_e,
                              ip_str='128.193.0.2', ctnr=c1)
            a.save()
            return a
        create_ar1.name = "AddressRecord 1"

        def create_ar2():
            a = AddressRecord(label='foo', domain=self.o_e,
                              ip_str='128.193.0.3', ctnr=c1)
            a.save()
            return a
        create_ar2.name = "AddressRecord 2"

        def create_ar3():
            a = AddressRecord(label='foo', domain=self.o_e,
                              ip_str='128.193.0.4', ctnr=c2)
            a.save()
            return a
        create_ar3.name = "AddressRecord 3"

        self.assertObjectsDontConflict((create_ar1, create_ar2))
        self.assertObjectsConflict((create_ar1, create_ar3))
        self.assertObjectsConflict((create_ar2, create_ar3))

    def test_address_record_conflicts_with_cname(self):
        """Test that an AddressRecord and a CNAME can't have the same name"""
        def create_cname():
            cn = CNAME(label='bar', domain=self.o_e,
                       target='foo.oregonstate.edu', ctnr=self.ctnr)
            cn.save()
            return cn
        create_cname.name = 'CNAME'

        def create_ar():
            a = AddressRecord(label='bar', domain=self.o_e,
                              ip_str='128.193.0.2', ctnr=self.ctnr)
            a.save()
            return a
        create_ar.name = 'AddressRecord'

        self.assertObjectsConflict((create_cname, create_ar))

    def test_same_name_as_static_interface(self):
        """Test that ARs and SIs can share a name iff they have the same ctnr
        """
        n = Network(vrf=Vrf.objects.get(name='test_vrf'), ip_type='4',
                    network_str='128.193.0.0/24')
        n.save()

        r = Range(network=n, range_type='st', start_str='128.193.0.2',
                  end_str='128.193.0.100')
        r.save()

        c1 = self.ctnr
        c2 = Ctnr(name='test_ctnr2')
        c2.save()
        c2.domains.add(self.o_e)

        def create_si():
            s = System(name='test_system')
            s.save()

            si = StaticInterface(
                mac='be:ef:fa:ce:11:11', label='foo1', domain=self.o_e,
                ip_str='128.193.0.2', ip_type='4', system=s,
                ctnr=c1)
            si.save()

            return si
        create_si.name = 'StaticInterface'

        def create_ar_same_ctnr():
            a = AddressRecord(label='foo1', domain=self.o_e,
                               ip_str='128.193.0.3', ctnr=c1)
            a.save()
            return a
        create_ar_same_ctnr.name = 'AddressRecord with same ctnr'

        def create_ar_different_ctnr():
            a = AddressRecord(label='foo1', domain=self.o_e,
                               ip_str='128.193.0.3', ctnr=c2)
            a.save()
            return a
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
            a = AddressRecord(label='foo', domain=self.o_e,
                              ip_str=ip_str, ip_type=ip_type, ctnr=self.ctnr)
            a.save()
            a.delete()

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
            with self.assertRaises(ValidationError):
                a = AddressRecord(label='foo', domain=self.o_e,
                                  ip_str=ip_str, ip_type=ip_type)
                a.save()
