import os
import shutil
from django.core.management import call_command
from django.test import TestCase
from time import sleep

from cyder.base.utils import remove_dir_contents
from cyder.base.vcs import GitRepo
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.cybind.builder import DNSBuilder


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

        repo_origin = GitRepo(PROD_ORIGIN_DIR)
        repo_origin.init(bare=True)

        GitRepo.clone(PROD_ORIGIN_DIR, BINDBUILD['prod_dir'])

        self.builder = DNSBuilder(verbose=False, debug=False, **BINDBUILD)

        self.builder.repo.commit_and_push(empty=True,
                                          message='Initial commit')

        super(DNSBuildTest, self).setUp()

    def test_force(self):
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev1 = self.builder.repo.get_revision()

        sleep(1)  # ensure different serial if rebuilt
        self.builder.build()
        self.builder.push(sanity_check=False)

        rev2 = self.builder.repo.get_revision()

        self.assertEqual(rev1, rev2)

        sleep(1)
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev3 = self.builder.repo.get_revision()

        self.assertNotEqual(rev2, rev3)

    def test_build_queue(self):
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev1 = self.builder.repo.get_revision()

        s = StaticInterface.objects.get(fqdn='www.example.com')
        s.schedule_rebuild_check()

        sleep(1)
        self.builder.build()
        self.builder.push(sanity_check=False)

        rev2 = self.builder.repo.get_revision()

        self.assertNotEqual(rev1, rev2)
