import os
import shutil
from django.core.management import call_command
from django.test import TestCase

from cyder.base.vcs import GitRepo
from cyder.cydhcp.range.models import Range


BINDBUILD = {
    'stage_dir': '/tmp/cyder_dns_test/stage/',
    'prod_dir': '/tmp/cyder_dns_test/prod/',
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
DEBUG = False


class DNSBuildTest(TestCase):
    fixtures = ['build_test/build_test.json']

    def setUp(self):
        if os.path.isdir(BINDBUILD['prod_dir']):
            shutil.rmtree(BINDBUILD['prod_dir'])
        os.makedirs(BINDBUILD['prod_dir'])

        if os.path.isdir(PROD_ORIGIN_DIR):
            shutil.rmtree(PROD_ORIGIN_DIR)
        os.makedirs(PROD_ORIGIN_DIR)

        repo_origin = GitRepo(PROD_ORIGIN_DIR)
        repo_origin.init(bare=True)

        GitRepo.clone(PROD_ORIGIN_DIR, BINDBUILD['prod_dir'])

        self.builder = DNSBuilder(**BINDBUILD)

        self.repo = GitRepo(
            BINDBUILD['prod_dir'], BINDBUILD['line_change_limit'],
            BINDBUILD['line_removal_limit'], debug=DEBUG,
            log_syslog=False)

        super(DNSBuildTest, self).setUp()

    def test_force(self):
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev1 = self.repo.get_revision()

        self.builder.build()
        self.builder.push(sanity_check=False)

        rev2 = self.repo.get_revision()

        self.assert_equal(rev1, rev2)

        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev3 = self.repo.get_revision()

        self.assert_not_equal(rev2, rev3)

    def test_build_queue(self):
        self.builder.build(force=True)
        self.builder.push(sanity_check=False)

        rev1 = self.repo.get_revision()

        Range.objects.get(start_str='192.168.0.2')
