import os
import argparse

import chili_manage

from cyder.core.ctnr.models import Ctnr


parser = argparse.ArgumentParser(
    description='Create ctnr portion of dhcp build')

parser.add_argument(
    '-f',
    '--file',
    default='',
    help='Path to where we want the cntr.conf file built')


def main():
    parsed = parser.parse_args()
    with open(os.path.join(parsed.file, 'ctnr.conf'), 'w') as f:
        for ctnr in Ctnr.objects.all():
            f.write(ctnr.build_legacy_class())
main()
