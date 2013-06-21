import cyder.cydhcp.keyvalue.utils as utils
from cyder.base.constants import IP_TYPE_4, IP_TYPE_6

ip_v4_good = ['0.0.0.0', '0.99.0.0', '0.0.0.255', '255.255.255.255']
ip_v4_bad = ['-1.0.0.-1', '0.0.0.256', '8.8.8.9001', '00.0.0.0',
             '8.8.8.e', '8.8,8.8', '8.8.8.8.', '.8.8.8.8']
ip_v4_list_good = ['1.1.1.1', '1.1.1.1,2.2.2.2', '1.1.1.1, 2.2.2.2',
                   '1.1.1.1 ,2.2.2.2', '1.1.1.1 , 2.2.2.2',
                   '1.1.1.1, 2.2.2.2, 3.3.3.3']
ip_v4_list_bad = ['1.1.1.1, 2.2.2.256', '1.1.1.1, 2.2.2.2,']

ip_v6_good = ['0:0:0:0:0:0:0:0', 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
              '0:0:0:0:0:0:0::', '0:0:0:0::', '0:0::0:0',
              '::0:0:0:0', '::0:0:0:0:0:0:0', '::0']
ip_v6_bad = ['0:0:0:0:0:0:0:10000', '0:0:0:0:0:0:0:0:0',
             '0:0:0:0:0:0:0:0:', ':0:0:0:0:0:0:0:0', '0:0.0:0:0:0:0:0',
             '0:0:0:0:0:0:0::0', '::0::', '0::0::0', '0:::']
ip_v6_list_good = ['::1', '::1,::2', '::1, ::2', '::1 ,::2', '::1 , ::2',
                   '::1, ::2, ::3']
ip_v6_list_bad = ['::1,::20000', '::1,::2,', ',::1,::2']

def test_is_valid_ip():
    for ip in ip_v4_good:
        assert utils.is_valid_ip(ip, ip_type=IP_TYPE_4)
    for ip in ip_v4_bad:
        assert not utils.is_valid_ip(ip, ip_type=IP_TYPE_4)

    for ip in ip_v6_good:
        assert utils.is_valid_ip(ip, ip_type=IP_TYPE_6)
    for ip in ip_v6_bad:
        assert not utils.is_valid_ip(ip, ip_type=IP_TYPE_6)

    ip_good = ip_v4_good
    ip_good.extend(ip_v6_good)
    for ip in ip_good:
        assert utils.is_valid_ip(ip)

def test_is_ip_list():
    for ip_list in ip_v4_list_good:
        assert utils.is_ip_list(ip_list)
    for ip_list in ip_v4_list_bad:
        assert not utils.is_ip_list(ip_list)

    for ip_list in ip_v6_list_good:
        assert utils.is_ip_list(ip_list)
    for ip_list in ip_v6_list_bad:
        assert not utils.is_ip_list(ip_list)

domain_good = ['example.com', 'example.com.', 'x.example.com', '1.example.com',
               '1-2-3.example.com', 'test']
domain_bad = ['example..com', '.example.com', '1-.example.com',
              '-1.example.com']

domain_list_good = ['1,2', '1, 2', '1 ,2', '1 , 2', '1, 2, 3']
domain_list_bad = ['1,2-', '1,2,', ',1,2']

def test_is_valid_domain():
    for domain in domain_good:
        assert utils.is_valid_domain(domain)
    for domain in domain_bad:
        assert not utils.is_valid_domain(domain)

def test_is_domain_list():
    for domain_list in domain_list_good:
        assert utils.is_domain_list(domain_list)
    for domain_list in domain_list_bad:
        assert not utils.is_domain_list(domain_list)
