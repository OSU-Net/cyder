from cyder.cydns.cybind.builder import DNSBuilder, BuildError
from django.core.management.base import BaseCommand, CommandError

from core.utils import fail_mail
from optparse import make_option


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
                    help="Rebuild zones even if they're up to date."),
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

        with DNSBuilder(**builder_opts) as b:
            if options['build']:
                b.build(clean_up=options['push'], force=options['force_build'])
            if options['push']:
                b.push(sanity_check=options['sanity_check'])

        #try:
            #b.build_dns()
        #except BuildError as err:
            #msg = "FATAL: {0}".format(err)
            #print msg
            #b.log(msg, log_level='LOG_ERR')
            #fail_mail(err)
            #raise err
        #except Exception as err:
            #msg = "Exception: {0}".format(err)
            #print msg
            #b.log(msg, log_level='LOG_CRIT')
            #fail_mail(err)
            #raise err
