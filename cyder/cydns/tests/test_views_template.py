import random
import string

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver


class GenericViewTests(object):
    """
    An object that builds test funtions. It's super generic and quite a huge
    hack. You need to define a setUp function like this.
    def setUp(self):
        # The url slug of the app being tested
        self.url_slug = "xxxxx"

        # A name of domain to use when creating records
        dname = "food"
        self.domain, create = Domain.objects.get_or_create(name=dname)
        while not create: # This ensures that a domain is created.
            dname = "a"+dname
            self.domain, create = Domain.objects.get_or_create(name=dname)

        # Make a generic test "object". This object is called self.test_obj and
        # is used to test datail and update views
        server = "random"
        self.test_obj, create = Nameserver.objects.get_or_create(
            server=server, domain= self.domain)
        while not create:
            server = "a"+server
            self.test_obj, create = Nameserver.objects.get_or_create(
                server=server, domain= self.domain)

    This function is used to generate valid data to test views that require
    POST data.

        def post_data(self):
            server = random_label()
            return {'server': server, 'domain':self.domain.pk}
    """
    def build_all_tests(self):
        return (
            self.build_base_cydns_app(),
            self.build_get_create(),
            self.build_post_create(),
            self.build_post_object_update(),
            self.build_get_object_update(),
            self.build_get_object_delete(),
            self.build_get_object_details(),
            lambda junk: True
        )

    def build_base_cydns_app(self):
        """
        List view.
        """
        def test_base_cydns_app(self):
            resp = self.client.get(self.test_class.get_list_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_base_cydns_app

    def build_get_create(self):
        """
        List view, get.
        """
        def test_get_create(self):
            resp = self.client.get(self.test_class.get_create_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_create

    def build_post_create(self):
        """
        Create view, post.
        """
        def test_post_create(self):
            resp = self.client.post(self.test_class.get_create_url(),
                                    self.post_data(), follow=True)
            self.assertTrue(resp.status_code in (302, 200))
        return test_post_create

    def build_get_object_update(self):
        """
        Update view, get. DEPRECATED.
        """
        def test_get_object_update(self):
            resp = self.client.get(self.test_obj.get_update_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_update

    def build_post_object_update(self):
        """
        Update view, post.
        """
        def test_post_object_update(self):
            resp = self.client.post(self.test_obj.get_update_url(),
                                    self.post_data(),
                                    follow=True)
            self.assertTrue(resp.status_code in (302, 200))
            pass
        return test_post_object_update

    def build_get_object_delete(self):
        """
        Delete view.
        """
        def test_get_object_delete(self):
            resp = self.client.post(self.test_obj.get_delete_url(),
                                    follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_delete

    def build_get_object_details(self):
        """
        Detail view.
        """
        def test_get_object_details(self):
            resp = self.client.get(self.test_obj.get_detail_url(),
                                   follow=True)
            self.assertEqual(resp.status_code, 200)
        return test_get_object_details


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
