import os
import chili_manage

from cyder.cydhcp.network.models import Network


def main():
    path = os.path(os.path.dirname(__file__))
    with open(path, 'subnet.conf', 'w') as f:
        for network in Network.objects.all():
            f.write(network.build_subnet())
main()
