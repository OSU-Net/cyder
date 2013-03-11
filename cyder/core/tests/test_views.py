from django.test.client import Client

import cyder.base.tests
from cyder.base.tests.test_views_template import GenericViewTests
from cyder.core.system.models import System


def do_setUp(self, test_class, test_data):
    self.client = Client()
    self.client.login(username='development', password='password')
    self.test_class = test_class

    # Create test object.
    test_data = dict(test_data.items())
    self.test_obj, create = test_class.objects.get_or_create(**test_data)


class SystemViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'system'

    def setUp(self):
        test_data = {
            'name': 'test_system',
            'department': 'test_department',
            'location': 'test_location',
        }
        do_setUp(self, System, test_data)

    def post_data(self):
        return {
            'name': 'post_system',
            'department': 'post_department',
            'location': 'post_location',
        }


# Build the tests.
tests = (SystemViewTests,)
for view_test in tests:
    builder = GenericViewTests()
    for test in builder.build_tests():
        # Set name of test.
        setattr(view_test, test.__name__ + '_' + view_test.name, test)
