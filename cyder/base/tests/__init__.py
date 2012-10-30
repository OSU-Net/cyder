from django.test import TestCase
from django.test.client import Client


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


class TestCase(TestCase, CyTestMixin):
    """
    Base class for all tests.
    """
    client_class = Client
    fixtures = ['core/users']
