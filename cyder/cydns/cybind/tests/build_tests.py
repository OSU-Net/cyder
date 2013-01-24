# These tests are similar to the ones in the scripts directory. They do not ran on
# real data so the testing db needs to be filled with info.
import os
from django.test.client import RequestFactory
from django.test import TestCase

from cyder.cydns.domain.models import Domain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.view.models import View
from cyder.cydns.tests.test_views_template import  random_label, random_byte
from cyder.cydns.cybind.builder import DNSBuilder

from cyder.cydns.cybind.dnsbuilds.tests.build_tests import BuildScriptTests
from cyder.cydns.cybind.tests.helpers import create_zone_ajax


class MockBuildScriptTests(BuildScriptTests, TestCase):
    def setUp(self):
        Domain.objects.get_or_create(name="arpa")
        Domain.objects.get_or_create(name="in-addr.arpa")
        self.r1, _ = Domain.objects.get_or_create(name="10.in-addr.arpa")
        Domain.objects.get_or_create(name="com")
        Domain.objects.get_or_create(name="test.com")
        self.factory = RequestFactory()
        super(MockBuildScriptTests, self).setUp()

    def get_post_data(self, random_str):
        """Return a valid set of data"""
        return {
            'root_domain': '{0}.{0}.test.com'.format(
                                            random_label()+random_str),
            'soa_primary': 'ns1.test.com',
            'soa_contact': 'noc.test.com',
            'nameserver_1': 'ns1.test.com',
            'nameserver_2': 'ns2.test.com',
            'nameserver_3': 'ns3.test.com',
            'ttl_1': random_byte(),
            'ttl_2': random_byte(),
            'ttl_3': random_byte(),
        }

    def build_zone(self, random_str):
        # Let's use the view that should be used by a user who is creating a
        # zone. Assume it works.
        post_data = self.get_post_data(random_str)
        request = self.factory.post("/herp/derp/doesnt/matter", post_data)
        create_zone_ajax(request)
        return post_data

    def test_build_zone(self):
        self.build_zone('asdf1')
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file, LOG_SYSLOG=False,
                       FIRST_RUN=True, PUSH_TO_PROD=False)
        b.build_dns()
        self.build_zone('asdf2')
        b.build_dns()
        self.build_zone('asdf3')
        self.build_zone('asdf4')
        b.build_dns()
        self.build_zone('asdf5')
        b.build_dns()

    def test_change_a_record(self):
        post_data = self.build_zone('asdfz1')
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file, LOG_SYSLOG=False,
                       FIRST_RUN=True, PUSH_TO_PROD=False)
        b.build_dns()
        self.assertEqual((15, 0), b.svn_lines_changed())
        b.PUSH_TO_PROD = True
        b.build_dns()

        # Now add a record.
        a, c = AddressRecord.objects.get_or_create(label='',
                        domain=Domain.objects.get(name=post_data['root_domain']),
                        ip_str="10.0.0.1", ip_type='4')
        a.views.add(View.objects.get_or_create(name='private')[0])
        if not c:
            a.ttl = 8
            a.save()
        b.PUSH_TO_PROD = False
        b.build_dns()
        # added new record and new serial, old serial removed.
        self.assertEqual((2, 1), b.svn_lines_changed())

    def test_one_file_svn_lines_changed(self):
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file, LOG_SYSLOG=False,
                       FIRST_RUN=True, PUSH_TO_PROD=False)
        test_file = os.path.join(self.prod_dir, 'test')
        with open(test_file, 'w+') as fd:
            fd.write('line 1\n')
        lc = b.svn_lines_changed()
        self.assertEqual((1, 0), lc)
        b.svn_checkin(lc)

        with open(test_file, 'w+') as fd:
            fd.write('line 1\nline 2\n')

        lc = b.svn_lines_changed()
        self.assertEqual((1, 0), lc)
        b.svn_checkin(lc)

        with open(test_file, 'w+') as fd:
            fd.write('line 1\n')

        lc = b.svn_lines_changed()
        self.assertEqual((0, 1), lc)
        b.svn_checkin(lc)

    def test_two_file_svn_lines_changed(self):
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file, LOG_SYSLOG=False,
                       FIRST_RUN=True, PUSH_TO_PROD=False)
        test1_file = os.path.join(self.prod_dir, 'test1')
        test2_file = os.path.join(self.prod_dir, 'test2')
        with open(test1_file, 'w+') as fd:
            fd.write('line 1.1\n')

        lc = b.svn_lines_changed()
        self.assertEqual((1, 0), lc)
        b.svn_checkin(lc)

        with open(test1_file, 'w+') as fd:
            fd.write('line 1.1\nline 1.2\n')
        with open(test2_file, 'w+') as fd:
            fd.write('line 2.1\nline 2.2\n')

        lc = b.svn_lines_changed()
        self.assertEqual((3, 0), lc)
        b.svn_checkin(lc)

        with open(test1_file, 'w+') as fd:
            fd.write('line 1\n')

        lc = b.svn_lines_changed()
        self.assertEqual((1, 2), lc)
        b.svn_checkin(lc)

        with open(test1_file, 'w+') as fd:
            fd.write('line 1.1\nline 1.2\n')
        with open(test2_file, 'w+') as fd:
            fd.write('line 2.3\nline 2.4\n')

        lc = b.svn_lines_changed()
        self.assertEqual((4, 3), lc)
        b.svn_checkin(lc)
