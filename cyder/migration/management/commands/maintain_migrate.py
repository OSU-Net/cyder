from django.core.management.base import BaseCommand
from django.conf import settings

from cyder.cydns.cybind.builder import DNSBuilder, BuildError

import subprocess
import dns_migrate
#import dhcp_migrate
from lib.diffdns import diff_zones
from lib.checkexcept import checkexcept


def build_dns():
    args = {'FIRST_RUN': False,
            'PRESERVE_STAGE': False,
            'PUSH_TO_PROD': False,
            'BUILD_ZONES': True,
            'LOG_SYSLOG': True,
            'CLOBBER_STAGE': True,
            'STAGE_ONLY': False,
            'DEBUG': False
            }
    b = DNSBuilder(**args)

    try:
        b
    except BuildError as why:
        b.log('LOG_ERR', why)
    except Exception as err:
        b.log('LOG_CRIT', err)
        raise


class Command(BaseCommand):

    def handle(self, **options):
        print "Migrating DNS objects."
        dns_migrate.do_everything(skip_edu=True)

        print "Building zone files."
        build_dns()
        p = subprocess.Popen(["rndc", "reload"], stdout=subprocess.PIPE)
        if "successful" in p.stdout.read():
            print "rndc reloaded successfully"
        else:
            print "Failed to reload rndc. Do you have permission?"
            exit(1)
        p.stdout.close()

        print "Comparing localhost to %s." % settings.VERIFICATION_SERVER
        diffs = diff_zones("localhost", settings.VERIFICATION_SERVER,
                           settings.ZONES_FILE, skip_edu=True)

        print "Removing excusable differences."
        checked, unexcused = checkexcept(diffs)

        print "%s differences. %s not excused." % (checked, len(unexcused))
        print
        for rdtype, name, A, B in unexcused:
            print rdtype, name
            print "localhost", A
            print settings.VERIFICATION_SERVER, B
            print

        #dhcp_migrate.migrate_all()
