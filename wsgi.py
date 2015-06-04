import inspect
import os
import site
from os import path


ROOT = path.dirname(path.abspath(inspect.stack()[0][1]))
if ROOT not in sys.path:
    sys.path.append(ROOT)
import activate
activate.activate()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
