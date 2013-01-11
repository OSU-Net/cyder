#!/usr/bin/python
from gettext import gettext as _
import inspect
import fcntl
import shutil
import shlex
import subprocess
import syslog
import os
import re
import time

from cyder.settings.dnsbuilds import STAGE_DIR, PROD_DIR, LOCK_FILE
from cyder.settings.dnsbuilds import NAMED_CHECKZONE_OPTS, MAX_ALLOWED_LINES_CHANGED


from cyder.cydns.domain.models import SOA
from cyder.cydns.view.models import View
from cyder.cydns.cybind.zone_builder import build_zone_data
from cyder.cydns.cybind.models import DNSBuildRun
from cyder.cydns.cybind.serial_utils import get_serial

class BuildError(Exception):
    """Exception raised when there is an error in the build process."""

class SVNBuilderMixin(object):
    svn_ignore = [re.compile("---\s.+\s+\(revision\s\d+\)"),
                  re.compile("\+\+\+\s.+\s+\(working copy\)")]

    vcs_type = 'svn'

    def svn_lines_changed(self):
        """This function will collect some metrics on how many lines were added
        and removed during the build process.

        :returns: (int, int) -> (lines_added, lines_removed)

        The current implementation of this function uses the underlying svn
        repo to generate a diff and then counts the number of lines that start
        with '-' or '+'. This causes the accuracy of this function to have
        slight errors because some lines in the diff output start with '-' or
        '+' but aren't indicative of a line being removed or added. Since the
        threashold of lines changing is in the hundreds of lines, an error of
        tens of lines is not a large concern.
        """
        cwd = os.getcwd()
        os.chdir(self.PROD_DIR)
        try:
            command_str = "svn add --force .".format(self.PROD_DIR)
            stdout, stderr, returncode = self.shell_out(command_str)
            if returncode != 0:
                raise BuildError("\nFailed to add files to svn."
                                 "\ncommand: {0}:\nstdout: {1}\nstderr:{2}".
                                 format(command_str, stdout, stderr))
            command_str = "svn diff --depth=infinity ."
            stdout, stderr, returncode = self.shell_out(command_str)
            if returncode != 0:
                raise BuildError("\nFailed to add files to svn."
                                 "\ncommand: {0}:\nstdout: {1}\nstderr:{2}".
                                 format(command_str, stdout, stderr))
        except Exception:
            raise
        finally:
            os.chdir(cwd)  # go back!

        la, lr = 0, 0
        def svn_ignore(line):
            for ignore in self.svn_ignore:
                if ignore.match(line):
                    return True
            return False
        for line in stdout.split('\n'):
            if svn_ignore(line):
                continue
            if line.startswith('-'):
                lr += 1
            elif line.startswith('+'):
                la += 1
        return la, lr

    def svn_sanity_check(self, lines_changed):
        """If sanity checks fail, this function will return a string which is
        True-ish. If all sanity cheecks pass, a Falsy value will be
        returned."""
        # svn diff changes and react if changes are too large
        if ((lambda x, y: x + y)(*lines_changed) >
             MAX_ALLOWED_LINES_CHANGED):
            pass
        # email and fail
            # Make sure we can run the script again
            # rm -rf stage/
            # rm lock.file
        return False

    def svn_checkin(self, lines_changed):
        # svn add has already been called
        cwd = os.getcwd()
        os.chdir(self.PROD_DIR)
        self.log('LOG_INFO', "Changing pwd to {0}".format(self.PROD_DIR))
        try:
            """
            command_str = "svn add --force .".format(self.PROD_DIR)
            stdout, stderr, returncode = self.shell_out(command_str)
            if returncode != 0:
                raise BuildError("\nFailed to add files to svn."
                                 "\ncommand: {0}:\nstdout: {1}\nstderr:{2}".
                                 format(command_str, stdout, stderr))
            """

            ci_message = _("Checking in DNS. {0} lines were added and {1} were"
                           " removed".format(*lines_changed))
            self.log('LOG_INFO', "Commit message: {0}".format(ci_message))
            command_str = "svn ci {0} -m \"{1}\"".format(self.PROD_DIR, ci_message)
            stdout, stderr, returncode = self.shell_out(command_str)
            if returncode != 0:
                raise BuildError("\nFailed to check in changes."
                                 "\ncommand: {0}:\nstdout: {1}\nstderr:{2}".
                                 format(command_str, stdout, stderr))
            else:
                self.log('LOG_INFO', "Changes have been checked in.")
        finally:
            os.chdir(cwd)  # go back!
            self.log('LOG_INFO', "Changing pwd to {0}".format(cwd))
        return

    def vcs_checkin(self):
        lines_changed = self.svn_lines_changed()
        self.svn_sanity_check(lines_changed)
        if lines_changed == (0, 0):
            self.log('LOG_INFO', "PUSH_TO_PROD is True but "
                     "svn_lines_changed found that no lines different "
                     "from last svn checkin.")
        else:
            self.log('LOG_INFO', "PUSH_TO_PROD is True. Checking into "
                     "svn.")
            self.svn_checkin(lines_changed)


