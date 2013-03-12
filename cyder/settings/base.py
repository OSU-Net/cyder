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

EMAIL_SUFFIX = '@onid.oregonstate.edu'
CAS_SERVER_URL = 'https://login.oregonstate.edu/cas/login'
CAS_AUTO_CREATE_USERS = True  # Not to be used in production.

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
        'search': ('css/search.scss',)
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
            'js/views.js',
        ),
        'tables': (
            'js/tables.js',
        ),
        'ctnr': (
            'js/ctnr/ctnr.js',
        )
    }
}

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'base',
    'search',
    'core',
    'core.ctnr',
    'core.cyuser',
    'core.system',
    'cydhcp',
    'cydhcp.site',
    'cydhcp.vlan',
    'cydhcp.network',
    'cydhcp.range',
    'cydhcp.build',
    'cydhcp.lib',
    'cydhcp.interface',
    'cydhcp.interface.dynamic_intr',
    'cydhcp.interface.static_intr',
    'cydhcp.vrf',
    'cydhcp.workgroup',
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
    'migration',

    # Third party apps
    'south',
    'django_cas',
    'djcelery',
    'django_extensions',
    'django_nose',
    'jingo_minify',
    'tastypie',
    'tastytools',
    # 'reversion',

    # Django contrib apps
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.messages',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
    'cyder.middleware.authentication.AuthenticationMiddleware',
    # 'reversion.middleware.RevisionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages'
)

SESSION_COOKIE_NAME = 'cyder'
SESSION_COOKIE_SECURE = False

AUTH_PROFILE_MODULE = 'cyuser.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
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

# Use sha 256 by default but support any other algorithm:
BASE_PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)
from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

# Migration settings
POINTERS = [('128.193.76.253', 'cob-dc81.bus.oregonstate.edu', 'forward'),
            ('128.193.76.254', 'cob-dc82.bus.oregonstate.edu', 'forward')]
REVERSE_DOMAINS = ['50.209.59.69', '193.128', '10', '211.140', '201.199', '32.198', '232.111',
                   '127', '131.80.252.131', '5.68.98.207']

VERIFICATION_SERVER = "ns1.oregonstate.edu"
ZONES_FILE = "/tmp/dns_prod/cyzones/config/master.public"
ZONE_PATH = "cyder/migration/management/commands/lib/zones"
ZONE_BLACKLIST = []
