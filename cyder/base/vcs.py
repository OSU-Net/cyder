import os
import re
import syslog
from os.path import dirname, basename

from cyder.base.utils import set_attrs, dict_merge, log, run_command


class ChdirHandler(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.path)
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_dir)


def repo_chdir_wrapper(func):
    """A decorator that handles changing to and from repo_dir"""
    def wrapped(self, *args, **kwargs):
        with ChdirHandler(self.repo_dir):
            return func(self, *args, **kwargs)

    wrapped.__name__ = func.__name__

    return wrapped


class VCSRepo(object):
    def __init__(self, repo_dir, line_change_limit=None,
                 line_removal_limit=None, debug=False, log_syslog=False,
                 logger=syslog):
        set_attrs(self, {
            'repo_dir': repo_dir,
            'line_change_limit': line_change_limit,
            'line_removal_limit': line_removal_limit,
            'debug': debug,
            'log_syslog': log_syslog,
            'logger': logger,
        })

    @repo_chdir_wrapper
    def reset_to_head(self):
        self._reset_to_head()

    @repo_chdir_wrapper
    def reset_and_pull(self):
        """Make the working tree match what's currently upstream."""

        self._reset_to_head()
        self._pull()

    @repo_chdir_wrapper
    def commit_and_push(self, message, sanity_check=True):
        self._commit_and_push(message, sanity_check=sanity_check)

    @repo_chdir_wrapper
    def get_revision(self):
        return self._get_revision()

    def _log(self, message, log_level='LOG_DEBUG'):
        log(message, log_level=log_level, to_stderr=self.debug,
                to_syslog=self.log_syslog, logger=self.logger)

    def _sanity_check(self):
        added, removed = self._lines_changed()
        if (self.line_change_limit is not None and
                added + removed > self.line_change_limit):
            raise Exception('Lines changed ({0}) exceeded limit ({1}).\n'
                            'Aborting commit.\n'
                            .format(added + removed,
                                    self.line_change_limit))

        if (self.line_removal_limit is not None and
                removed > self.line_removal_limit):
            raise Exception('Lines removed ({0}) exceeded limit ({1}).\n'
                            'Aborting commit.\n'
                            .format(removed, self.line_removal_limit))


    def _run_command(self, command, log=True, failure_msg=None,
                     ignore_failure=False):
        if log:
            command_logger = self._log
            failure_logger = lambda msg: self._log(msg, log_level='LOG_ERR')
        else:
            command_logger, failure_logger = None, None

        return run_command(
            command, command_logger=command_logger,
            failure_logger=failure_logger, failure_msg=failure_msg,
            ignore_failure=ignore_failure)


class GitRepo(VCSRepo):
    @repo_chdir_wrapper
    def commit_and_push(self, message, sanity_check=True,
                        empty=False):
        self._commit_and_push(message, sanity_check=sanity_check,
                              empty=empty)

    @classmethod
    def clone(cls, source, dest):
        run_command('git clone {0} {1}'.format(source, dest))

    @repo_chdir_wrapper
    def init(self, bare=False):
        cmd = 'git init' + (' --bare' if bare else '')
        self._run_command(cmd)

    def _get_revision(self):
        revision, _, _ = self._run_command('git rev-parse HEAD')
        return revision.strip()

    def _is_index_dirty(self):
        _, _, returncode = self._run_command('git diff --cached --quiet',
                                             ignore_failure=True)
        return returncode != 0

    def _commit_and_push(self, message, sanity_check=True, empty=False):
        if not empty:
            self._add_all()

        if not self._is_index_dirty() and not empty:
            self._log('There were no changes. Nothing to commit.',
                      log_level='LOG_INFO')
            return

        if sanity_check:
            self._sanity_check()
        else:
            self._log('Skipping sanity check because sanity_check=False was '
                      'passed.')

        self._commit(message, allow_empty=empty)
        self._push()

    def _reset_to_head(self):
        self._run_command('git reset --hard')
        self._run_command('git clean -dxf')

    def _remove_all(self):
        self._run_command('git rm -rf .', ignore_failure=True)

    def _pull(self):
        self._run_command('git pull --ff-only')

    def _add_all(self):
        self._run_command('git add -A .')

    def _lines_changed(self):
        diff_ignore = (re.compile(r'--- \S'),
                       re.compile(r'\+\+\+ \S'))

        output, _, _ = self._run_command('git diff --cached', log=False)

        added, removed = 0, 0
        for line in output.split('\n'):
            if any(regex.match(line) for regex in diff_ignore):
                continue
            if line.startswith('+'):
                added += 1
            elif line.startswith('-'):
                removed += 1

        return added, removed

    def _commit(self, message, allow_empty=False):
        cmd = ('git commit ' + ('--allow-empty ' if allow_empty else '') +
               '-m "{0}"'.format(message))
        self._run_command(cmd)

    def _push(self):
        self._run_command('git push')
