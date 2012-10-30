from django.test.client import Client

import cyder.base.tests
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.tests.test_views_template import GenericViewTests, random_label
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP


def do_setUp(self, url_slug, test_class, test_data, use_domain=True):
    """
    Hack hack hack, hack it up!
    """
    self.client = Client()
    self.url_slug = url_slug
    dname = random_label()
    self.domain, create = Domain.objects.get_or_create(name=dname)

    while not create:
        dname = "a" + dname
        self.domain, create = Domain.objects.get_or_create(name=dname)

    if use_domain:
        test_data = dict(test_data.items() + [('domain', self.domain)])
    self.test_obj, create = test_class.objects.get_or_create(**test_data)

    if not create:
        raise Exception


class CydnsViewTests(object):
    def setUp(self):
        self.client = Client()
        self.url_slug = url_slug
        self.domain, create = Domain.objects.get_or_create(name=random_label())

        while not create:
            dname = "a" + dname
            self.domain, create = Domain.objects.get_or_create(name=dname)
        label = random_label()
        self.test_obj, create = test_class.objects.get_or_create(
            label=label, domain=self.domain)

        while not create:
            label = "a" + label
            self.test_obj, create = test_class.objects.get_or_create(
                label=label, domain=self.domain)


class CNAMEViewTests(CydnsViewTests, cyder.base.tests.TestCase):
    def setUp(self):
        test_data = {
            'label': random_label(),
            'target': random_label()
        }
        do_setUp(self, "cname", CNAME, test_data)

    def post_data(self):
        return {
            'label': random_label(),
            'domain': self.domain.pk,
            'target': random_label()
        }

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(CNAMEViewTests, test.__name__ + "_cname", test)


class MXViewTests(CydnsViewTests, cyder.base.tests.TestCase):
    def setUp(self):
        test_data = {
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }
        do_setUp(self, "mx", MX, test_data)

    def post_data(self):
        return {
            'label': random_label(),
            'domain': self.domain.pk,
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(MXViewTests, test.__name__ + "_mx", test)


class SRVViewTests(CydnsViewTests, cyder.base.tests.TestCase):
    def setUp(self):
        test_data = {
            'label': "_" + random_label(),
            'target': random_label(),
            'priority': 2,
            'weight': 2222,
            'port': 222
        }
        do_setUp(self, "srv", SRV, test_data)

    def post_data(self):
        return {
            'label': "_" + random_label(),
            'domain': self.domain.pk,
            'target': random_label(),
            'priority': 2,
            'weight': 2222,
            'port': 222
        }

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(SRVViewTests, test.__name__ + "_srv", test)


class TXTViewTests(CydnsViewTests, cyder.base.tests.TestCase):
    def setUp(self):
        test_data = {
            'label': random_label(),
            'txt_data': random_label()
        }
        do_setUp(self, "txt", TXT, test_data)

    def post_data(self):
        return {
            'label': random_label(),
            'domain': self.domain.pk,
            'txt_data': random_label()
        }

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(TXTViewTests, test.__name__ + "_txt", test)


class SSHFPViewTests(CydnsViewTests, cyder.base.tests.TestCase):
    def setUp(self):
        test_data = {
            'label': random_label(),
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': random_label()
        }
        do_setUp(self, "sshfp", SSHFP, test_data)

    def post_data(self):
        return {
            'label': random_label(),
            'domain': self.domain.pk,
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': random_label()
        }

builder = GenericViewTests()
for test in builder.build_all_tests():
    setattr(SSHFPViewTests, test.__name__ + "_sshfp", test)
