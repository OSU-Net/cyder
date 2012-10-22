from django.test import TestCase
from django.test.client import Client

from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.view_tests import random_label
from django.conf import settings


class SOAViewTests(TestCase):
    def setUp(self):
        self.url_slug = 'soa'
        self.test_obj = SOA(primary=random_label(
        ), contact=random_label(), comment=random_label())
        self.test_obj.save()

    def test_base_cydns_app_soa(self):
        resp = self.client.get(
            settings.MOZDNS_BASE_URL + "/%s/" % (self.url_slug),
            follow=True)
        self.assertEqual(resp.status_code, 200)

    # url(r'^cydns/nameserver/create$', NSCreateView.as_view()),
    def test_get_create_soa(self):
        resp = self.client.get(
            settings.MOZDNS_BASE_URL + "/%s/create/" % (self.url_slug),
            follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_create_soa(self):
        resp = self.client.post(settings.MOZDNS_BASE_URL + "/%s/create/" %
                                (self.url_slug), self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

        # url(r'^cydns/nameserver/(?P<pk>[\w-]+)/update$', NSUpdateView.as_view() ),
    def test_get_object_update_soa(self):
        resp = self.client.get(settings.MOZDNS_BASE_URL + "/%s/%s/update/" %
                               (self.url_slug, self.test_obj.pk), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_object_update_soa(self):
        resp = self.client.post(settings.MOZDNS_BASE_URL + "/%s/%s/update/" %
                                (self.url_slug, self.test_obj.pk), self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_object_details_soa(self):
        resp = self.client.get(
            settings.MOZDNS_BASE_URL + "/%s/%s/" % (self.url_slug,
                                                    self.test_obj.pk), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_get_object_delete_soa(self):
        resp = self.client.get(settings.MOZDNS_BASE_URL + "/%s/%s/delete/" %
                               (self.url_slug, self.test_obj.pk), follow=True)
        self.assertEqual(resp.status_code, 200)

    def post_data(self):
        return {'primary': random_label(), 'contact': random_label(), 'retry': '123', 'refresh': '123', 'comment': random_label()}
