# This is Cyder's main settings file. If you need to override a setting
# locally, use cyder/settings/local.py

import glob
import itertools
import logging
import os
import socket
import sys
from django.utils.functional import lazy

from lib.path_utils import ROOT, path

##########################
# copied from funfactory #
##########################

SLAVE_DATABASES = []

DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

## Logging
LOG_LEVEL = logging.INFO
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_playdoh"  # Change this after you fork.
LOGGING_CONFIG = None
LOGGING = {}

# CEF Logging
CEF_PRODUCT = 'Playdoh'
CEF_VENDOR = 'Mozilla'
CEF_VERSION = '0'
CEF_DEVICE_VERSION = '0'

## Accepted locales

# Tells the product_details module where to find our local JSON files.
# This ultimately controls how LANGUAGES are constructed.
PROD_DETAILS_DIR = path('lib/product_details_json')

# On dev instances, the list of accepted locales defaults to the contents of
# the `locale` directory within a project module or, for older Playdoh apps,
# the root locale directory.  A localizer can add their locale in the l10n
# repository (copy of which is checked out into `locale`) in order to start
# testing the localization on the dev server.
try:
    DEV_LANGUAGES = [
        os.path.basename(loc).replace('_', '-')
        for loc in itertools.chain(glob.iglob(ROOT + '/locale/*'),  # old style
                                   glob.iglob(ROOT + '/*/locale/*'))
        if (os.path.isdir(loc) and os.path.basename(loc) != 'templates')
    ]
except OSError:
    DEV_LANGUAGES = ('en-US',)


def lazy_lang_url_map():
    from django.conf import settings
    langs = settings.DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()


# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs if lang in product_details.languages])

LANGUAGES = lazy(lazy_langs, dict)()

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        # Searching apps dirs only exists for historic playdoh apps.
        # See playdoh's base settings for how message paths are set.
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('apps/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],
}

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'static', 'admin']

## Media and templates.

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'lib.context_processors.i18n',
    'lib.context_processors.globals',
    #'jingo_minify.helpers.build_ids',
)


def get_template_context_processors(exclude=(), append=(),
                        current={'processors': TEMPLATE_CONTEXT_PROCESSORS}):
    """
    Returns TEMPLATE_CONTEXT_PROCESSORS without the processors listed in
    exclude and with the processors listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the TEMPLATE_CONTEXT_PROCESSORS tuple across multiple settings files.
    """

    current['processors'] = tuple(
        [p for p in current['processors'] if p not in exclude]
    ) + tuple(append)

    return current['processors']


TEMPLATE_DIRS = (
    path('templates'),
)

# Storage of static files
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
)
COMPRESS_PRECOMPILERS = (
    #('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    #('text/x-sass', 'sass {infile} {outfile}'),
    #('text/x-scss', 'sass --scss {infile} {outfile}'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
#    from caching.base import cache
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
#    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
#        bc = jinja2.MemcachedBytecodeCache(cache._cache,
#                                           "%sj2:" % settings.CACHE_PREFIX)
#        config['cache_size'] = -1 # Never clear the cache
#        config['bytecode_cache'] = bc
    return config

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

## Celery

# True says to simulate background tasks without actually using celeryd.
# Good for local development in case celeryd is not running.
CELERY_ALWAYS_EAGER = True

BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Time in seconds before celery.exceptions.SoftTimeLimitExceeded is raised.
# The task can catch that and recover but should exit ASAP.
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 2

## Arecibo
# when ARECIBO_SERVER_URL is set, it can use celery or the regular wrapper
ARECIBO_USES_CELERY = True

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except socket.error:
    DOMAIN = 'localhost'
PROTOCOL = "http://"
PORT = 80

## django-mobility
MOBILE_COOKIE = 'mobile'


#########
# Cyder #
#########


TESTING = True if sys.argv[1:] and sys.argv[1] == 'test' else False
MIGRATING = (True if sys.argv[1:] and sys.argv[1] == 'maintain_migrate'
             else False)

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
        'search': ('css/search.scss',),
        'tags_css': ('css//lib/jquery.tagsinput.css',),
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
        'cyuser': (
            'js/cyuser/cyuser.js',
        ),
        'interface_delete': (
            'js/interface_delete.js',
        ),
        'systemform': (
            'js/systemform.js',
        ),
        'tags_js': (
            'js/lib/jquery.tagsinput.js',
        ),
    }
}

