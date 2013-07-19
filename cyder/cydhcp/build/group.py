import os
import argparse

import chili_manage

from cyder.cydhcp.workgroup.models import Workgroup


parser = argparse.ArgumentParser(
    description='Create workgroup portion of dhcp build')

parser.add_argument(
    '-f',
    '--file',
    default='',
    help=("Path to where we want the group.conf file built.  This "
          "defaults to the current working directory"))


def main():
    parsed = parser.parse_args()
    with open(os.path.join(parsed.file, 'group.conf'), 'w') as f:
        for workgroup in Workgroup.objects.all():
            f.write(workgroup.build_workgroup())

if __name__ == '__main__':
    main()
