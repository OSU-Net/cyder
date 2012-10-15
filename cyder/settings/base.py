# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *
from cyder.settings.dns import *

ROOT_URLCONF = 'cyder.urls'
MEDIA_ROOT = path('media')
MEDIA_URL = '/media/'

SASS_PREPROCESS = True
SASS_BIN = '/usr/bin/sass'
JINGO_MINIFY_USE_STATIC = False

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'cyder_css': (
            'css/lib/blueprint/ie.css',
            'css/lib/blueprint/print.css',
            'css/lib/blueprint/screen.css',
            'css/lib/blueprint/plugins/buttons/screen.css',
            'css/lib/blueprint/plugins/fancy-type/screen.css',
            'css/lib/blueprint/plugins/link-icons/screen.css',
            'css/lib/blueprint/plugins/rtl/screen.css',
            'css/lib/jquery.autocomplete.css',
            'css/lib/smoothness/jquery-ui-1.8.11.custom.css',
            'css/lib/ui-lightness/jquery-ui-1.8.11.custom.css',

            'css/base.scss',
            'css/navtabs.scss',
            'css/globals.scss',
        ),
    },
    'js': {
        'cyder_js': (
            'js/lib/jquery-1.6.1.min.js',
            'js/lib/attribute_adder.js',
            'js/lib/jquery-ui-1.8.11.custom.min.js',
            'js/lib/jquery.autocomplete.min.js',
            'js/lib/jquery.history.js',
            'js/lib/jQuery.rightclick.js',
            'js/lib/jquery.tools.min.js',
            'js/lib/jquery.validate.min.js',
            'js/lib/jquery.dataTables.js',
            'js/lib/jquery.tabletools.min.js',
            'js/lib/tablesorter.js',

            'js/application.js',
            'js/dhcp_raw_include.js',
            'js/key_value_validators.js',
            'js/master_form.js',
            'js/master_form_utils.js',
        ),
    }
}

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'api',
    'api_v2',
    'base',
    'base.mozdns',
    'build',
    'core',
    'core.site',
    'core.vlan',
    'core.network',
    'core.range',
    'core.build',
    'core.lib',
    'core.interface',
    'core.interface.static_intr',
    'core.search',
    'core.lib',
    'core.bulk_change',
    'dhcp',
    'mozdns',
    'mdns',
    'mdns.migrate',
    'mozdns',
    'mozdns.address_record',
    'mozdns.cname',
    'mozdns.domain',
    'mozdns.ip',
    'mozdns.mx',
    'mozdns.nameserver',
    'mozdns.ptr',
    'mozdns.soa',
    'mozdns.sshfp',
    'mozdns.srv',
    'mozdns.txt',
    'mozdns.view',
    'mozdns.mozbind',
    'mozdns.master_form',
    'reports',
    'systems',
    'truth',
    'user_systems',

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


# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'debug_toolbar',
    'tastytools',
]

DJANGO_TEMPLATE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

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

LOGGING = dict(loggers=dict(playdoh = {'level': logging.INFO}))
AUTH_PROFILE_MODULE = 'systems.UserProfile'
AUTHENTICATION_BACKENDS = (
        'middleware.restrict_by_api_token.RestrictByToken',
        'django.contrib.auth.backends.RemoteUserBackend',
)

#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

#########################################################
#                   MOZ DNS                             #
#########################################################

MOZDNS_BASE_URL = "/mozdns"
CORE_BASE_URL = "/core"
JINJA_CONFIG = {'autoescape': False}
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INTERNAL_IPS = ('127.0.0.1','10.22.74.139','10.250.2.54')

def custom_show_toolbar(request):
    return True # Always show toolbar, for example purposes only.


#############################################################
#                       MOZ DNS                             #
#############################################################
MOZDNS_BASE_URL = "/mozdns"
CORE_BASE_URL = "/core"
BUILD_PATH = 'builds'
