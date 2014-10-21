from django.test import TestCase, Client

from cyder.cydns.tests.utils import create_fake_zone
from cyder.cydns.ptr.models import PTR
from cyder.cydns.cname.models import CNAME
from cyder.cydns.address_record.models import AddressRecord
from cyder.search.compiler.django_compile import compile_to_django
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.network.models import Network


class SearchDNSTests(TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.c = Client()

    def create_network_range(self, network_str, start_str, end_str,
                             range_type="st", ip_type='4', domain=None):
        if domain is None:
            domain = self.domain

        n = Network(ip_type=ip_type, network_str=network_str)
        n.save()

        r = Range(network=n, range_type=range_type, start_str=start_str,
                  end_str=end_str, domain=domain, ip_type=ip_type)
        r.save()

        self.ctnr.ranges.add(r)

    def search(self, query):
        res, errors = compile_to_django(query)
        return res, errors

    def test_integration1(self):
        create_fake_zone("wee.wee.mozilla.com", "")
        res, error = self.search("wee.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

        create_fake_zone("wee1.wee.mozilla.com", "")
        res, error = self.search("wee1.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

        res, error = self.search("wee1.wee.mozilla.com OR "
                                 "wee.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 2)
        self.assertEqual(len(res['NS']), 2)
        self.assertEqual(len(res['DOMAIN']), 2)

        res, error = self.search("wee1.wee.mozilla.com type:SOA")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 0)
        self.assertEqual(len(res['DOMAIN']), 0)

        res, error = self.search(
            "wee1.wee.mozilla.com type:NS OR "
            "wee.wee.mozilla.com type:DOMAIN")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 0)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

    def test_integration2(self):
        root_domain = create_fake_zone("wee2.wee.mozilla.com", "")
        self.ctnr.domains.add(root_domain)
        res, error = self.search("wee2.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

        create_fake_zone("1.1.ip6.arpa", "")
        res, error = self.search("1.1.ip6.arpa")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

        self.create_network_range(
            network_str="1111:0::/32", start_str="1111:0::0", end_str="1111:0::1000",
            range_type="st", ip_type='6', domain=root_domain)

        ptr = PTR(ctnr=self.ctnr, fqdn="host1.wee2.wee.mozilla.com", ip_str="1111::",
                  ip_type="6")
        ptr.save()
        addr = AddressRecord(label="host1", ctnr=self.ctnr, domain=root_domain, ip_str="11::",
                             ip_type="6")
        addr.save()
        res, error = self.search("host1.wee2.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['A']), 1)
        self.assertEqual(len(res['PTR']), 1)

        res, error = self.search("host1.wee2.wee.mozilla.com type:A")
        self.assertFalse(error)
        self.assertEqual(len(res['A']), 1)
        self.assertEqual(len(res['PTR']), 0)

        res, error = self.search("host1.wee2.wee.mozilla.com type:PTR")
        self.assertFalse(error)
        self.assertEqual(len(res['A']), 0)
        self.assertEqual(len(res['PTR']), 1)

        res, error = self.search("host1.wee2.wee.mozilla.com type:A "
                                 "type:PTR")
        self.assertFalse(error)
        self.assertEqual(len(res['A']), 0)
        self.assertEqual(len(res['PTR']), 0)

    def test_integration3_zone(self):
        root_domain = create_fake_zone("wee3.wee.mozilla.com", "")
        self.ctnr.domains.add(root_domain)
        res, error = self.search("zone:wee3.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        cn = CNAME(label="host1", ctnr=self.ctnr, domain=root_domain, target="whop.whop")
        cn.save()
        res, error = self.search("zone:wee3.wee.mozilla.com host1")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 0)
        self.assertEqual(len(res['NS']), 0)
        self.assertEqual(len(res['CNAME']), 1)

        res, error = self.search("zone:wee3.wee.mozilla.com "
                                 "type:CNAME")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 0)
        self.assertEqual(len(res['NS']), 0)
        self.assertEqual(len(res['CNAME']), 1)

    def test_integration4_ip_range(self):
        d = create_fake_zone("wee3.wee.mozilla.com", "")
        d2 = create_fake_zone("1.2.ip6.arpa", "")
        self.ctnr.domains.add(d, d2)
        res, error = self.search("1.2.ip6.arpa")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 1)
        self.assertEqual(len(res['NS']), 1)
        self.assertEqual(len(res['DOMAIN']), 1)

        self.create_network_range(
            network_str="2111:0::/32", start_str="2111:0::0", end_str="2111:0::1000",
            range_type="st", ip_type='6', domain=d)
        ptr = PTR(ctnr=self.ctnr, fqdn="host1.wee.mozilla.com", ip_str="2111:0::",
                  ip_type="6")
        ptr.save()

        res, error = self.search(ptr.ip_str)
        self.assertFalse(error)
        self.assertEqual(len(res['PTR']), 1)
        self.assertEqual(len(res['A']), 0)

        res, error = self.search("2111:0:0::")
        self.assertFalse(error)
        self.assertEqual(len(res['PTR']), 0)
        self.assertEqual(len(res['A']), 0)

    def test_integration5_ip(self):
        root_domain = create_fake_zone("wee5.wee.mozilla.com", "")
        self.ctnr.domains.add(root_domain)
        create_fake_zone("10.in-addr.arpa", "")
        res, error = self.search("10.in-addr.arpa OR "
                                 "wee5.wee.mozilla.com")
        self.assertFalse(error)
        self.assertEqual(len(res['SOA']), 2)
        self.assertEqual(len(res['NS']), 2)
        self.assertEqual(len(res['DOMAIN']), 2)
        self.create_network_range(
            network_str="10.0.0.0/24", start_str="10.0.0.1", end_str="10.0.0.2",
            range_type="st", ip_type='4', domain=root_domain)
        ptr = PTR(ctnr=self.ctnr, fqdn="host1.wee.mozilla.com", ip_str="10.0.0.1",
                  ip_type="4")
        ptr.save()
        addr = AddressRecord(label="host1", ctnr=self.ctnr, domain=root_domain,
                             ip_str="10.0.0.1", ip_type="4")
        addr.save()

        res, error = self.search(ptr.ip_str)
        self.assertFalse(error)
        self.assertEqual(len(res['PTR']), 1)
        self.assertEqual(len(res['A']), 1)

        res, error = self.search("10.0.0.2")
        self.assertFalse(error)
        self.assertEqual(len(res['PTR']), 0)
        self.assertEqual(len(res['A']), 0)
