import os
import chili_manage

from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.workgroup.models import Workgroup


def main():
    with open(os.path.join(os.path.dirname(__file__), 'group.conf'), 'w') as f:
        for workgroup in Workgroup.objects.all():
            f.write(workgroup.build_workgroup())
main()
