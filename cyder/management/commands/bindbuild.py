from cyder.cydns.cybind.builder import DNSBuilder, BuildError
from django.core.management.base import BaseCommand, CommandError

from core.utils import fail_mail
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--stage-only',
                    dest='STAGE_ONLY',
                    action='store_true',
                    default=False,
                    help="Just build staging and don't copy to prod. name"
                         "d-checkzone will still be run."),
        make_option('--clobber-stage',
                    dest='CLOBBER_STAGE',
                    action='store_true',
                    default=False,
                    help="If stage already exists delete it before runnin"
                         "g the build script."),
        make_option('--ship-it',
                    dest='PUSH_TO_PROD',
                    action='store_true',
                    default=False,
                    help="Check files into vcs and push upstream."),
        make_option('--preserve-stage',
                    dest='PRESERVE_STAGE',
                    action='store_true',
                    default=False,
                    help="Do not remove staging area after build"
                         " completes."),
        make_option('--no-build',
                    dest='BUILD_ZONES',
                    action='store_false',
                    default=True,
                    help="Do not build zone files."),
        make_option('--no-syslog',
                    dest='LOG_SYSLOG',
                    action='store_false',
                    default=True, help="Do not log to syslog."),
        make_option('--debug',
                    dest='DEBUG',
                    action='store_true',
                    default=False,
                    help="Print copious amounts of text."),
        make_option('-f', '--force',
                    dest='FORCE',
                    action='store_true',
                    default=False,
                    help="Ignore all change delta thresholds."),
    )

    def handle(self, *args, **options):
        b = DNSBuilder(**dict(options))
        try:
            b.build_dns()
        except BuildError as err:
            msg = "FATAL: {0}".format(err)
            print msg
            b.log(msg, log_level='LOG_ERR')
            fail_mail(err)
            raise err
        except Exception as err:
            msg = "Exception: {0}".format(err)
            print msg
            b.log(msg.format(err), log_level='LOG_CRIT')
            fail_mail(err)
            raise err
