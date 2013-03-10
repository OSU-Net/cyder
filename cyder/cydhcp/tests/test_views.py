from django.test.client import Client

from nose.tools import eq_

from cyder.base.constants import IP_TYPE_4
import cyder.base.tests
from cyder.base.tests.test_views_template import GenericViewTests
from cyder.base.tests.test_views_template import random_label
from cyder.cydhcp.constants import (ALLOW_OPTION_VRF, DENY_OPTION_UNKNOWN,
                                    STATIC)
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup


def do_setUp(self, test_class, test_data):
    self.client = Client()
    self.client.login(username='development', password='password')
    self.test_class = test_class

    # Create test object.
    test_data = dict(test_data.items())
    self.test_obj, create = test_class.objects.get_or_create(**test_data)


class RangeViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'range'

    def setUp(self):
        test_data = {
            'ip_type': IP_TYPE_4,
            'start_str': '196.168.1.1',
            'end_str': '196.168.1.2',
            'is_reserved': True,
            'allow': ALLOW_OPTION_VRF,
            'deny': DENY_OPTION_UNKNOWN,
            'range_type': STATIC,
        }
        do_setUp(self, Range, test_data)

    def post_data(self):
        return {
            'ip_type': IP_TYPE_4,
            'start_str': '196.168.1.3',
            'end_str': '196.168.1.4',
            'is_reserved': True,
            'allow': ALLOW_OPTION_VRF,
            'deny': DENY_OPTION_UNKNOWN,
            'range_type': STATIC,
        }


class VlanViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'vlan'

    def setUp(self):
        test_data = {
            'name': 'test_vlan',
            'number': 1,
        }
        do_setUp(self, Vlan, test_data)

    def post_data(self):
        return {
            'name': 'post_vlan',
            'number': 2,
        }


# Build the tests.
tests = (RangeViewTests, VlanViewTests)
for view_test in tests:
    builder = GenericViewTests()
    for test in builder.build_tests():
        # Set name of test.
        setattr(view_test, test.__name__ + '_' + view_test.name, test)
