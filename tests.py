import unittest
from dhcp_objects import (Subnet, Host, Option, Parameter,
                          Pool, Group, Allow, Deny)
from parser import iscgrammar, DhcpConfigContext
from constants import *


class ParserTests(unittest.TestCase):

    def setUp(self):
        self.subnet_input = """
        subnet 128.193.212.0 netmask 255.255.254.0 {
            option subnet-mask 255.255.254.0;
            option time-offset 28800;
            option routers 128.193.212.1;
            option netbios-node-type 8;
            pool {
                failover peer "dhcp";
                deny dynamic bootp clients;
                allow members of "zone.science:128.193.213.1:128.193.213.244";
                range 128.193.213.1 128.193.213.244;
            }
        }"""

        self.pool_input = """
        pool {
            failover peer "dhcp";
            deny dynamic bootp clients;
            allow members of "zone.vet:128.193.215.160:128.193.215.199";
            allow members of "zone.vetoregonstate:128.193.215.160:128.193.215.199";
            range 128.193.215.160 128.193.215.199;
        }"""

        self.host_input1 = """
        host x74742-boot.nws.oregonstate.edu {
            hardware ethernet 00:04:0d:f0:3b:e8;
        }"""

        self.host_input2 = """
        host temp-hhs.hhs.oregonstate.edu {
            fixed-address 128.193.122.93;
            hardware ethernet 00:b0:d0:7e:c8:c3;
        }"""

        self.group_input = """
        group {
            option subnet-mask 255.255.255.224;
            option time-offset 28800;
            option routers 128.193.158.65;
            host temp-hhs.hhs.oregonstate.edu {
                fixed-address 128.193.122.93;
                hardware ethernet 00:b0:d0:7e:c8:c3;
            }
        }"""
        """
        subnet 128.193.212.0 netmask 255.255.254.0 {
            option subnet-mask 255.255.254.0;
            option time-offset 28800;
            option routers 128.193.212.1;
            option netbios-node-type 8;
            pool {
                failover peer "dhcp";
                deny dynamic bootp clients;
                allow members of "zone.science:128.193.213.1:128.193.213.244";
                range 128.193.213.1 128.193.213.244;
            }
        }"""
    def test_subnet_parse(self):
        o1 = Option('subnet-mask', '255.255.254.0', SUBNET)
        o2 = Option('time-offset', '28800', SUBNET)
        o3 = Option('routers', '128.193.212.1', SUBNET)
        o4 = Option('netbios-node-type', '8', SUBNET)
        p1 = Parameter('failover', 'peer "dhcp"', POOL)
        a1 = Allow('members of "zone.science:128.193.213.1:128.193.213.244"')
        d1 = Deny('dynamic bootp clients')
        expected_pool = Pool(start='128.193.213.1', end='128.193.213.244',
                             allow=[a1],
                             deny=[d1],
                             parameters=[p1])
        expected_subnet = Subnet(network_addr='128.193.212.0',
                                 netmask_addr='255.255.254.0',
                                 options=[o1, o2, o3,o4],
                                 pools=[expected_pool])
        subnet = iscgrammar(self.subnet_input).Subnet()
        self.assertEqual(subnet, expected_subnet)

    def test_pool_parse(self):
        p1 = Parameter('failover', 'peer "dhcp"', POOL)
        a1 = Allow('members of "zone.vet:128.193.215.160:128.193.215.199"')
        a2 = Allow('members of "zone.vetoregonstate:128.193.215.160:128.193.215.199"')
        d1 = Deny('dynamic bootp clients')
        expected_pool = Pool(start='128.193.215.160', end='128.193.215.199',
                             allow=[a1, a2],
                             deny=[d1],
                             parameters=[p1])
        pool = iscgrammar(self.pool_input).Pool()
        self.assertEqual(pool, expected_pool)

    def test_host_parse(self):
        expected_host1 = Host('x74742-boot.nws.oregonstate.edu',
                     mac='00:04:0d:f0:3b:e8')

        host1 = iscgrammar(self.host_input1).Host()
        self.assertEqual(host1, expected_host1)
        expected_host2 = Host('temp-hhs.hhs.oregonstate.edu',
                     '128.193.122.93',
                     '00:b0:d0:7e:c8:c3')
        host2 = iscgrammar(self.host_input2).Host()
        self.assertEqual(host2, expected_host2)

    def test_group_parse(self):
        o1 = Option('subnet-mask', '255.255.255.224', GROUP)
        o2 = Option('time-offset', '28800', GROUP)
        o3 = Option('routers', '128.193.158.65', GROUP)
        host = Host(fqdn='temp-hhs.hhs.oregonstate.edu',
                    ip='128.193.122.93',
                    mac='00:b0:d0:7e:c8:c3')
        expected_group = Group(options=[o1,o2,o3], hosts=[host])
        group = iscgrammar(self.group_input).Group()
        self.assertEqual(expected_group, group)

if __name__ == '__main__':
    unittest.main()
