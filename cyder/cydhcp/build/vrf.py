import os
import chili_manage

from cyder.cydhcp.vrf.models import Vrf


def main():
    with open(os.path.join(os.path.dirname(__file__), 'vrf.conf'), 'w') as f:
        for vrf in Vrf.objects.all():
            f.write(vrf.build_vrf())
main()
