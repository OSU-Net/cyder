import os
import argparse
import chili_manage

from cyder.cydhcp.network.models import Network

parser = argparse.ArgumentParser(
    description='Create subnet portion of dhcp build')

parser.add_argument(
    '-f',
    '--file',
    default='',
    help='Path to where we want the subnet.conf file built')


def main():
    parsed = parser.parse_args()
    path = os.path.join(os.path.join(parsed.file, 'subnet.conf'))
    with open(path, 'w') as f:
        for network in Network.objects.all():
            f.write(network.build_subnet())
main()
