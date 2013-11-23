from cyder.cydns.cybind.builder import DNSBuilder, BuildError
from django.core.management.base import BaseCommand, CommandError

from core.utils import fail_mail
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
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
        make_option('--log-syslog',
                    dest='log_syslog',
                    action='store_true',
                    help="Log to syslog."),
        make_option('--no-log-syslog',
                    dest='log_syslog',
                    action='store_false',
                    help="Do not log to syslog."),
        make_option('--debug',
                    dest='debug',
                    action='store_true',
                    default=False,
                    help="Print copious amounts of text."),
        make_option('-f', '--force',
                    dest='force',
                    action='store_true',
                    default=False,
                    help="Ignore all change delta thresholds."),
    )

    def handle(self, *args, **options):
        options

        builder_opts = {}
        for name in ('log_syslog', 'debug', 'force'):
            val = options.pop(name)
            if val is not None:
                builder_opts[name] = val

        b = DNSBuilder(**builder_opts)

        if options['build']:
            b.build(clean_up=options['push'])

        if options['push']:
            b.push()

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
