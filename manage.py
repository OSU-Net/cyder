#!/usr/bin/env python
import os
import site
import sys
from django.core.management import execute_manager

from lib.path_utils import path, import_mod_by_name, _dot_lookup, ROOT


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyder.settings')


# Adjust the python path and put local packages in front.
prev_sys_path = list(sys.path)

# Make root application importable without the need for
# python setup.py install|develop
sys.path.append(ROOT)

# Local (project) vendor library
site.addsitedir(path('vendor-local'))
site.addsitedir(path('vendor-local/lib/python'))

# Global (upstream) vendor library
site.addsitedir(path('vendor'))
site.addsitedir(path('vendor/lib/python'))

# Move the new items to the front of sys.path. (via virtualenv)
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

import cyder.signal_handlers # register the handlers


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