INSTALLED_APPS = [
    # Local apps
    'compressor',

    'tower',  # for ./manage.py extract (L10n)
    'cronjobs',  # for ./manage.py cron * cmd line tasks
    'django_browserid',


    # Django contrib apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # Third-party apps, patches, fixes
    'commonware.response.cookies',
    'djcelery',
    'django_nose',
    'session_csrf',

    # L10n
    'product_details',

    # Cyder
    'cyder',

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
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django_cas.middleware.CASMiddleware',
    'cyder.middleware.dev_authentication.DevAuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages'
)

SESSION_COOKIE_NAME = 'cyder'
SESSION_COOKIE_SECURE = False

AUTH_PROFILE_MODULE = 'cyder.UserProfile'
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
HMAC_KEYS = {  # for bcrypt only
    #'2012-06-06': 'cheesecake',
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

# Migration settings
POINTERS = [('128.193.76.253', 'cob-dc81.bus.oregonstate.edu', 'forward'),
            ('128.193.76.254', 'cob-dc82.bus.oregonstate.edu', 'forward'),
            ('128.193.76.252', 'cob-dc83.bus.oregonstate.edu', 'forward'),
            ('128.193.76.255', 'cob-dc84.bus.oregonstate.edu', 'forward'),
            ]

NONDELEGATED_NS = ['dns.merit.net', 'ns1.nero.net', 'ns1.oregonstate.edu',
                   'ns1.ucsb.edu', 'ns2.oregonstate.edu']

SECONDARY_ZONES = ["oscs.orst.edu", "oscs.oregonstate.edu", "oscs.orst.net",
                   "100.193.128.in-addr.arpa", "101.193.128.in-addr.arpa",
                   "4.215.10.in-addr.arpa", "5.215.10.in-addr.arpa",
                   "bus.oregonstate.edu", "74.193.128.in-addr.arpa",
                   "75.193.128.in-addr.arpa", "76.193.128.in-addr.arpa",
                   "77.193.128.in-addr.arpa", "78.193.128.in-addr.arpa",
                   "ceoas.oregonstate.edu", "coas.oregonstate.edu",
                   "oce.orst.edu", "64.193.128.in-addr.arpa",
                   "65.193.128.in-addr.arpa", "66.193.128.in-addr.arpa",
                   "67.193.128.in-addr.arpa", "68.193.128.in-addr.arpa",
                   "69.193.128.in-addr.arpa", "70.193.128.in-addr.arpa",
                   "71.193.128.in-addr.arpa"]

REVERSE_SOAS = [
    '139.201.199', '17.211.140', '18.211.140', '19.211.140', '20.211.140',
    '21.211.140', '28.211.140', '32.211.140', '33.211.140', '162.211.140',
    '163.211.140', '16.211.140', '193.128', '23.211.140', '165.211.140', '10',
    '26.211.140', '71.211.140', '224.211.140', '225.211.140', '226.211.140',
    '227.211.140', '228.211.140', '229.211.140', '230.211.140', '231.211.140',
    '232.211.140', '233.211.140', '234.211.140', '235.211.140', '236.211.140',
    '237.211.140', '238.211.140', '239.211.140', '100.193.128', '101.193.128',
    '74.193.128', '75.193.128', '76.193.128', '77.193.128', '78.193.128',
    '64.193.128', '65.193.128', '66.193.128', '67.193.128', '68.193.128',
    '69.193.128', '70.193.128', '71.193.128',
]

NONAUTHORITATIVE_DOMAINS = [
    'nero.net', 'peak.org', 'orvsd.org', 'pdx.orvsd.org',
]

# This list contains tuples that have a zone's name as their 0th element and a
# view's name as the 1st element. For example:
#
# ('mozilla.net', 'public'),
# ('mozilla.net', 'private')
#
# This will cause the public and private view of the mozilla.net zone to not
# have a config statement in the produced config/master.private and
# config/master.public files. The files net/mozilla/mozilla.net.public and
# net/mozilla.net.private *will* be generated and written to disk.
ZONES_WITH_NO_CONFIG = [
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        # 'cyder.api.v1.permissions.ReadOnlyIfAuthenticated',
        'cyder.api.v1.permissions.ReadOnlyIfAuthenticatedWriteIfSpecialCase',
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


BINDBUILD = {
    # stage_dir: Where test builds should go. This shouldn't be under
    # version control.
    'stage_dir': '/tmp/dns_stage/',

    # prod_dir: This is the directory where Cyder will place its DNS files.
    # This should be a Git repo.
    'prod_dir': '/tmp/dns_prod/cyzones/',

    # bind_prefix: This is the path to where Cyder zone files are built
    # relative to the root of the Git repo. This is usually a substring of
    # prod_dir.
    'bind_prefix': '/tmp/dns_prod/cyzones/',

    'lock_file': '/tmp/cyder_dns.lock',
    'pid_file': '/tmp/cyder_dns.pid',
    'named_checkzone': 'named-checkzone',
    'named_checkconf': 'named-checkconf',
    'named_checkzone_opts': '',

    'line_change_limit': 500,
    # Only one zone at a time should be removed
    'line_removal_limit': 10,

    'stop_file': '/tmp/cyder_dns.stop',
    'stop_file_email_interval': 1800,  # 30 minutes

    'last_run_file': '/tmp/cyder.last_run',
    'log_syslog': False,
}


# dhcp_build settings
# ===================


DHCPBUILD = {
    # stage_dir: Where test builds should go. This shouldn't be under
    # version control.
    'stage_dir': '/tmp/dhcp/stage',

    # prod_dir: Where Cyder will place the dhcpd configuration file. This
    # should be a Git repo.
    'prod_dir': '/tmp/dhcp/prod',

    'lock_file': '/tmp/cyder_dhcp.lock',
    'pid_file': '/tmp/cyder_dhcp.pid',
    'dhcpd': 'dhcpd',

    # target_file: The configuration file that will be generated
    'target_file': 'dhcpd.conf.data',

    # check_file: The conf file whose syntax will be checked (None means don't
    # check any file)
    'check_file': None,

    'line_change_limit': 500,
    'line_removal_limit': None,

    'stop_file': '/tmp/cyder_dhcp.stop',
    'stop_file_email_interval': 1800,  # 30 minutes

    'log_syslog': False,
}


DATETIME_INPUT_FORMATS = (
    '%m/%d/%y',              # '10/25/06'
    '%m/%d/%y %H:%M',
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
)

###############################
# more copied from funfactory #
###############################

## Middlewares, apps, URL configs.

def get_middleware(exclude=(), append=(),
                   current={'middleware': MIDDLEWARE_CLASSES}):
    """
    Returns MIDDLEWARE_CLASSES without the middlewares listed in exclude and
    with the middlewares listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the MIDDLEWARE_CLASSES tuple across multiple settings files.
    """

    current['middleware'] = tuple(
        [m for m in current['middleware'] if m not in exclude]
    ) + tuple(append)
    return current['middleware']

def get_apps(exclude=(), append=(), current={'apps': INSTALLED_APPS}):
    """
    Returns INSTALLED_APPS without the apps listed in exclude and with the apps
    listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the INSTALLED_APPS tuple across multiple settings files.
    """

    current['apps'] = tuple(
        [a for a in current['apps'] if a not in exclude]
    ) + tuple(append)
    return current['apps']
