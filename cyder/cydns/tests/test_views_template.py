import random
import string

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver


class GenericViewTests(object):
    """
    An object that builds test funtions. It's super generic and quite a huge hack.
    You need to define a setUp function like this.
    def setUp(self):
        # The url slug of the app being tested
        self.url_slug = "xxxxx"

        # A name of domain to use when creating records
        dname = "food"
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create: # This ensures that a domain is created.
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)

        # Make a generic test "object". This object is called self.test_obj and is used to test datail and
        # update views
        server = "random"
        self.test_obj, create = Nameserver.objects.get_or_create(
            server=server, domain= self.domain)
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create(
                server=server, domain= self.domain)

    This function is used to generate valid data to test views that require POST data.

        def post_data(self):
            server = random_label()
            return {'server': server, 'domain':self.domain.pk}
    """
    def build_all_tests(self):
        return (
            self.build_get_object_delete(),
            self.build_get_object_details(),
            self.build_post_object_update(),
            self.build_get_object_update(),
            self.build_post_create_in_domain(),
            self.build_get_create_in_domain(),
            self.build_post_create(),
            self.build_base_cydns_app(),
            self.build_get_create(),
            lambda junk: True
        )

    def build_base_cydns_app(self):
        """
        ex: url(r'^/cydns/domain/$', DomainListView.as_view()),
        """
        def test_base_cydns_app(self):
            resp = self.client.get(reverse(self.url_slug + '-list'),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_base_cydns_app

    def build_get_create(self):
        """
        ex: url(r'^/cydns/domain/create/$', DomainCreateView.as_view()),
        """
        def test_get_create(self):
            resp = self.client.get(reverse(self.url_slug + '-create'),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_create

    def build_post_create(self):
        def test_post_create(self):
            resp = self.client.post(reverse(self.url_slug + '-create'),
                                    self.post_data(), follow=True)
            self.assertTrue(resp.status_code in (302, 200))
        return test_post_create

    def build_get_create_in_domain(self):
        """
        ex: url(r'^/cydns/domain/(?P<domain>[\w-]+)/create$', DomainCreateView.as_view()),
        """
        def test_get_create_in_domain(self):
            resp = self.client.get(reverse(self.url_slug + '-create-in-domain',
                                           args=[self.domain.pk]),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_create_in_domain

    def build_post_create_in_domain(self):
        def test_post_create_in_domain(self):
            resp = self.client.post(reverse(self.url_slug + '-create-in-domain',
                                            args=[self.domain.pk]),
                                    self.post_data(), follow=True)
            self.assertTrue(resp.status_code in (302, 200))
        return test_post_create_in_domain

    def build_get_object_update(self):
        """
        ex: url(r'^/cydns/domain/(?P<pk>[\w-]+)/update$', DomainUpdateView.as_view()),
        """
        def test_get_object_update(self):
            resp = self.client.get(reverse(self.url_slug + '-update',
                                           args=[self.test_obj.pk]),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_update

    def build_post_object_update(self):
        def test_post_object_update(self):
            resp = self.client.post(reverse(self.url_slug + '-update',
                                            args=[self.test_obj.pk]),
                                    self.post_data(),
                                    follow=True)
            self.assertTrue(resp.status_code in (302, 200))
            pass
        return test_post_object_update

    def build_get_object_details(self):
        """
        ex: url(r'^/cydns/domain/(?P<pk>[\w-]+)/$', DomainDetailView.as_view()),
        """
        def test_get_object_details(self):
            resp = self.client.get(reverse(self.url_slug + '-detail',
                                           args=[self.test_obj.pk]),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_details

    def build_get_object_delete(self):
        """
        ex: url(r'^/cydns/domain/(?P<pk>[\w-]+)/delete$', DomainDeleteView.as_view())
        """
        def test_get_object_delete(self):
            resp = self.client.get(reverse(self.url_slug + '-delete',
                                           args=[self.test_obj.pk]),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_delete


def random_label():
    """
    Utility function to generate a random *valid* label.
    """
    label = ''
    for i in range(random.randint(5, 30)):
        label += string.letters[random.randint(0, len(string.letters) - 1)]
    return label


def random_byte():
    """
    Utility function to generate a random byte for random IPs
    """
    return random.randint(0, 255)
