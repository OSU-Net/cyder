import os
from django.test import TestCase

from cyder.base.eav.models import Attribute
from cyder.base.utils import copy_tree, remove_dir_contents
from cyder.base.vcs import GitRepo
from cyder.cydhcp.build.builder import DHCPBuilder
from cyder.cydhcp.network.models import Network, NetworkAV

from cyder.cydhcp.range.models import Range


DHCPBUILD = {
    'stage_dir': '/tmp/cyder_dhcp_test/stage',
    'prod_dir': '/tmp/cyder_dhcp_test/prod',
    'lock_file': '/tmp/cyder_dhcp_test.lock',
    'pid_file': '/tmp/cyder_dhcp_test.pid',
    'target_file': 'dhcpd.conf.data',
    'check_file': 'dhcpd.conf',
    'line_change_limit': 500,
    'line_removal_limit': None,
    'stop_file': '/tmp/cyder_dhcp_test.stop',
    'stop_file_email_interval': None,  # never
    'log_syslog': False,
}

PROD_ORIGIN_DIR = '/tmp/cyder_dhcp_test/prod_origin'


class DHCPBuildTest(TestCase):
    fixtures = ['dhcp_build_test.json']

    def setUp(self):
        if not os.path.isdir(DHCPBUILD['stage_dir']):
            os.makedirs(DHCPBUILD['stage_dir'])

        if not os.path.isdir(DHCPBUILD['prod_dir']):
            os.makedirs(DHCPBUILD['prod_dir'])
        remove_dir_contents(DHCPBUILD['prod_dir'])

        if not os.path.isdir(PROD_ORIGIN_DIR):
            os.makedirs(PROD_ORIGIN_DIR)
        remove_dir_contents(PROD_ORIGIN_DIR)

        repo_origin = GitRepo(PROD_ORIGIN_DIR)
        repo_origin.init(bare=True)

        GitRepo.clone(PROD_ORIGIN_DIR, DHCPBUILD['prod_dir'])

        self.builder = DHCPBuilder(verbose=False, debug=False, **DHCPBUILD)

        self.builder.repo.commit_and_push(empty=True,
                                          message='Initial commit')

        copy_tree('cyder/cydhcp/build/tests/files/', DHCPBUILD['stage_dir'])

        super(DHCPBuildTest, self).setUp()

    def test_build_and_push(self):
        self.builder.build()
        self.builder.push()

        rev1 = self.builder.repo.get_revision()

        self.builder.build()
        self.builder.push()

        rev2 = self.builder.repo.get_revision()

        self.assertEqual(rev1, rev2)

        NetworkAV(
            entity=Network.objects.get(network_str='192.168.0.0/16'),
            attribute=Attribute.objects.get(attribute_type='o',
                                            name='routers'),
            value='192.168.0.1'
        ).save()

        self.builder.build()
        self.builder.push()

        rev3 = self.builder.repo.get_revision()

        self.assertNotEqual(rev2, rev3)
