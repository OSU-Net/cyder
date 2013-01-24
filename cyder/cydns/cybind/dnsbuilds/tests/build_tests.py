import os
import subprocess
import shutil
import shlex
import sys
import unittest

from unittest import TestCase
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.pardir, os.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.pardir, os.pardir, os.pardir)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.base'

#import manage

from cydns.cybind.builder import DNSBuilder, BuildError
from cydns.soa.models import SOA



class BuildScriptTests(object):
    """These test cases test the build scripts and should be able to run
    outside of the django test runner. No checkins should happen during any
    test.
    """

    def setUp(self):
        self.stage_dir = '/tmp/fake/stage/inv_zones/'
        self.svn_dir = '/tmp/fake/dnsconfig/'
        self.prod_dir = '/tmp/fake/dnsconfig/inv_zones/'
        self.svn_repo = '/tmp/fake/svn_repo'
        self.lock_file = '/tmp/fake/lock.fake'
        if os.path.isdir('/tmp/fake/'):
            shutil.rmtree('/tmp/fake')
            os.makedirs('/tmp/fake')
        command_str = "svnadmin create {0}".format(self.svn_repo)
        os.makedirs(self.svn_repo)
        rets = subprocess.Popen(shlex.split(command_str),
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        stdout, stderr = rets.communicate()
        self.assertEqual(0, rets.returncode)

        command_str = "svn co file://{0} {1}".format(self.svn_repo,
                                                     self.prod_dir)
        rets = subprocess.Popen(shlex.split(command_str),
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        stdout, stderr = rets.communicate()
        self.assertEqual(0, rets.returncode)

    def tearDown(self):
        #shutil.rmtree('/tmp/fake/')
        pass

    def svn_info(self):
        cwd = os.getcwd()
        os.chdir('/tmp/fake/dnsconfig/inv_zones/')
        command_str = "svn info"
        rets = subprocess.Popen(shlex.split(command_str),
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        stdout, stderr = rets.communicate()
        self.assertEqual(0, rets.returncode)
        print stdout
        os.chdir(cwd)

    def test_build_svn(self):
        print "This will take a while, be patient..."
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file, LOG_SYSLOG=False,
                       FIRST_RUN=True, PUSH_TO_PROD=True)
        b.build_dns()
        #self.svn_info()
        s = SOA.objects.all()
        if len(s) > 0:
            s[0].dirty = True
            s[0].save()
        b.build_dns()
        #self.svn_info()
        b.build_dns()
        #self.svn_info()

    def test_svn_lines_changed(self):
        pass

    def test_build_staging(self):
        if os.path.isdir(self.stage_dir):
            shutil.rmtree(self.stage_dir)
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file)
        b.build_staging()
        # Make sure it made the staging dir
        self.assertTrue(os.path.isdir(self.stage_dir))
        # Ensure if fails if the directory exists
        self.assertRaises(BuildError, b.build_staging)
        # There shouldn't be errors because force=True
        b.build_staging(force=True)

        self.assertTrue(os.path.isdir(self.stage_dir))
        b.clear_staging()
        self.assertFalse(os.path.isdir(self.stage_dir))
        self.assertRaises(BuildError, b.clear_staging)
        b.clear_staging(force=True)
        self.assertFalse(os.path.isdir(self.stage_dir))

    def test_lock_unlock(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
        b = DNSBuilder(STAGE_DIR=self.stage_dir, PROD_DIR=self.prod_dir,
                       LOCK_FILE=self.lock_file)
        self.assertFalse(os.path.exists(self.lock_file))
        b.lock()
        self.assertTrue(os.path.exists(self.lock_file))
        for i in xrange(10):
            b.unlock()
            b.lock()

        b.unlock()
        self.assertTrue(os.path.exists(self.lock_file))

        b.lock()
        self.assertTrue(os.path.exists(self.lock_file))

        b.unlock()
        self.assertTrue(os.path.exists(self.lock_file))


class LiveBuildScriptTests(BuildScriptTests, TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
