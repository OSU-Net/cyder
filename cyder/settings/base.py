# This is Cyder's main settings file. If you need to override a setting
# locally, use cyder/settings/local.py

import os
import sys

from funfactory.settings_base import *
from cyder.settings.dns import *

TESTING = True if sys.argv[1:] and sys.argv[1] == 'test' else False

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
BUG_REPORT_EMAIL = 'CyderProject@oregonstate.edu'
EMAIL_HOST = 'mail.oregonstate.edu'

SASS_PREPROCESS = True
JINGO_MINIFY_USE_STATIC = False

SOUTH_TESTS_MIGRATE = False

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
            'js/views.js',
            'js/rangewizard.js',
        ),
        'rangeform': (
            'js/rangeform.js',
        ),
        'tables': (
            'js/tables.js',
        ),
        'admin': (
            'js/admin.js',
        ),
        'ctnr': (
            'js/ctnr/ctnr.js',
        ),
        'interface_delete': (
            'js/interface_delete.js',
        ),
        'systemform': (
            'js/systemform.js',
        ),
    }
}

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'api.authtoken',
    'base',
    'search',
    'core',
    'core.ctnr',
    'core.cyuser',
    'core.system',
    'core.task',
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
    'rest_framework',

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
    #'django_cas.middleware.CASMiddleware',
    'cyder.middleware.dev_authentication.DevAuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages'
)

FIXTURES = [
    'cyder/core/ctnr/fixtures/base',
    'cyder/core/cyuser/fixtures/test_users',
]

SESSION_COOKIE_NAME = 'cyder'
SESSION_COOKIE_SECURE = False

AUTH_PROFILE_MODULE = 'cyuser.UserProfile'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'django_cas.backends.CASBackend',
)

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'debug_toolbar',
    'rest_framework',
    'cyder.api.authtoken',
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
            ('128.193.76.254', 'cob-dc82.bus.oregonstate.edu', 'forward'),
            ('128.193.76.252', 'cob-dc83.bus.oregonstate.edu', 'forward'),
            ('128.193.76.255', 'cob-dc84.bus.oregonstate.edu', 'forward')]

REVERSE_DOMAINS = [
    '50.209.59.69', '193.128', '10', '211.140', '201.199', '32.198', '232.111',
    '127', '131.80.252.131', '5.68.98.207'
]

VERIFICATION_SERVER = "ns1.oregonstate.edu"
ZONES_FILE = "/tmp/dns_prod/cyzones/config/master.public"
ZONE_PATH = "cyder/migration/management/commands/lib/zones"
ZONE_BLACKLIST = []

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'cyder.api.v1.permissions.ReadOnlyIfAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'cyder.api.v1.authentication.CyderTokenAuthentication',
    ),
    'PAGINATE_BY': 25,
    'PAGINATE_BY_PARAM': 'count',
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_FILTER_BACKENDS': (
        'cyder.api.v1.filter.SearchFieldFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}


# bindbuild settings
# ==================


# DNS_STAGE_DIR: Where test builds should go. This shouldn't be in an SVN repo.
DNS_STAGE_DIR = "/tmp/dns_stage/"

# DNS_PROD_DIR: This is the directory where Cyder will place its DNS files.
# This should be an SVN repo
DNS_PROD_DIR = "/tmp/dns_prod/cyzones/"

# DNS_BIND_PREFIX: This is the path to where Cyder zone files are built
# relative to the root of the SVN repo. This is usually a substring of
# PROD_DIR.
DNS_BIND_PREFIX = DNS_PROD_DIR


DNS_LOCK_FILE = "/tmp/lock.file"
DNS_NAMED_CHECKZONE_OPTS = ""
DNS_MAX_ALLOWED_LINES_CHANGED = 500
DNS_NAMED_CHECKZONE = "/usr/sbin/named-checkzone"  # path to named-checkzone
DNS_NAMED_CHECKCONF = "/usr/sbin/named-checkconf"  # path to named-checkconf

# Only one zone at a time should be removed
DNS_MAX_ALLOWED_CONFIG_LINES_REMOVED = 10

DNS_STOP_UPDATE_FILE = "/tmp/stop.update"
DNS_LAST_RUN_FILE = "/tmp/last.run"


# dhcp_build settings
# ===================


# DHCP_STAGE_DIR: Where test builds should go. This shouldn't be in an SVN
# repo.
DHCP_STAGE_DIR = '/tmp/dhcp/stage'

# DHCP_PROD_DIR: Where Cyder will place the dhcpd configuration file.
DHCP_PROD_DIR = '/tmp/dhcp/prod'

# DHCP_TARGET_FILE: The configuration file that will be generated
DHCP_TARGET_FILE = 'dhcpd.conf.data'

# DHCP_CHECK_FILE: The conf file whose syntax will be checked (None means
# don't check any file)
DHCP_CHECK_FILE = None

DHCP_REPO_DIR = DHCP_STAGE_DIR

DHCP_VERBOSE_ERROR_LOG = True
DHCP_VERBOSE_ERROR_LOG_LOCATION = '/tmp/error.log'
