#!/usr/bin/python
import argparse
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                os.pardir, os.pardir, os.pardir, os.pardir)))

import manage

manage
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.base'

from cyder.cydns.cybind.builder import DNSBuilder, BuildError
#from core.utils import fail_mail  # TODO, write this function


def main():
    parser = argparse.ArgumentParser(description='DNS Build scripts')
    parser.add_argument('--stage-only', dest='STAGE_ONLY', action='store_true',
                        default=False, help="Just build staging and don't "
                        "copy to prod. named-checkzone will still be run.")
    parser.add_argument('--clobber-stage', dest='CLOBBER_STAGE',
                        action='store_true', default=False, help="If stage "
                        "already exists delete it before running the build "
                        "script.")
    parser.add_argument('--ship-it', dest='PUSH_TO_PROD',
                        action='store_true', default=False, help="Check files "
                        "into rcs and push upstream.")
    parser.add_argument('--preserve-stage', dest='PRESERVE_STAGE',
                        action='store_true', default=False, help="Do not "
                        "remove staging area after build completes.")
    parser.add_argument('--no-build', dest='BUILD_ZONES',
                        action='store_false', default=True, help="Do not "
                        "build zone files.")
    parser.add_argument('--no-syslog', dest='LOG_SYSLOG',
                        action='store_false', default=True, help="Do not "
                        "log to syslog.")
    parser.add_argument('--debug', dest='DEBUG',
                        action='store_true', default=False, help="Print "
                        "copious amounts of text.")
    parser.add_argument('--first-run', dest='FIRST_RUN',
                        action='store_true', default=False, help="Ignore "
                        "all change delta thresholds.")
    nas = parser.parse_args(sys.argv[1:])
    b = DNSBuilder(**dict(nas._get_kwargs()))
    try:
        b.build_dns()
    except BuildError as why:
        b.log('LOG_ERR', why)
        #fail_mail(message.format(why))
    except Exception as err:
        # Make some noise
        #fail_mail(message.format(err))
        b.log('LOG_CRIT', err)
        raise

if __name__ == '__main__':
    main()
