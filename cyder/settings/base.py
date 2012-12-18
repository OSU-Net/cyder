# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py
import os
import sys

from funfactory.settings_base import *
from cyder.settings.dns import *


ROOT_URLCONF = 'cyder.urls'
APPEND_SLASH = True
MEDIA_ROOT = path('media')
MEDIA_URL = '/media/'

_base = os.path.dirname(__file__)
site_root = os.path.realpath(os.path.join(_base, '../'))
sys.path.append(site_root)
sys.path.append(site_root + '/vendor')

SASS_PREPROCESS = True
JINGO_MINIFY_USE_STATIC = False

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'cyder_css': (
            'css/lib/jquery-ui-1.8.11.custom.css',
            'css/lib/jquery.autocomplete.css',
            'css/sticky_footer.css',

            'css/globals.scss',
            'css/base.scss',
            'css/forms.scss',
            'css/tables.scss',
        ),
    },
    'js': {
        'cyder_js': (
            'js/lib/jquery-1.8.3.min.js',
            'js/lib/attribute_adder.js',
            'js/lib/jquery.history.js',
            'js/lib/jQuery.rightclick.js',
            'js/lib/jquery.tools.min.js',
            'js/lib/jquery.validate.min.js',
            'js/lib/jquery.autocomplete.min.js',
            'js/lib/jquery-ui-1.8.11.custom.min.js',
            'js/lib/tablesorter.js',
            'js/lib/editablegrid/editablegrid.js',
            'js/lib/editablegrid/editablegrid_renderers.js',
            'js/lib/editablegrid/editablegrid_editors.js',
            'js/lib/editablegrid/editablegrid_validators.js',
            'js/lib/editablegrid/editablegrid_utils.js',
            'js/lib/editablegrid/editablegrid_charts.js',

            'js/utils.js',
            'js/application.js',
            'js/dhcp_raw_include.js',
            'js/key_value_validators.js',
        ),
        'tables': (
            'js/tables.js',
        ),
        'cydns': (
            'js/cydns/cydns_record_form.js',
            'js/cydns/cydns_record_form_utils.js',
        ),
        'ctnr': (
            'js/ctnr/ctnr.js',
        )
    }
}

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'base',
    'core',
    'core.ctnr',
    'core.cyuser',
    'core.search',
    'core.system',
    'cydhcp',
    'cydhcp.site',
    'cydhcp.vlan',
    'cydhcp.network',
    'cydhcp.range',
    'cydhcp.build',
    'cydhcp.lib',
    'cydhcp.interface',
    'cydhcp.interface.static_intr',
    'cydhcp.bulk_change',
    'cydns',
    'dnsutils',
    'dnsutils.migrate',
    'cydns',
    'cydns.address_record',
    'cydns.cname',
    'cydns.domain',
    'cydns.ip',
    'cydns.mx',
    'cydns.nameserver',
    'cydns.ptr',
    'cydns.soa',
    'cydns.sshfp',
    'cydns.srv',
    'cydns.txt',
    'cydns.view',
    'cydns.cybind',

    # Third party apps
    'djcelery',
    'django_extensions',
    'django_nose',
    'jingo_minify',
    'tastypie',
    'tastytools',

    # Django contrib apps
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cyder.middleware.dev_authentication.DevAuthenticationMiddleware',
)

SESSION_COOKIE_NAME = 'cyder'
SESSION_COOKIE_SECURE = False


AUTH_PROFILE_MODULE = 'cyuser.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'debug_toolbar',
    'tastytools',
]

DJANGO_TEMPLATE_APPS = ['admin']

LOGGING = dict(loggers=dict(playdoh={'level': logging.INFO}))

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

BUILD_PATH = 'builds'
INTERNAL_IPS = ('127.0.0.1', '10.22.74.139', '10.250.2.54')
