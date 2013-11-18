import os
import re
import syslog

from cyder.base.utils import set_attrs, dict_merge, log, run_command


class VCSRepo(object):
    def __init__(self, repo_dir, diff_line_threshold, logger=syslog,
                 debug=False, log_syslog=False):
        set_attrs(self, {
            'repo_dir': repo_dir,
            'diff_line_threshold': diff_line_threshold,
            'logger': logger,
            'debug': debug,
            'log_syslog': log_syslog,
        })

    def commit_and_push(self, message):
        old_dir = os.getcwd()
        os.chdir(self.repo_dir)

        try:
            self._commit_and_push(message)
        finally:
            os.chdir(old_dir)

    def _log(self, message, log_level='LOG_INFO'):
        log(message, log_level=log_level, to_stderr=self.debug,
                to_syslog=self.log_syslog)

    def _sanity_check(self):
        lines_changed = self._lines_changed()
        if sum(lines_changed) > self.diff_line_threshold:
            raise Exception('Too many lines changed. Aborting commit.\n'
                            '({0} lines added, {1} lines removed)'
                            .format(*lines_changed))

    def _run_command(self, command, log=True, failure_msg=None):
        if log:
            command_logger = self._log
            failure_logger = lambda msg: self._log(msg, log_level='LOG_ERR')
        else:
            command_logger, failure_logger = None, None

        return run_command(command, command_logger=command_logger,
                           failure_logger=failure_logger,
                           failure_msg=failure_msg)


class SVNRepo(VCSRepo):
    def _commit_and_push(self, message, force=False):
        self._add()
        if force:
            log('Skipping sanity check.')
        else:
            self._sanity_check(diff_line_threshold)
        self._checkin(message)
        self._update()

    def _add(self):
        self._run_command('svn add --force .')

    def _checkin(self, message):
        self._run_command('svn ci -m "{0}"'.format(message))

    def _update(self):
        self._run_command('svn up')

    def _lines_changed(self):
        diff_ignore = (re.compile(r'---\s.+\s+\(revision\s\d+\)'),
                       re.compile(r'\+\+\+.*'))

        output, _ = self._run_command('svn diff --depth=infinity')

        added, removed = 0, 0
        for line in output.split('\n'):
            if any(regex.match(line) for regex in diff_ignore):
                continue
            if line.startswith('+'):
                added += 1
            elif line.startswith('-'):
                removed += 1

        return added, removed


class GitRepo(VCSRepo):
    def _commit_and_push(self, message, force=False):
        self._pull()
        self._add_all()
        if force:
            log('Skipping sanity check because force=True was passed.')
        else:
            self._sanity_check()
        self._commit(message)
        self._push()

    def _pull(self):
        self._run_command('git pull --ff-only')

    def _add_all(self):
        self._run_command('git add -A .')

    def _lines_changed(self):
        diff_ignore = (re.compile(r'--- \S'),
                       re.compile(r'\+\+\+ \S'))

        output, _ = self._run_command('git diff --cached', log=False)

        added, removed = 0, 0
        for line in output.split('\n'):
            if any(regex.match(line) for regex in diff_ignore):
                continue
            if line.startswith('+'):
                added += 1
            elif line.startswith('-'):
                removed += 1

        return added, removed

    def _commit(self, message):
        self._run_command('git commit -m "{0}"'.format(message))

    def _push(self):
        self._run_command('git push')