class DNSBuilder(SVNBuilderMixin):
    def __init__(self, **kwargs):
        defaults = {
            'STAGE_DIR': STAGE_DIR,
            'PROD_DIR': PROD_DIR,
            'LOCK_FILE': LOCK_FILE,
            'STAGE_ONLY': False,
            'NAMED_CHECKZONE_OPTS': NAMED_CHECKZONE_OPTS,
            'CLOBBER_STAGE': False,
            'PUSH_TO_PROD': False,
            'BUILD_ZONES': True,
            'PRESERVE_STAGE': False,
            'LOG_SYSLOG': True,
            'DEBUG': False,
            'bs': DNSBuildRun()  # Build statistic
        }
        for k, default in defaults.iteritems():
            setattr(self, k, kwargs.get(k, default))

        # This is very specific to python 2.6
        syslog.openlog('dnsbuild', 0, syslog.LOG_USER)
        self.lock_fd = None

    def log(self, log_level, msg, **kwargs):
        # Eventually log this stuff into bs
        # Let's get the callers name and log that
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        callername = calframe[1][3]
        fmsg = "[{0}] {1}".format(callername, msg)
        if hasattr(syslog, log_level):
            ll = getattr(syslog, log_level)
        else:
            ll = syslog.LOG_INFO

        if self.LOG_SYSLOG:
            syslog.syslog(ll, fmsg)
        if self.DEBUG:
            print "{0} {1}".format(log_level, fmsg)

    def build_staging(self, force=False):
        """
        Create the stage folder. Fail if it already exists unless
        force=True.
        """
        if os.path.exists(self.STAGE_DIR) and not force:
            raise BuildError("The DNS build scripts tried to build the staging"
                             " but area already exists.")
        try:
            os.makedirs(self.STAGE_DIR)
        except OSError:
            if not force:
                raise

    def clear_staging(self, force=False):
        """
        rm -rf the staging area. Fail if the staging area doesn't exist.
        """
        self.log('LOG_INFO', "Attempting rm -rf staging "
                 "area. ({0})...".format(self.STAGE_DIR))
        if os.path.exists(self.STAGE_DIR) or force:
            try:
                shutil.rmtree(self.STAGE_DIR)
            except OSError, e:
                if e.errno == 2:
                    self.log('LOG_WARNING', "Staging was "
                             "not present.")
                else:
                    raise
            self.log('LOG_INFO', "Staging area cleared")
        else:
            if not force:
                raise BuildError("The DNS build scripts tried to remove the "
                                 "staging area but the staging area didn't "
                                 "exist.")

    def lock(self):
        """
        Try to write a lock file. Fail if the lock already exists.
        """
        try:
            if not os.path.exists(os.path.dirname(self.LOCK_FILE)):
                os.makedirs(os.path.dirname(self.LOCK_FILE))
            self.log('LOG_INFO', "Attempting aquire mutext "
                                  "({0})...".format(self.LOCK_FILE))
            self.lock_fd = open(self.LOCK_FILE, 'w+')
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.log('LOG_INFO', "Lock written.")
        except IOError, exc_value:
            #  IOError: [Errno 11] Resource temporarily unavailable
            if exc_value[0] == 11:
                raise BuildError("DNS build script attemted to aquire the "
                        "build mutux but another process already has it.")
            else:
                raise

    def unlock(self):
        """
        Try to remove the lock file. Fail very loudly if the lock doesn't exist
        and this function is called.
        """
        self.log('LOG_INFO', "Attempting release mutex "
                              "({0})...".format(self.LOCK_FILE))
        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        self.log('LOG_INFO', "Unlock Complete.")

    def calc_target(self, root_domain, soa):
        """
        This function decides which directory a zone's zone files go. The
        following is used to decide on the target directory.

        If `root_domain` is a forward domain:

            * Replace all '.' characters with '/' characters.

        If `root_domain` is a reverse domain:

            If it's ipv4:

                'reverse/in-addr.arpa/'
            If it's ipv6:

                'reverse/in-addr.ipv6/'

        The build scripts will create this path on the filesystem if it does
        not exist.

        A relative path is returned by this function.
        """
        if root_domain.is_reverse:
            if root_domain.name.endswith('ipv6'):
                zone_path = "reverse/in-addr.arpa/"
            elif root_domain.name.endswith('arpa'):
                zone_path = "reverse/in-addr.arpa/"
            else:
                raise Exception("WTF type of reverse domain is this "
                        "{0}?!?".format(root_domain))
        else:
            tmp_path = '/'.join(reversed(root_domain.name.split('.')))
            zone_path = tmp_path + '/'
        return zone_path

    def write_stage_zone(self, stage_fname, root_domain, soa, fname, data):
        """
        Write a zone_file.
        Return the path to the file.
        """
        if not os.path.exists(os.path.dirname(stage_fname)):
            os.makedirs(os.path.dirname(stage_fname))
        self.log('LOG_INFO', "Stage zone file is {0}".format(stage_fname,
                soa=soa))
        with open(stage_fname, 'w+') as fd:
            fd.write(data)
        return stage_fname

    def shell_out(self, command, use_shlex=True):
        """A little helper function that will shell out and return stdout,
        stderr and the return code."""
        if use_shlex:
            command_args = shlex.split(command)
        else:
            command_args = command
        p = subprocess.Popen(command_args, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout, stderr, p.returncode

    def named_checkzone(self, zone_file, root_domain, soa):
        """Shell out and call named-checkzone on the zone file. If it returns
        with errors raise a BuildError.
        """
        # Make sure we have the write tools to do the job
        command_str = "which named-checkzone"
        stdout, stderr, returncode = self.shell_out(command_str)
        if returncode != 0:
            raise BuildError("Couldn't find named-checkzone.")

        # Check the zone file.
        command_str = "named-checkzone {0} {1} {2}".format(
                      self.NAMED_CHECKZONE_OPTS, root_domain.name,
                      zone_file)
        self.log('LOG_INFO', "Calling `named-checkzone {0} "
                             "{1}`".format(root_domain.name, zone_file))
        stdout, stderr, returncode = self.shell_out(command_str)
        if returncode != 0:
            raise BuildError("\nnamed-checkzone failed on zone {0}. "
                             "\ncommand: {1}:\nstdout: {2}\nstderr:{3}".
                             format(root_domain.name, command_str, stdout,
                             stderr))

    def named_checkconf(self, conf_file):
        command_str = "which named-checkconf"
        stdout, stderr, returncode = self.shell_out(command_str)
        if returncode != 0:
            raise BuildError("Couldn't find named-checkconf.")

        command_str = "named-checkconf {0}".format(conf_file)
        self.log('LOG_INFO', "Calling `named-checkconf {0}` ".
                                   format(conf_file))
        stdout, stderr, returncode = self.shell_out(command_str)
        if returncode != 0:
            raise BuildError("\nnamed-checkconf rejected config {0}. "
                             "\ncommand: {1}:\nstdout: {2}\nstderr:{3}".
                             format(conf_file, command_str, stdout,
                             stderr))

    def stage_to_prod(self, src):
        """Copy file over to PROD_DIR. Return the new location of the
        file.
        """

        if not src.startswith(self.STAGE_DIR):
            raise BuildError("Improper file '{0}' passed to "
                             "stage_to_prod".format(src))
        dst = src.replace(self.STAGE_DIR, self.PROD_DIR)
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        # copy2 will copy file metadata
        try:
            shutil.copy2(src, dst)
            self.log('LOG_INFO', "Copied {0} to {1}".format(src, dst))
        except (IOError, os.error) as why:
            raise BuildError("cp -p {0} {1} caused {2}".format(src,
                             dst, str(why)))
        except shutil.Error:
            raise
        return dst

    def write_stage_config(self, config_fname, stmts):
        """
        Write config files to the correct area in staging.
        Return the path to the file.
        """
        stage_config = os.path.join(self.STAGE_DIR, "config", config_fname)

        if not os.path.exists(os.path.dirname(stage_config)):
            os.makedirs(os.path.dirname(stage_config))
        with open(stage_config, 'w+') as fd:
            fd.write(stmts)
        return stage_config

    def build_zone(self, view, rel_fname, view_data, root_domain, soa):
        """
        This function will write the zone's zone file to the the staging area
        and call named-checkconf on the files before they are copied over to
        PROD_DIR. If will return a tuple of files corresponding to where the
        `privat_file` and `public_file` are written to. If a file is not
        written to the file system `None` will be returned instead of the path
        to the file.
        """
        self.log('LOG_INFO', "{0} for view '{1}' will be rebuilt.".format(soa,
                             view))

        stage_fname = os.path.join(self.STAGE_DIR, rel_fname)
        self.write_stage_zone(stage_fname, root_domain, soa, rel_fname,
                                             view_data)
        self.log('LOG_INFO', "Built stage_{0}_file to "
                             "{1}".format(view.name, stage_fname))
        self.named_checkzone(stage_fname, root_domain, soa)

        prod_fname = self.stage_to_prod(stage_fname)

        return prod_fname

    def calc_fname(self, view, root_domain):
        return "{0}.{1}".format(root_domain.name, view.name)

    def render_zone_stmt(self, zone_name, file_path):
        zone_stmt = "zone \"{0}\" IN {{{{\n".format(zone_name)
        zone_stmt += "\ttype {ztype};\n"  # We'll format this later
        zone_stmt += "\tfile \"{0}\";\n".format(file_path)
        zone_stmt += "}};\n"
        return zone_stmt

    def verify_prev_build(self, prod_fname, view_data, root_domain, soa):
        if not view_data:
            return
        serial = get_serial(os.path.join(prod_fname))
        if not serial.isdigit():
            if not soa.serial:
                soa.serial = int(time.time()) - 1
            soa.dirty = True
            # it's a new serial
            self.log('LOG_NOTICE', "{0} appears to be a new zone. Building"
                     " {1} with initial serial {2}".format(soa, prod_fname,
                     soa.serial + 1), soa=soa)
        elif int(serial) != soa.serial:
            # Looks like someone made some changes... let's nuke them.
            # We should probably email someone too.
            self.log('LOG_NOTICE', "{0} has serial {1} in svn ({2}) and "
                     "serial {3} in the database. SOA is being marked as "
                     "dirty.".format(soa, serial, prod_fname, soa.serial),
                     soa=soa)
            soa.dirty = True
            # Choose the highest serial so any slave nameservers don't get
            # confused.
            soa.serial = max(int(serial), soa.serial)

    def build_view(self, view, view_data, root_domain, soa):
        rel_zdir = self.calc_target(root_domain, soa)
        fname = self.calc_fname(view, root_domain)
        rel_fname = os.path.join(rel_zdir, fname)
        prod_fname = os.path.join(self.PROD_DIR, rel_fname)
        # If there is zomething different about the zone, like it's new or
        # it's serial doesn't match the one if the db, :func:`verify_prev`
        # will mark the soa as dirty.
        self.verify_prev_build(prod_fname, view_data, root_domain, soa)
        if soa.dirty:
            # Update the new zone strings with the correct serial number.
            self.log('LOG_INFO', "{0} is seen as dirty.".format(soa),
                                 soa=soa)
            self.log('LOG_INFO', "Prev serial was {0}. Using serial "
                                 "new serial {1}.".format(soa.serial,
                                  soa.serial + 1), soa=soa)
            self.build_zone(view, rel_fname,
                              view_data.format(serial=soa.serial + 1),
                              root_domain, soa)
        else:
            # private_data and public_data are not used because the soa
            # was not dirty and doesn't have any new changes in it,
            # instead the data already in prod_fname is checked again
            # using named_checkzone.  Later prod_fname is pointed to by
            # the view's config file in the form of a zone statement
            # (see render_zone_stmt).
            self.log('LOG_INFO', "{0} is seen as NOT dirty.".format(soa),
                     soa=soa)
            self.named_checkzone(prod_fname, root_domain, soa)

        return self.render_zone_stmt(root_domain.name, prod_fname)

    def build_zone_files(self):
        """
        This function builds and then writes zone files to the file system.
        This function also returns a list of zone statements.
        """
        # Keep track of which zones we build and what they look like.

        private_zone_stmts, public_zone_stmts = [], []

        for soa in SOA.objects.all():
            zinfo = soa.root_domain, soa

            # The *_data vars help us to decide whether we should build a zone.
            # If there are no records in the public/private view the
            # corresponding *_data var will be the emptry string. We will not
            # build and write a zone file for a view that does not have any
            # data.

            t_start = time.time()  # tic
            private_data, public_data = build_zone_data(*zinfo)
            build_time = time.time() - t_start  # toc
            self.log('LOG_INFO', 'Built {0} in {1} seconds '.format(soa,
                     build_time), soa=soa, build_time=build_time)

            private_view = View.objects.get_or_create(name='private')[0]
            public_view = View.objects.get_or_create(name='public')[0]
            if private_data:
                # The private view has data. let's build it.
                private_zone_stmts.append(self.build_view(private_view,
                                                         private_data, *zinfo))
            if public_data:
                public_zone_stmts.append(self.build_view(public_view,
                                                         public_data, *zinfo))
            if soa.dirty:
                soa.serial += 1
                soa.dirty = False
                soa.save()

        return private_zone_stmts, public_zone_stmts

    def build_view_config(self, view, ztype, stmts):
        config_fname = "{0}.{1}".format(ztype, view.name)
        zone_stmts = '\n'.join(stmts).format(ztype=ztype)
        stage_config = self.write_stage_config(config_fname, zone_stmts)
        self.named_checkconf(stage_config)
        return self.stage_to_prod(stage_config)

    def build_config_files(self, private_zone_stmts, public_zone_stmts):
        # named-checkconf on config files
        self.log('LOG_INFO', "Building config files.")
        private_view = View.objects.get_or_create(name='private')[0]
        public_view = View.objects.get_or_create(name='public')[0]
        # If we need slave configs, do it here
        private_config = self.build_view_config(private_view, 'master',
                                           private_zone_stmts)

        public_config = self.build_view_config(public_view, 'master',
                                           public_zone_stmts)
        return private_config, public_config

    def build_dns(self):
        self.log('LOG_NOTICE', 'Building...')
        self.lock()
        try:
            if self.CLOBBER_STAGE:
                self.clear_staging(force=True)
            self.build_staging()

            # zone files
            if self.BUILD_ZONES:
                self.build_config_files(*self.build_zone_files())
            else:
                self.log('LOG_INFO', "BUILD_ZONES is False. Not "
                         "building zone files.")

            if self.BUILD_ZONES and self.PUSH_TO_PROD:
                self.vcs_checkin()
            else:
                self.log('LOG_INFO', "PUSH_TO_PROD is False. Not checking "
                         "into {0}".format(self.vcs_type))

            if self.PRESERVE_STAGE:
                self.log('LOG_INFO', "PRESERVE_STAGE is True. Not "
                         "removing staging. You will need to use "
                         "--clobber-stage on the next run.")
            else:
                self.clear_staging()
        # All errors are handled by caller (this function)
        except BuildError, e:
            self.log('LOG_NOTICE', 'Error during build. Not removing staging')
            raise
        except Exception, e:
            print e
            self.log('LOG_NOTICE', 'Error during build. Not removing staging')
            raise
        finally:
            # Clean up
            self.unlock()
            pass
        self.log('LOG_NOTICE', 'Successful build is successful.')
