import os
import site

os.environ['CELERY_LOADER'] = 'django'
os.environ["DJANGO_SETTINGS_MODULE"] = "cyder.settings"

# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)

site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../')))
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../media/')))
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../media/css')))
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../chili_env/lib/python2.6/site-packages')))

# manage adds /apps, /lib, and /vendor to the Python path.
import manage

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python
