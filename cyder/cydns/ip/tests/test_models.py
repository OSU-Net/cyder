from django.core.exceptions import ValidationError

import ipaddr
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs, Ip
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.tests.utils import create_reverse_domain, DNSTest


class SimpleTest(DNSTest):
    def setUp(self):
        super(SimpleTest, self).setUp()

        rd = create_reverse_domain('66', ip_type='4')

    def test_ipv4_str(self):
        rd = create_reverse_domain('192', ip_type='4')
        ip_str = '192.168.1.1'
        ipaddr.IPv4Address(ip_str)
        Ip(ip_str=ip_str, ip_type='4').clean_ip()

        rd = create_reverse_domain('128', ip_type='4')
        ip_str = '128.168.1.1'
        ipaddr.IPv4Address(ip_str)
        Ip(ip_str=ip_str, ip_type='4').clean_ip()

    def test_update_ipv4_str(self):
        ip_str = '66.168.1.1'
        v_ip = ipaddr.IPv4Address(ip_str)
        ip = Ip(ip_str=ip_str, ip_type='4')
        ip.clean_ip()
        self.assertEqual(ip.ip_upper, 0)
        self.assertEqual(ip.ip_lower, int(v_ip))

        # Make sure ip_lower is updated.
        ip_str = '66.213.1.9'
        v_ip = ipaddr.IPv4Address(ip_str)
        ip.ip_str = ip_str
        ip.clean_ip()
        self.assertEqual(ip.ip_upper, 0)
        self.assertEqual(ip.ip_lower, int(v_ip))

    def test_ipv6_str(self):
        create_reverse_domain('1.2.3.4', '6')

        ip_str = '1234:1234:1243:1243:1243::'
        new_ip = Ip(ip_str=ip_str, ip_type='6')
        new_ip.clean_ip()

        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        self.assertEqual(new_ip.ip_upper, ip_upper)
        self.assertEqual(new_ip.ip_lower, ip_lower)

        ip_str = '1234:432:3:0:3414:22::'
        new_ip = Ip(ip_str=ip_str, ip_type='6')
        new_ip.clean_ip()

        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        self.assertEqual(new_ip.ip_upper, ip_upper)
        self.assertEqual(new_ip.ip_lower, ip_lower)

    def test_large_ipv6(self):
        rd = create_reverse_domain('f', ip_type='6')
        ip_str = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        ip = ipaddr.IPv6Address(ip_str)
        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        self.assertEqual(ip.__int__(), (2 ** 64) * ip_upper + ip_lower)
        new_ip = Ip(ip_str=ip_str, ip_upper=ip_upper,
                    ip_lower=ip_lower, ip_type='6')
        new_ip.clean_ip()
        self.assertEqual(ip_str, new_ip.ip_str)
        self.assertEqual(ip.__int__(), new_ip.__int__())

    def bad_ipv6(self):
        self.assertRaises(ValidationError, ipv6_to_longs, {'addr': "1::::"})

    def test_int_ip(self):
        rd = create_reverse_domain('129', ip_type='4')
        ip = Ip(ip_str="129.193.1.1", ip_type='4')
        ip.clean_ip()
        ip.__int__()
        ip.__repr__()
        rd = create_reverse_domain('e', ip_type='6')
        ip_str = 'efff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        ip = Ip(ip_str=ip_str, ip_type='6')
        ip.clean_ip()
        ip.__int__()
        ip.__repr__()

    def test_creation(self):
        rd = create_reverse_domain('130', ip_type='4')

        ip = Ip(ip_str="111:22:3::", ip_type='6')
        ip.clean_ip()

        ip = Ip(ip_str="130.193.1.2", ip_type='4')
        self.assertFalse(ip.ip_upper and ip.ip_lower and ip.reverse_domain)

    def test_bad_create(self):
        ip = Ip(ip_str="111:22:3::")  # Default type is IPv4
        self.assertRaises(ValidationError, ip.clean_ip)

        ip = Ip(ip_str="130.193.1.2", ip_type='6')
        self.assertRaises(ValidationError, ip.clean_ip)

        ip = Ip(ip_str="66.193.1.2", ip_type='x')
        self.assertRaises(ValidationError, ip.clean_ip)

        ip = Ip(ip_str="66.193.1.2", ip_type=None)
        self.assertRaises(ValidationError, ip.clean_ip)

        ip = Ip(ip_str="66.193.1.2", ip_type=99)
        self.assertRaises(ValidationError, ip.clean_ip)

    def test_ipv6_to_longs(self):
        addr = "herp derp, not an ip"
        self.assertRaises(ValidationError, ipv6_to_longs, addr)

    def test1_ipv6_to_longs(self):
        ip_str = "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"
        ip_upper, ip_lower = ipv6_to_longs(ip_str)
        self.assertEqual(hex(ip_upper).lower(), "0xffffffffffffffffl")
        self.assertEqual(hex(ip_lower).lower(), "0xffffffffffffffffl")

    def test2_ipv6_to_longs(self):
        ip_upper_str = "aFFF:FaFF:FFaF:FFFa"
        ip_lower_str = "FFFa:FFaF:FaFF:aFFF"
        ip_upper, ip_lower = ipv6_to_longs(ip_upper_str + ":" + ip_lower_str)
        self.assertEqual(hex(ip_upper).lower(), "0x%sl" % (ip_upper_str.lower()
            .replace(':', '')))
        self.assertEqual(hex(ip_lower).lower(), "0x%sl" % (ip_lower_str.lower()
            .replace(':', '')))

    def test3_ipv6_to_longs(self):
        ip_upper_str = "aFFF:FaFF:FFaF:FFFa"
        ip_lower_str = "0000:0000:0000:0000"
        ip_upper, ip_lower = ipv6_to_longs(ip_upper_str + ":" + ip_lower_str)
        self.assertEqual(hex(ip_upper).lower(), "0x%sl" % (ip_upper_str.lower()
            .replace(':', '')))
        self.assertEqual(hex(ip_lower).lower(), "0x0l")
