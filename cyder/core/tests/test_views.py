from django.test.client import Client

from cyder.base.tests import TestCase
from cyder.base.tests.test_views_base import GenericViewTests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System


def do_setUp(self, test_class, test_data):
    self.client = Client()
    self.client.login(username='test_superuser', password='password')
    self.test_class = test_class

    # Create test object.
    test_data = dict(test_data.items())
    self.test_obj, create = test_class.objects.get_or_create(**test_data)


class CtnrViewTests(TestCase, GenericViewTests):
    fixtures = ['test_users/test_users.json']
    name = 'ctnr'

    def setUp(self):
        test_data = {
            'name': 'test_test_ctnr',
        }
        do_setUp(self, Ctnr, test_data)

    def post_data(self):
        return {
            'name': 'post_ctnr',
        }


class SystemViewTests(TestCase, GenericViewTests):
    fixtures = ['test_users/test_users.json']
    name = 'system'

    def setUp(self):
        test_data = {
            'name': 'test_system',
        }
        do_setUp(self, System, test_data)

    def post_data(self):
        return {
            'name': 'post_system',
        }
