import os
import chili_manage

from cyder.core.ctnr.models import Ctnr


def main():
    with open(os.path.join(os.path.dirname(__file__), 'ctnr.conf'), 'w') as f:
        for ctnr in Ctnr.objects.all():
            f.write(ctnr.build_legacy_class())
main()
