from django.test.client import Client

from cyder.base.tests import TestCase
from cyder.base.tests.test_views_base import GenericViewTests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System


def do_setUp(self, test_data):
    self.client = Client()
    self.client.login(username='test_superuser', password='password')

    # Create test object.
    self.test_obj = self.model.objects.create(**test_data)


class CtnrViewTests(TestCase, GenericViewTests):
    fixtures = ['test_users/test_users.json']
    model = Ctnr
    name = 'ctnr'

    def setUp(self):
        test_data = {
            'name': 'test_test_ctnr',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_ctnr',
        }


class SystemViewTests(TestCase, GenericViewTests):
    fixtures = ['test_users/test_users.json']
    model = System
    name = 'system'

    def setUp(self):
        test_data = {
            'name': 'test_system',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'name': 'post_system',
        }
