import errno
import os

from django.test import TestCase

from cyder.base.eav.models import Attribute
from cyder.base.utils import copy_tree, remove_dir_contents
from cyder.base.vcs import GitRepo, GitRepoManager, SanityCheckFailure
from cyder.core.system.models import System
from cyder.cydhcp.build.builder import DHCPBuilder
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network, NetworkAV
from cyder.cydhcp.range.models import Range


DHCPBUILD = {
    'stage_dir': '/tmp/cyder_dhcp_test/stage',
    'prod_dir': '/tmp/cyder_dhcp_test/prod',
    'lock_file': '/tmp/cyder_dhcp_test.lock',
    'pid_file': '/tmp/cyder_dhcp_test.pid',
    'line_decrease_limit': None,
    'line_increase_limit': None,
    'stop_file': '/tmp/cyder_dhcp_test.stop',
    'stop_file_email_interval': None,  # never
    'files_v4': {
        'target_file': 'dhcpd.conf',
        'check_file': None,
    },
    'files_v6': {
        'target_file': 'dhcpd.conf.6',
        'check_file': None,
    },
}

PROD_ORIGIN_DIR = '/tmp/cyder_dhcp_test/prod_origin'


class DHCPBuildTest(TestCase):
    fixtures = ['dhcp_build_test.json']


    def build_and_push(self, sanity_check=True):
        try:
            os.remove(DHCPBUILD['stop_file'])
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        self.builder.build()
        self.builder.push(sanity_check=sanity_check)

    def setUp(self):
        if not os.path.isdir(DHCPBUILD['stage_dir']):
            os.makedirs(DHCPBUILD['stage_dir'])

        if not os.path.isdir(DHCPBUILD['prod_dir']):
            os.makedirs(DHCPBUILD['prod_dir'])
        remove_dir_contents(DHCPBUILD['prod_dir'])

        if not os.path.isdir(PROD_ORIGIN_DIR):
            os.makedirs(PROD_ORIGIN_DIR)
        remove_dir_contents(PROD_ORIGIN_DIR)

        mgr = GitRepoManager(config={
            'user.name': 'test',
            'user.email': 'test',
        })
        mgr.init(PROD_ORIGIN_DIR, bare=True)
        mgr.clone(PROD_ORIGIN_DIR, DHCPBUILD['prod_dir'])

        self.builder = DHCPBuilder(verbose=False, debug=False, **DHCPBUILD)
        self.builder.repo.commit_and_push(empty=True, message='Initial commit')

        copy_tree('cyder/cydhcp/build/tests/files/', DHCPBUILD['stage_dir'])

        super(DHCPBuildTest, self).setUp()

    def test_build_and_push(self):
        """Test that adding data triggers a rebuild"""
        self.build_and_push(sanity_check=False)

        rev1 = self.builder.repo.get_revision()

        self.build_and_push(sanity_check=False)

        rev2 = self.builder.repo.get_revision()

        self.assertEqual(rev1, rev2)

        NetworkAV.objects.create(
            entity=Network.objects.get(network_str='192.168.0.0/16'),
            attribute=Attribute.objects.get(attribute_type='o',
                                            name='routers'),
            value='192.168.0.1',
        )

        self.build_and_push(sanity_check=False)

        rev3 = self.builder.repo.get_revision()

        self.assertNotEqual(rev2, rev3)

    def test_sanity_check_increase(self):
        """Test sanity check when line count increases"""

        self.build_and_push(sanity_check=False)

        self.builder.repo.line_decrease_limit = 0  # No decrease allowed.
        self.builder.repo.line_increase_limit = 1
        d = DynamicInterface.objects.create(
            system=System.objects.get(name='Test_system_5'),
            mac='ab:cd:ef:ab:cd:ef',
            range=Range.objects.get(name='Test range 1'),
        )
        self.assertRaises(
            SanityCheckFailure, self.build_and_push)

        self.builder.repo.line_increase_limit = 100
        self.build_and_push()

    def test_sanity_check_no_change(self):
        """Test sanity check when line count doesn't change"""

        self.build_and_push(sanity_check=False)

        self.builder.repo.line_decrease_limit = 0  # No decrease allowed.
        self.builder.repo.line_increase_limit = 0  # No increase allowed.
        DynamicInterface.objects.filter(
            mac__in=('010204081020', 'aabbccddeeff')).delete()
        d = DynamicInterface.objects.create(
            system=System.objects.get(name='Test_system_5'),
            mac='ab:cd:ef:ab:cd:ef',
            range=Range.objects.get(name='Test range 1'),
        )
        self.build_and_push()

    def test_sanity_check_decrease(self):
        """Test sanity check when line count decreases"""

        self.build_and_push(sanity_check=False)

        self.builder.repo.line_increase_limit = 0  # No increase allowed
        self.builder.repo.line_decrease_limit = 1
        DynamicInterface.objects.get(mac='aa:bb:cc:dd:ee:ff').delete()
        self.assertRaises(
            SanityCheckFailure, self.build_and_push)

        self.builder.repo.line_decrease_limit = 100
        self.build_and_push()
