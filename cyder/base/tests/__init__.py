from exceptions import AssertionError

import django.test
from django.core.exceptions import ValidationError
from django.test.client import Client

from cyder.base.utils import savepoint_atomic
from cyder.core.ctnr.models import Ctnr


class CyTestMixin(object):
    """
    Mixin for all tests.
    """
    def _pre_setup(self):
        super(TestCase, self)._pre_setup()

        # Add ctnrs to session.
        session = self.client.session
        session['ctnr'] = Ctnr.objects.get(id=2)
        session['ctnrs'] = list(Ctnr.objects.all())
        session.save()

    def assertObjectsConflict(self, obj_create_list):
        pairs = [(a,b)
                 for a in obj_create_list
                 for b in obj_create_list
                 if a != b]

        for first, second in pairs:
            x = first()
            try:
                with savepoint_atomic():
                    second()
            except ValidationError:
                pass
            else:
                raise AssertionError(
                    "'{}' and '{}' do not conflict".format(
                        first.name, second.name))
            x.delete()

    def assertObjectsDontConflict(self, obj_create_list):
        pairs = [(a,b)
                 for a in obj_create_list
                 for b in obj_create_list
                 if a != b]

        for first, second in pairs:
            x = first()
            y = second()
            y.delete()
            x.delete()


class TestCase(django.test.TestCase, CyTestMixin):
    """
    Base class for all tests.
    """
    client_class = Client
    fixtures = ['core/users']

    def assertRaises(self, *args, **kwargs):
        with savepoint_atomic():
            return super(TestCase, self).assertRaises(*args, **kwargs)
