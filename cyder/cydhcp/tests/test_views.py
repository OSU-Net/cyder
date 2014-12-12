from django.test.client import Client

from cyder.base.constants import IP_TYPE_4
from cyder.base.tests import TestCase
from cyder.base.tests.test_views_base import GenericViewTests
from cyder.cydhcp.constants import (ALLOW_VRF, STATIC)
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydns.domain.models import Domain


def do_setUp(self, test_data):
    self.client = Client()
    self.client.login(username='test_superuser', password='password')

    # Create test object.
    test_data = dict(test_data.items())
    self.test_obj = self.model.objects.create(**test_data)


class NetworkViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    model = Network
    name = 'network'

    def setUp(self):
        test_data = {
            'ip_type': IP_TYPE_4,
            'network_str': '192.168.1.0/24',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'ip_type': IP_TYPE_4,
            'network_str': '192.168.2.0/24',
            'vrf': Vrf.objects.get(name='Legacy').id,
        }


class RangeViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    name = 'range'
    model = Range
    domain, _ = Domain.objects.get_or_create(name="dummy")
    network, _ = Network.objects.get_or_create(network_str="196.168.1.0/24")

    def setUp(self):
        test_data = {
            'ip_type': IP_TYPE_4,
            'start_str': '196.168.1.1',
            'end_str': '196.168.1.2',
            'is_reserved': True,
            'allow': ALLOW_VRF,
            'range_type': STATIC,
            'domain': self.domain,
            'network': self.network,
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'ip_type': IP_TYPE_4,
            'start_str': '196.168.1.3',
            'end_str': '196.168.1.4',
            'is_reserved': True,
            'allow': ALLOW_VRF,
            'range_type': STATIC,
            'domain': self.domain.pk,
            'network': self.network.pk,
        }


class SiteViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    model = Site
    name = 'site'

    def setUp(self):
        test_data = {
            'name': 'test_site',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_site',
        }


class WorkgroupViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    model = Workgroup
    name = 'workgroup'

    def setUp(self):
        test_data = {
            'name': 'test_workgroup',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_workgroup',
        }


class VlanViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    model = Vlan
    name = 'vlan'

    def setUp(self):
        test_data = {
            'name': 'test_vlan',
            'number': 1,
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_vlan',
            'number': 2,
        }


class VrfViewTests(GenericViewTests, TestCase):
    fixtures = ['test_users/test_users.json']
    model = Vrf
    name = 'vrf'

    def setUp(self):
        test_data = {
            'name': 'test_vrf',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_vrf',
        }
