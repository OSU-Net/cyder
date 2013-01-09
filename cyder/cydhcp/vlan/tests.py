from django.test import TestCase
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan


class VlanTests(TestCase):

    def do_basic_add_network(self, network, prefixlen, ip_type, name=None,
                             vlan=None, site=None):
        n = Network(network_str=network + "/" + prefixlen, ip_type=ip_type,
                    site=site, vlan=vlan)
        n.clean()
        n.save()
        return n

    def do_basic_add_site(self, name, parent=None):
        s = Site(name=name, parent=parent)
        s.clean()
        s.save()
        return s

    def do_basic_add_vlan(self, name, number):
        vlan = Vlan(name=name, number=number)
        vlan.clean()
        vlan.save()
        return vlan

    def test_related_networks(self):
        s1 = self.do_basic_add_site(name="Site 1")
        s2 = self.do_basic_add_site(name="Site 2", parent=s1)
        s3 = self.do_basic_add_site(name="Site 3", parent=s1)
        s4 = self.do_basic_add_site(name="Site 4", parent=s2)
        s5 = self.do_basic_add_site(name="Site 5", parent=s4)
        s6 = self.do_basic_add_site(name="Site 6", parent=s3)
        s7 = self.do_basic_add_site(name="Site 7", parent=s3)
        s8 = self.do_basic_add_site(name="Site 8", parent=s7)
        s9 = self.do_basic_add_site(name="Site 9", parent=s7)
        s10 = self.do_basic_add_site(name="Site 10", parent=s7)

        v1 = self.do_basic_add_vlan(name="Vlan 1", number=1)
        v2 = self.do_basic_add_vlan(name="Vlan 2", number=2)
        v3 = self.do_basic_add_vlan(name="Vlan 3", number=3)
        v4 = self.do_basic_add_vlan(name="Vlan 4", number=4)


        network = "123.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s1}
        n1 = self.do_basic_add_network(**kwargs)

        network = "123.0.10.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s3,
                  'vlan': v3}
        n2 = self.do_basic_add_network(**kwargs)

        network = "123.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s7}
        n3 = self.do_basic_add_network(**kwargs)

        network = "123.0.16.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'vlan': v4}
        n4 = self.do_basic_add_network(**kwargs)

        network = "123.0.16.0"
        prefixlen = "21"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s10}
        n5 = self.do_basic_add_network(**kwargs)

        network = "123.0.17.0"
        prefixlen = "26"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n6 = self.do_basic_add_network(**kwargs)

        network = "123.0.18.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n7 = self.do_basic_add_network(**kwargs)

        network = "223.0.0.0"
        prefixlen = "10"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4', 'site': s1}
        n8 = self.do_basic_add_network(**kwargs)

        network = "223.0.10.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'vlan': v1}
        n9 = self.do_basic_add_network(**kwargs)

        network = "223.0.32.0"
        prefixlen = "20"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s2,
                  'vlan': v2}
        n10 = self.do_basic_add_network(**kwargs)

        network = "223.0.32.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4'}
        n11 = self.do_basic_add_network(**kwargs)

        network = "223.0.33.0"
        prefixlen = "24"
        kwargs = {'network': network,
                  'prefixlen': prefixlen,
                  'ip_type': '4',
                  'site': s4}
        n12 = self.do_basic_add_network(**kwargs)

        self.assertEqual(v1.get_related_networks(), set([n9]))
        self.assertEqual(v2.get_related_networks(), set([n10, n11, n12]))
        self.assertEqual(v3.get_related_networks(), set([n2, n3]))
        self.assertEqual(v4.get_related_networks(), set([n4, n5, n6, n7]))
