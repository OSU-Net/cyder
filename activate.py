import inspect
import os
import site
import sys
from os import path


def cy_path(x):
    return path.join(ROOT, x)


def activate():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyder.settings')

    filename = path.join(ROOT, '.env/bin/activate_this.py')
    try:
        execfile(filename, {'__file__': filename})
    except:
        pass


    import cyder.signal_handlers  # register the handlers


    site.addsitedir(cy_path('media/'))
    site.addsitedir(cy_path('media/css'))
    site.addsitedir(cy_path('vendor-local'))  # local (project) vendor library
    site.addsitedir(cy_path('vendor'))  # global (upstream) vendor library


ROOT = path.dirname(path.abspath(inspect.stack()[0][1]))
if ROOT not in sys.path:
    sys.path.append(ROOT)
