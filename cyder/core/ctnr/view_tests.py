from django.test import TestCase
from django.test.client import Client

from cyder.core.ctnr.models import Ctnr
from cyder.cydns.tests.view_tests import random_label


class CtnrViewTests(TestCase):
    def setUp(self):
        self.url_slug = 'ctnr'
        self.ctnr = Ctnr(name=random_label())
        self.ctnr.save()

    def test_base_app_ctnr(self):
        resp = self.client.get('/%s/' % (self.url_slug))
        self.assertEqual(resp.status_code, 200)

    def test_get_create_ctnr(self):
        resp = self.client.get('/%s/create/' % (self.url_slug))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_ctnr(self):
        resp = self.client.post('/%s/create/' % (self.url_slug), self.post_data())
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_update_ctnr(self):
        resp = self.client.get('/%s/%s/update/' % (self.url_slug, self.ctnr.pk))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_ctnr(self):
        resp = self.client.post('/%s/%s/update/' % (self.url_slug, self.ctnr.pk), self.post_data())
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_details_ctnr(self):
        resp = self.client.get('/%s/%s/' % (self.url_slug, self.ctnr.pk))
        self.assertEqual(resp.status_code, 200)

    def test_get_delete_ctnr(self):
        resp = self.client.get('/%s/%s/delete/' % (self.url_slug, self.ctnr.pk))
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_change_ctnr(self):
        resp = self.client.get('/%s/%s/change/' % (self.url_slug, self.ctnr.pk))
        self.assertTrue(resp.status_code in (302, 200))

    def test_post_change_ctnr(self):
        resp = self.client.get('/%s/change/' % (self.url_slug), {'id':self.ctnr.pk})
        self.assertTrue(resp.status_code in (302, 200))

    def post_data(self):
        return {
            'name': random_label()
        }
