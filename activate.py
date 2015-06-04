from glob import glob
import inspect
import os
import subprocess
import sys
from os import path


def cy_path(x):
    return path.join(ROOT, x)


def cy_addsitedir(x):
    """Do essentially what site.addsitedir does, except prepend the paths

    Note: Import lines aren't supported, because they're not useful to us.

    """

    if not path.exists(x):
        return

    for pth_name in glob(path.join(x, '*.pth')):
        ps = []
        with open(pth_name) as pth:
            for line in pth:
                line = line.strip()
                if line[0] == '#':
                    continue
                p = path.join(x, line)
                if path.exists(p) and p not in sys.path:
                    ps.append(p)
        sys.path[1:1] = ps

    if x not in sys.path:
        sys.path.insert(1, x)


def activate():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyder.settings')

    filename = path.join(ROOT, '.env/bin/activate_this.py')
    try:
        execfile(filename, {'__file__': filename})
    except:
        pass

    cy_addsitedir(cy_path('vendor'))  # global (upstream) vendor library
    cy_addsitedir(cy_path('vendor-local'))  # local (project) vendor library

    from lib.monkeypatches import patch

    patch()

    import cyder.signal_handlers  # register the handlers


ROOT = path.dirname(path.abspath(inspect.stack()[0][1]))
if ROOT not in sys.path:
    sys.path.append(ROOT)

CYDER_REVISION = subprocess.check_output(
    ['git', '--git-dir=' + cy_path('.git'), 'rev-parse', 'HEAD']).rstrip()
