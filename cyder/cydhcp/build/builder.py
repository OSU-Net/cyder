from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup

from cyder.base.utils import shell_out
from cyder.cydns.cybind.builder import SVNBuilderMixin, BuildError
from cyder.settings import DHCPBUILD
import os
import subprocess
import shlex
import syslog


class DHCPBuilder(MutexMixin):
    def __init__(self, *args, **kwargs):
        kwargs = dict_merge(DHCPBUILD, {
            'debug': True,
        }, kwargs)
        set_attrs(self, kwargs)

        if self.log_syslog:
            syslog.openlog('dhcpbuild', 0, syslog.LOG_LOCAL6)

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

    def build(self, test_syntax=True):
        try:
            with open(self.stop_file) as stop_fd:
                now = time.time()
                contents = stop_fd.read()
            last = os.path.getmtime(self.stop_file)

            msg = ("The stop file ({0}) exists. Build canceled.\n"
                   "Reason for skipped build:\n"
                   "{1}".format(self.stop_file, contents))
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

        if self.LOG_SYSLOG:
            syslog.syslog(self.DEBUG_LOG_LEVEL, "DHCP builds started")
        with open(os.path.join(self.STAGE_DIR, self.TARGET_FILE), 'w') as f:
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
                if self.DEBUG:
                    print str(e)
                if self.LOG_SYSLOG:
                    syslog.syslog(self.ERR_LOG_LEVEL, str(e))
        if test_syntax and self.CHECK_FILE:
            valid, output = self.is_valid_syntax()
            if not valid:
                raise BuildError(output)
        if self.LOG_SYSLOG:
            syslog.syslog(self.DEBUG_LOG_LEVEL, "DHCP builds finished")

    def is_valid_syntax(self):
        stdout, stderr, ret = shell_out(
            "{0} -t -cf {1}".format(
                self.dhcpd,
                os.path.join(self.stage_dir, self.check_file)
            )
        )
        if ret != 0:
            if self.LOG_SYSLOG:
                syslog.syslog(
                    self.ERR_LOG_LEVEL,
                    "DHCP builds failed due to a syntax error")
            if self.DEBUG:
                print "DHCP builds failed due to a syntax error"
                print stderr
            return (False, stderr)
        return (True, stdout)
