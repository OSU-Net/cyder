import syslog
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from cyder.cydhcp.build.builder import DHCPBuilder


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        ### action options ###
        make_option('-p', '--push',
                    dest='push',
                    action='store_true',
                    default=False,
                    help="Check files into vcs and push upstream."),
        ### logging/debug options ###
        make_option('-l', '--syslog',
                    dest='to_syslog',
                    action='store_true',
                    help="Log to syslog."),
        make_option('-L', '--no-syslog',
                    dest='to_syslog',
                    action='store_false',
                    help="Do not log to syslog."),
        ### miscellaneous ###
        make_option('-C', '--no-sanity-check',
                    dest='sanity_check',
                    action='store_false',
                    default=True,
                    help="Don't run the diff sanity check."),
    )

    def handle(self, *args, **options):
        builder_opts = {}

        if options['to_syslog']:
            syslog.openlog('dhcp_build', facility=syslog.LOG_LOCAL6)
            builder_opts['to_syslog'] = True

        verbosity = int(options['verbosity'])
        builder_opts['quiet'] = verbosity == 0
        builder_opts['verbose'] = verbosity >= 2

        with DHCPBuilder(**builder_opts) as b:
            b.build()
            if options['push']:
                b.push(sanity_check=options['sanity_check'])
