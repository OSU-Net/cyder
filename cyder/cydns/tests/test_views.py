from django.test.client import Client

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
from cyder.cydns.tests.test_views_template import (GenericViewTests,
                                                   random_label)
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP


def do_setUp(self, test_class, test_data, use_domain=True, use_rdomain=False):
    self.client = Client()
    self.test_class = test_class

    # Create domain.
    self.soa = SOA.objects.create(
        primary=random_label(), contact=random_label(), comment='test')
    self.domain = Domain.objects.create(name=random_label(), soa=self.soa)
    self.subdomain = Domain.objects.create(
        name=random_label() + self.domain.name)
    self.soa2 = SOA.objects.create(
        primary=random_label(), contact=random_label(), comment='test2')
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
            'domain': self.domain.pk,
            'ip_type': '4',
            'ip_str': '196.168.1.2',
            'ttl': '400',
            'comment': 'yo',
        }


class CNAMEViewTests(cyder.base.tests.TestCase):
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
            'domain': self.subdomain.pk,
            'label': random_label(),
            'target': random_label()
        }


class NSViewTests(cyder.base.tests.TestCase):
    name = 'nameserver'

    def setUp(self):
        test_data = {
            'server': self.domain.name
        }
        do_setUp(self, Nameserver, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'domain': self.domain.pk,
            'server': self.domain.name
        }


class MXViewTests(cyder.base.tests.TestCase):
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
            'domain': self.domain.pk,
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }


class PTRViewTests(cyder.base.tests.TestCase):
    name = 'ptr'

    def setUp(self):
        test_data = {
            'name': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.2',
        }
        Domain.objects.create(name=ip_to_domain_name(test_data['ip_str']))
        do_setUp(self, PTR, test_data, use_domain=False, use_rdomain=True)

    def post_data(self):
        return {
            'data_domain': self.domain.pk,
            'reverse_domain': self.reverse_domain.pk,
            'name': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.2',
            'comment': 'yo',
        }


class SRVViewTests(cyder.base.tests.TestCase):
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
            'domain': self.domain.pk,
            'label': "_" + random_label(),
            'target': random_label(),
            'priority': 2,
            'weight': 2222,
            'port': 222
        }


class TXTViewTests(cyder.base.tests.TestCase):
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
            'domain': self.domain.pk,
            'label': random_label(),
            'txt_data': random_label()
        }


class SSHFPViewTests(cyder.base.tests.TestCase):
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
            'domain': self.domain.pk,
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
