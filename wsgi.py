import inspect
import os
import site
from os import path


ROOT = path.dirname(path.abspath(inspect.stack()[0][1]))
if ROOT not in sys.path:
    sys.path.append(ROOT)

os.environ['CELERY_LOADER'] = 'django'


import activate
import django.core.handlers.wsgi


application = django.core.handlers.wsgi.WSGIHandler()
