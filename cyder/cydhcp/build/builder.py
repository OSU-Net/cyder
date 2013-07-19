import chili_manage

from cyder.base.utils import shell_out
from cyder.cydns.cybind.builder import SVNBuilderMixin, BuildError
from cyder.settings.dhcpbuilds import (REPO_DIR, STAGE_DIR, VERBOSE_ERROR_LOG,
                                       VERBOSE_ERROR_LOG_LOCATION)
import os
import subprocess
import shlex
import syslog


class DHCPBuilder(SVNBuilderMixin):

    def __init__(self, *args, **kwargs):
        defaults = {
            'REPO_DIR': REPO_DIR,
            'STAGE_DIR': STAGE_DIR,
            'LOG_SYSLOG': True,
            'VERBOSE_ERROR_LOG': VERBOSE_ERROR_LOG,
            'VERBOSE_ERROR_LOG_LOCATION': VERBOSE_ERROR_LOG_LOCATION,
            'ERR_LOG_LEVEL': syslog.LOG_ERR,
            'DEBUG_LOG_LEVEL': syslog.LOG_DEBUG,
            'DEBUG': True,
        }
        for k, default in defaults.iteritems():
            setattr(self, k, kwargs.get(k, default))
        if self.LOG_SYSLOG:
            syslog.openlog('dhcpbuild', 0, syslog.LOG_LOCAL6)

    def build_staging(self):
        if not os.path.isdir(self.STAGE_DIR):
            try:
                os.mkdir(self.STAGE_DIR)
            except OSError, e:
                if self.DEBUG:
                    print str(e)
                if self.LOG_SYSLOG:
                    syslog.syslog(self.LOG_ERR, str(e))

    def build(self, test_syntax=True):
        cmds = ['python subnet.py',
                'python group.py',
                'python ctnr.py',
                'python vrf.py']
        if self.LOG_SYSLOG:
            syslog.syslog(self.DEBUG_LOG_LEVEL, "Dhcp builds started")
        try:
            procs = [subprocess.Popen(shlex.split(cmd)) for cmd in cmds]
            for proc in procs:
                proc.wait()
        except (OSError, ValueError), e:
            if self.DEBUG:
                print str(e)
            if self.LOG_SYSLOG:
                syslog.syslog(self.ERR_LOG_LEVEL, str(e))
        if test_syntax:
            valid, output = self.is_valid_syntax()
            if not valid:
                raise BuildError(output)
        if self.LOG_SYSLOG:
            syslog.syslog(self.DEBUG_LOG_LEVEL, "Dhcp builds finished")

    def is_valid_syntax(self):
        stdout, stderr, ret = shell_out(
            "dhcpd -t -cf {0}".format(
                os.path.join('dhcpd.conf')
            )
        )
        if ret != 0:
            if self.LOG_SYSLOG:
                syslog.syslog(
                    self.ERR_LOG_LEVEL,
                    "Dhcp builds failed due to a syntax error")
            if self.DEBUG:
                print "Dhcp builds failed due to a syntax error"
                print stderr
            return (False, stderr)
        return (True, stdout)

d = DHCPBuilder()
d.build(test_syntax=True)
