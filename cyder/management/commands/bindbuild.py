from cyder.cydns.cybind.builder import DNSBuilder, BuildError
from django.core.management.base import BaseCommand, CommandError

from core.utils import fail_mail
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--stage-only',
                    dest='stage_only',
                    action='store_true',
                    default=False,
                    help="Just build staging and don't copy to prod. name"
                         "d-checkzone will still be run."),
        make_option('--clobber-stage',
                    dest='clobber_stage',
                    action='store_true',
                    default=False,
                    help="If stage already exists delete it before runnin"
                         "g the build script."),
        make_option('--ship-it',
                    dest='push_to_prod',
                    action='store_true',
                    default=False,
                    help="Check files into vcs and push upstream."),
        make_option('--preserve-stage',
                    dest='preserve_stage',
                    action='store_true',
                    default=False,
                    help="Do not remove staging area after build"
                         " completes."),
        make_option('--no-build',
                    dest='build_zones',
                    action='store_false',
                    default=True,
                    help="Do not build zone files."),
        make_option('--no-syslog',
                    dest='log_syslog',
                    action='store_false',
                    default=True, help="Do not log to syslog."),
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
