from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from cyder.core.utils import fail_mail
from cyder.cydns.cybind.builder import DNSBuilder


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        ### action options ###
        make_option('-b', '--build',
                    dest='build',
                    action='store_true',
                    default=False,
                    help="Build zone files."),
        make_option('-p', '--push',
                    dest='push',
                    action='store_true',
                    default=False,
                    help="Check files into vcs and push upstream."),
        ### logging/debug options ###
        make_option('-l', '--log-syslog',
                    dest='log_syslog',
                    action='store_true',
                    help="Log to syslog."),
        make_option('-L', '--no-log-syslog',
                    dest='log_syslog',
                    action='store_false',
                    help="Do not log to syslog."),
        make_option('--debug',
                    dest='debug',
                    action='store_true',
                    default=False,
                    help="Print copious amounts of text."),
        ### miscellaneous ###
        make_option('-f', '--force-build',
                    dest='force_build',
                    action='store_true',
                    default=False,
                    help="Rebuild all zones even if they're up to date."),
        make_option('-C', '--no-sanity-check',
                    dest='sanity_check',
                    action='store_false',
                    default=True,
                    help="Don't run the diff sanity check."),
    )

    def handle(self, *args, **options):
        builder_opts = {}
        for name in ('log_syslog', 'debug'):
            val = options.pop(name)
            if val is not None:
                builder_opts[name] = val
            # else use settings

        with DNSBuilder(**builder_opts) as b:
            if options['build']:
                b.build(clean_up=options['push'], force=options['force_build'])
            if options['push']:
                if options['build']:
                    b.push(sanity_check=options['sanity_check'])
                else:
                    raise CommandError('--push requires --build')
