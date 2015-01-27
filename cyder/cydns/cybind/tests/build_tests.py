import os
import shutil
from django.core.management import call_command
from django.test import TestCase
from time import sleep

from cyder.base.utils import remove_dir_contents
from cyder.base.vcs import GitRepo, GitRepoManager, SanityCheckFailure
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cybind.builder import DNSBuilder
from cyder.cydns.domain.models import Domain
from cyder.cydns.view.models import View


BINDBUILD = {
    'stage_dir': '/tmp/cyder_dns_test/stage',
    'prod_dir': '/tmp/cyder_dns_test/prod',
    'bind_prefix': '',
    'lock_file': '/tmp/cyder_dns_test.lock',
    'pid_file': '/tmp/cyder_dns_test.pid',
    'line_change_limit': 500,
    'line_removal_limit': 10,
    'stop_file': '/tmp/cyder_dns_test.stop',
    'stop_file_email_interval': 1800,  # 30 minutes
    'last_run_file': '/tmp/last.run',
    'log_syslog': False,
}

PROD_ORIGIN_DIR = '/tmp/cyder_dns_test/prod_origin/'


class DNSBuildTest(TestCase):
    fixtures = ['dns_build_test.json']

    def setUp(self):
        if not os.path.isdir(BINDBUILD['stage_dir']):
            os.makedirs(BINDBUILD['stage_dir'])

        if not os.path.isdir(BINDBUILD['prod_dir']):
            os.makedirs(BINDBUILD['prod_dir'])
        remove_dir_contents(BINDBUILD['prod_dir'])

        if not os.path.isdir(PROD_ORIGIN_DIR):
            os.makedirs(PROD_ORIGIN_DIR)
        remove_dir_contents(PROD_ORIGIN_DIR)

        mgr = GitRepoManager(config={
            'user.name': 'test',
            'user.email': 'test',
        })
        mgr.init(PROD_ORIGIN_DIR, bare=True)
        mgr.clone(PROD_ORIGIN_DIR, BINDBUILD['prod_dir'])

        self.builder = DNSBuilder(verbose=False, debug=False, **BINDBUILD)
        self.builder.repo.commit_and_push(empty=True, message='Initial commit')

        super(DNSBuildTest, self).setUp()

    def test_force(self):
        """Test that the 'force' argument works"""

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)
        rev1 = self.builder.repo.get_revision()

        sleep(1)  # Ensure different serial if rebuilt.
        self.builder.build()
        self.builder.push(sanity_check=False)
        rev2 = self.builder.repo.get_revision()

        self.assertEqual(rev1, rev2)

        sleep(1)  # Ensure different serial if rebuilt.
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)
        rev3 = self.builder.repo.get_revision()

        self.assertNotEqual(rev2, rev3)

    def test_build_queue(self):
        """Test that the build queue works"""

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)
        rev1 = self.builder.repo.get_revision()

        CNAME.objects.get(fqdn='foo.example.com').delete()
        s = StaticInterface.objects.get(fqdn='www.example.com')
        s.domain.soa.schedule_rebuild()

        sleep(1)  # Ensure different serial if rebuilt.
        self.builder.build()
        self.builder.push(sanity_check=False)
        rev2 = self.builder.repo.get_revision()

        self.assertNotEqual(rev1, rev2)

    def test_sanity_check1(self):
        """Test that the sanity check fails when too many lines are changed"""

        self.builder.repo.line_change_limit = 2
        self.builder.repo.line_removal_limit = 100

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        s = StaticInterface.objects.create(
            system=System.objects.get(name='Test system'),
            label='www3',
            domain=Domain.objects.get(name='example.com'),
            ip_str='192.168.0.50',
            mac='01:23:45:01:23:45',
            ctnr=Ctnr.objects.get(name='Global')
        )
        s.views.add(
            View.objects.get(name='public'),
            View.objects.get(name='private'))

        self.builder.build()
        self.assertRaises(
            SanityCheckFailure, self.builder.push, sanity_check=True)

    def test_sanity_check2(self):
        """Test that the sanity check fails when too many lines are removed"""

        self.builder.repo.line_change_limit = 100
        self.builder.repo.line_removal_limit = 2

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        CNAME.objects.get(fqdn='foo.example.com').delete()
        StaticInterface.objects.filter(
            fqdn__in=('www.example.com', 'www2.example.com')).delete()

        self.builder.build()
        self.assertRaises(
            SanityCheckFailure, self.builder.push, sanity_check=True)

    def test_sanity_check3(self):
        """Test that the sanity check succeeds when changes are sane"""

        self.builder.repo.line_change_limit = 100
        self.builder.repo.line_removal_limit = 100

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        CNAME.objects.get(fqdn='foo.example.com').delete()
        StaticInterface.objects.filter(
            fqdn__in=('www.example.com', 'www2.example.com')).delete()

        self.builder.build()
        self.builder.push(sanity_check=True)
