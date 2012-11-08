from django.core.urlresolvers import reverse

import cyder.base.tests
from cyder.cydns.domain.models import Domain
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.test_views import random_label


class DomainViewTests(cyder.base.tests.TestCase):
    def setUp(self):
        soa = SOA(primary=random_label(
        ), contact=random_label(), comment=random_label())
        self.test_obj = Domain(name=random_label())
        self.test_obj.save()
        self.test_obj.soa = soa
        self.test_obj.save()

    def test_base_cydns_app_domain(self):
        resp = self.client.get(reverse('domain-list'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_get_create_domain(self):
        resp = self.client.get(reverse('domain-create'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_create_domain(self):
        resp = self.client.post(reverse('domain-create'),
                                self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_object_update_domain(self):
        resp = self.client.get(reverse('domain-update',
                                       args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_object_update_domain(self):
        resp = self.client.post(reverse('domain-update',
                                        args=[self.test_obj.pk]),
                                self.post_data(), follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_post_object_update_domain(self):
        resp = self.client.post(reverse('domain-update',
                                        args=[self.test_obj.pk]),
                                {'soa': ''}, follow=True)
        self.assertTrue(resp.status_code in (302, 200))

    def test_get_object_details_domain(self):
        resp = self.client.get(reverse('domain-detail',
                                       args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_get_object_delete_domain(self):
        resp = self.client.get(reverse('domain-delete',
                                       args=[self.test_obj.pk]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

    def post_data(self):
        return {
            'name': random_label()
        }
