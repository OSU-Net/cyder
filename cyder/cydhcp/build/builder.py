from __future__ import unicode_literals

import os
import shlex
import subprocess
import syslog
from distutils.dir_util import copy_tree

from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup

from cyder.base.utils import dict_merge, log, MutexMixin, set_attrs, shell_out
from cyder.base.vcs import GitRepo
from cyder.settings import DHCPBUILD


class BuildError(Exception):
    """Exception raised when there is an error in the build process."""


class DHCPBuilder(MutexMixin):
    """
    DHCPBuilder must be instantiated from a `with` statement. Its __exit__
    method releases a mutex, so it's critical that it be called regardless of
    the reason the Python interpreter exits. __del__ is not sufficient because
    CPython is not guaranteed to delete objects involved in circular
    references even when every object in the circular reference goes out of
    scope.
    """
    def __init__(self, *args, **kwargs):
        kwargs = dict_merge(DHCPBUILD, {
            'debug': True,
        }, kwargs)
        set_attrs(self, kwargs)

        if self.log_syslog:
            syslog.openlog(b'dhcpbuild', 0, syslog.LOG_LOCAL6)

        self.repo = GitRepo(self.prod_dir, self.max_allowed_lines_changed,
            debug=True, log_syslog=True, logger=syslog)

    def log(self, *args, **kwargs):
        kwargs = dict_merge({
            'to_syslog': self.log_syslog,
            'logger': syslog,
        }, kwargs)

        log(*args, **kwargs)

    def log_debug(self, msg, to_stderr=None):
        if to_stderr is None:
            to_stderr = self.debug
        self.log(msg, log_level='LOG_DEBUG', to_stderr=to_stderr)

    def log_info(self, msg, to_stderr=True):
        self.log(msg, log_level='LOG_INFO', to_stderr=to_stderr)

    def log_notice(self, msg, to_stderr=True):
        self.log(msg, log_level='LOG_NOTICE', to_stderr=to_stderr)

    def log_err(self, msg, to_stderr=True):
        self.log(msg, log_level='LOG_ERR', to_stderr=to_stderr)

    def build(self):
        try:
            with open(self.stop_file) as stop_fd:
                now = time.time()
                contents = stop_fd.read()
            last = os.path.getmtime(self.stop_file)

            msg = ('The stop file ({0}) exists. Build canceled.\n'
                   'Reason for skipped build:\n'
                   '{1}'.format(self.stop_file, contents))
            self.log_info(msg, to_stderr=False)
            if now - last > self.stop_file_email_interval:
                os.utime(self.stop_file, (now, now))
                fail_mail(msg, subject="DHCP builds have stopped")

            raise BuildError(msg)
        except IOError as e:
            if e.errno == 2:  # IOError: [Errno 2] No such file or directory
                pass
            else:
                raise

        self.log_debug('Building...')

        with open(os.path.join(self.stage_dir, self.target_file), 'w') as f:
            try:
                for ctnr in Ctnr.objects.all():
                    f.write(ctnr.build_legacy_classes())
                for vrf in Vrf.objects.all():
                    f.write(vrf.build_vrf())
                for network in Network.objects.filter(enabled=True):
                    f.write(network.build_subnet())
                for workgroup in Workgroup.objects.all():
                    f.write(workgroup.build_workgroup())
            except (OSError, ValueError), e:
                self.log_err(e)

        if test_syntax and self.CHECK_FILE:
            self.check_syntax()

        self.log_debug('DHCP build successful')

    def push(self, sanity_check=True):
        self.repo.reset_and_pull()

        try:
            copy_tree(self.stage_dir, self.prod_dir)
        except:
            self.repo.reset_to_head()
            raise

        self.repo.commit_and_push('Update config', sanity_check=sanity_check)

    def check_syntax(self):
        out, err, ret = shell_out("{0} -t -cf {1}".format(
            self.dhcpd, os.path.join(self.stage_dir, self.check_file)
        ))
        if ret != 0:
            log_msg = 'DHCP build failed due to a syntax error'
            extra = ('{0} said:\n'
                     '{1}'
                     .format(self.dhcpd, err))
            self.log_err(log_msg, to_stderr=False)
            raise BuildError(log_msg + '\n' + extra)

    def _lock_failure(self):
        self.log_err(
            'DHCP build script attempted to acquire the build mutux but '
            'another process already has it.',
            to_stderr=False)
        fail_mail(
            'An attempt was made to start the DHCP build script while an '
            'instance of the script was already running. The attempt was '
            'denied.',
            subject="Concurrent DHCP builds attempted.")
        super(DNSBuilder, self)._lock_failure()
