from django.test.client import Client

from nose.tools import eq_

import cyder.base.tests
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.tests.test_views_template import GenericViewTests
from cyder.cydns.tests.test_views_template import random_label
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP


def do_setUp(self, test_class, test_data, use_domain=True, use_rdomain=False):
    self.client = Client()
    self.client.login(username='development', password='password')
    self.test_class = test_class

    # Create domain.
    self.soa = SOA.objects.create(
        primary=random_label(), contact=random_label())
    self.soa2 = SOA.objects.create(
        primary=random_label(), contact=random_label())

    self.domain = Domain.objects.create(name=random_label(), soa=self.soa)
    self.subdomain = Domain.objects.create(
        name=random_label() + '.' + self.domain.name, soa=self.soa)
    self.reverse_domain = Domain.objects.create(name=random_label(),
                                                is_reverse=True, soa=self.soa2)

    # Create test object.
    test_data = dict(test_data.items())
    if use_domain:
        test_data['domain'] = self.domain
    if use_rdomain:
        test_data['reverse_domain'] = self.reverse_domain
    self.test_obj, create = test_class.objects.get_or_create(**test_data)


class AddressRecordViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'address_record'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.1',
        }
        do_setUp(self, AddressRecord, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'ip_type': '4',
            'ip_str': '196.168.1.2',
            'ttl': '400',
            'description': 'yo',
        }


class CNAMEViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'cname'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'target': random_label()
        }
        do_setUp(self, CNAME, test_data)

    def post_data(self):
        return {
            'fqdn': self.subdomain.name,
            'label': random_label(),
            'target': random_label()
        }


class NSViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'nameserver'

    def setUp(self):
        test_data = {
            'server': self.domain.name
        }
        do_setUp(self, Nameserver, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'server': self.domain.name
        }


class MXViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'mx'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }
        do_setUp(self, MX, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }


class PTRViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'ptr'

    def setUp(self):
        test_data = {
            'name': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.2',
        }
        Domain.objects.create(name='arpa')
        Domain.objects.create(name='in-addr.arpa')
        Domain.objects.create(name='196.in-addr.arpa')
        Domain.objects.create(name='168.196.in-addr.arpa')
        Domain.objects.create(name='1.168.196.in-addr.arpa')

        Domain.objects.create(name=ip_to_domain_name(test_data['ip_str']))
        do_setUp(self, PTR, test_data, use_domain=False, use_rdomain=True)

    def post_data(self):
        return {
            'name': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.3',
            'description': 'yo',
        }

    def test_update_reverse_domain(self):
        eq_(self.test_obj.reverse_domain.name, '2.1.168.196.in-addr.arpa')
        post_data = self.post_data()

        self.client.post(self.test_obj.get_update_url(), post_data,
                         follow=True)
        updated_obj = PTR.objects.get(id=self.test_obj.id)
        eq_(updated_obj.ip_str, '196.168.1.3')


class SRVViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'srv'

    def setUp(self):
        test_data = {
            'label': "_" + random_label(),
            'target': random_label(),
            'priority': 2,
            'weight': 2222,
            'port': 222
        }
        do_setUp(self, SRV, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': "_" + random_label(),
            'target': random_label(),
            'priority': 2,
            'weight': 2222,
            'port': 222
        }


class TXTViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'txt'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'txt_data': random_label()
        }
        do_setUp(self, TXT, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'txt_data': random_label()
        }


class SSHFPViewTests(cyder.base.tests.TestCase):
    fixtures = ['core/users.json']
    name = 'sshfp'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': random_label()
        }
        do_setUp(self, SSHFP, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': random_label()
        }


# Build the tests.
tests = [AddressRecordViewTests, CNAMEViewTests, MXViewTests, PTRViewTests,
         TXTViewTests]
for view_test in tests:
    builder = GenericViewTests()
    for test in builder.build_tests():
        # Set name of test.
        setattr(view_test, test.__name__ + '_' + view_test.name, test)
