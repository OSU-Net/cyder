from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.models import ipv6_to_longs

import random
import ipaddr
import pdb


class SiteTests(TestCase):
    def do_basic_add_network(self, network, prefixlen, ip_type, name=None, number=None, parent=None):
        if parent:
            s = Network(network_str=network + "/" + prefixlen, ip_type=ip_type, site=parent)
        else:
            s = Network(network_str=network + "/" + prefixlen, ip_type=ip_type)
        s.clean()
        s.save()
        self.assertTrue(s)
        return s

    def do_basic_add_site(self, name, parent=None):
        s = Site(name=name, parent=parent)
        s.clean()
        s.save()
        self.assertTrue(s)
        return s

    def test_related_sites(self):
        s1 = self.do_basic_add_site(name="Moses")
        s2 = self.do_basic_add_site(name="Son of Moses", parent=s1)
        s3 = self.do_basic_add_site(name="Other Son of Moses", parent=s1)
        s4 = self.do_basic_add_site(name="Son of the son of Moses", parent=s2)
        s5 = self.do_basic_add_site(name="Son of the son of the son of Moses", parent=s4)
        s6 = self.do_basic_add_site(name="Another Dude")
        s7 = self.do_basic_add_site(name="Some Dude")
        related_sites = s1.get_related_sites()
        self.assertEqual(set([s2,s3,s4,s5]), related_sites)
        related_sites = s4.get_related_sites()
        self.assertEqual(set([s5]), related_sites)
        related_sites = s2.get_related_sites()
        self.assertEqual(set([s4,s5]), related_sites)
