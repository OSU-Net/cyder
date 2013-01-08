from django.core.urlresolvers import reverse

import cyder.base.tests
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.test_views import random_label


class SOAViewTests(cyder.base.tests.TestCase):
    def setUp(self):
        self.test_obj = SOA(primary=random_label(
        ), contact=random_label(), description=random_label())
        self.test_obj.save()

    def test_base_cydns_app_soa(self):
        resp = self.client.get(reverse('soa-list'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_get_create_soa(self):
        resp = self.client.get(reverse('soa-create'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_create_soa(self):
        resp = self.client.post(reverse('soa-create'),
                                self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_object_update_soa(self):
        resp = self.client.get(reverse('soa-update', args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_object_update_soa(self):
        resp = self.client.post(reverse('soa-update', args=[self.test_obj.pk]),
                                self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_object_details_soa(self):
        resp = self.client.get(reverse('soa-detail', args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_get_object_delete_soa(self):
        resp = self.client.get(reverse('soa-delete', args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def post_data(self):
        return {'primary': random_label(), 'contact': random_label(), 'retry':
                '123', 'refresh': '123', 'description': random_label()}
