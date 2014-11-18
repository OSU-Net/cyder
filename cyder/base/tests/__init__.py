from exceptions import AssertionError

import django.test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test.client import Client

from cyder.base.mixins import ObjectUrlMixin
from cyder.base.utils import savepoint_atomic
from cyder.core.ctnr.models import Ctnr


class TestCase(django.test.TestCase):
    """
    Base class for all tests.
    """
    client_class = Client
    fixtures = ['core/users']

    def assertRaises(self, *args, **kwargs):
        with savepoint_atomic():
            return super(TestCase, self).assertRaises(*args, **kwargs)

    def assertObjectsConflict(self, obj_create_list):
        pairs = [(a, b)
                 for a in obj_create_list
                 for b in obj_create_list
                 if a != b]

        for first, second in pairs:
            sid = transaction.savepoint()

            x = first()
            try:
                second()
            except ValidationError:
                pass
            else:
                raise AssertionError(
                    "'{}' and '{}' do not conflict".format(
                        first.name, second.name))

            transaction.savepoint_rollback(sid)

    def assertObjectsDontConflict(self, obj_create_list):
        pairs = [(a, b)
                 for a in obj_create_list
                 for b in obj_create_list
                 if a != b]

        for first, second in pairs:
            sid = transaction.savepoint()

            x = first()
            y = second()

            transaction.savepoint_rollback(sid)


class ModelTestMixin(object):
    def test_create_delete(self):
        for obj in self.objs:
            self.assertTrue(obj.pk)
            self.assertTrue(repr(obj))
            self.assertTrue(str(obj))
            self.assertTrue(unicode(obj))
            self.assertTrue(obj.details())
            if isinstance(obj, ObjectUrlMixin):
                self.assertTrue(obj.get_update_url())
                self.assertTrue(obj.get_delete_url())
            obj.delete()
            self.assertFalse(obj.pk)
