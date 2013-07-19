import os
import argparse

import chili_manage

from cyder.cydhcp.vrf.models import Vrf


parser = argparse.ArgumentParser(
    description='Create VRF portion of dhcp build')

parser.add_argument(
    '-f',
    '--file',
    default='',
    help='Path to where we want the vrf.conf file built')


def main():
    parsed = parser.parse_args()
    with open(os.path.join(parsed.file, 'vrf.conf'), 'w') as f:
        for vrf in Vrf.objects.all():
            f.write(vrf.build_vrf())
main()
