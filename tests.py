import unittest
from dhcp_objects import DhcpConfigContext, Subnet, Host

class ConfigContexTests(unittest.TestCase):

    def setUp(self):
        print "Running Config context tests"
        self.context = DhcpConfigContext()
        self.context.subnets = sorted(
                [Subnet('22.22.22.123', '255.255.255.128'),
                 Subnet('11.11.11.11', '255.255.255.0'),
                 Subnet('33.33.22.3', '255.255.255.128')])

    def test_subnet_binary_search(self):
        foo = Host('foo', ip='123.123.123.20')
        baz = Host('baz', ip='111.111.111.111')
        bar = Subnet('123.123.123.0', '255.255.255.0')
        self.context.add_subnet(bar)
        result = self.context.subnet_binary_search(foo)
        self.assertEqual(result, bar)
        result = self.context.subnet_binary_search(baz)
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
