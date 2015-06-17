import errno
import os
import shutil
from django.core.management import call_command
from django.test import TestCase
from time import sleep

from cyder.base.utils import remove_dir_contents
from cyder.base.vcs import GitRepo, GitRepoManager, SanityCheckFailure
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
    'line_decrease_limit': 10,
    'line_increase_limit': 500,
    'stop_file': '/tmp/cyder_dns_test.stop',
    'stop_file_email_interval': None,  # never
    'last_run_file': '/tmp/last.run',
    'log_syslog': False,
}

PROD_ORIGIN_DIR = '/tmp/cyder_dns_test/prod_origin/'


class DNSBuildTest(TestCase):
    fixtures = ['dns_build_test.json']

    def build_and_push(self, force=False, sanity_check=True):
        """
        force: whether to force unchanged zones to be rebuilt
        sanity_check: whether to run the diff sanity check
        """

        try:
            os.remove(BINDBUILD['stop_file'])
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        self.builder.build(force=force)
        self.builder.push(sanity_check=sanity_check)

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

        self.build_and_push(force=True, sanity_check=False)
        rev1 = self.builder.repo.get_revision()

        sleep(1)  # Ensure different serial if rebuilt.
        self.build_and_push(sanity_check=False)
        rev2 = self.builder.repo.get_revision()

        self.assertEqual(rev1, rev2)

        sleep(1)  # Ensure different serial if rebuilt.
        self.build_and_push(force=True, sanity_check=False)
        rev3 = self.builder.repo.get_revision()

        self.assertNotEqual(rev2, rev3)

    def test_build_queue(self):
        """Test that the build queue works"""

        self.build_and_push(force=True, sanity_check=False)
        rev1 = self.builder.repo.get_revision()

        CNAME.objects.get(fqdn='foo.example.com').delete()
        s = StaticInterface.objects.get(fqdn='www.example.com')
        s.domain.soa.schedule_rebuild()

        sleep(1)  # Ensure different serial if rebuilt.
        self.build_and_push(sanity_check=False)
        rev2 = self.builder.repo.get_revision()

        self.assertNotEqual(rev1, rev2)

    def test_sanity_check_increase(self):
        """Test sanity check when line count increases"""

        self.build_and_push(force=True, sanity_check=False)

        self.builder.repo.line_decrease_limit = 0  # No decrease allowed.
        self.builder.repo.line_increase_limit = 1
        sys = System.objects.get(name='Test system')
        s = StaticInterface.objects.create(
            system=sys,
            label='www3',
            domain=Domain.objects.get(name='example.com'),
            ip_str='192.168.0.50',
            mac='01:23:45:01:23:45',
        )
        s.views.add(
            View.objects.get(name='public'),
            View.objects.get(name='private'))
        self.assertRaises(SanityCheckFailure, self.build_and_push, force=True)

        self.builder.repo.line_increase_limit = 100
        self.build_and_push()

    def test_sanity_check_no_change(self):
        """Test that the sanity check succeeds when changes are sane"""

        self.builder.repo.line_decrease_limit = 0
        self.builder.repo.line_increase_limit = 0

        self.build_and_push(force=True, sanity_check=False)

        sys = System.objects.get(name='Test system')
        s = StaticInterface.objects.create(
            system=sys,
            label='www3',
            domain=Domain.objects.get(name='example.com'),
            ip_str='192.168.0.50',
            mac='01:23:45:01:23:45',
        )
        s.views.add(
            View.objects.get(name='public'),
            View.objects.get(name='private'))
        StaticInterface.objects.get(fqdn='www2.example.com').delete()
        self.build_and_push()

    def test_sanity_check_decrease(self):
        """Test sanity check when line count decreases"""

        self.build_and_push(force=True, sanity_check=False)

        self.builder.repo.line_increase_limit = 0  # No increase allowed.
        self.builder.repo.line_decrease_limit = 1
        CNAME.objects.get(fqdn='foo.example.com').delete()
        StaticInterface.objects.filter(
            fqdn__in=('www.example.com', 'www2.example.com')).delete()
        self.assertRaises(SanityCheckFailure, self.build_and_push)

        self.builder.repo.line_decrease_limit = 100
        self.build_and_push()
