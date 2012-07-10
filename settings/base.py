# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *


# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'example_css': (
            'css/examples/main.css',
        ),
        'example_mobile_css': (
            'css/examples/mobile.css',
        ),
    },
    'js': {
        'example_js': (
            'js/examples/libs/jquery-1.4.4.min.js',
            'js/examples/libs/jquery.cookie.js',
            'js/examples/init.js',
        ),
    }
}


INSTALLED_APPS = list(INSTALLED_APPS) + [
    # Example code. Can (and should) be removed for actual projects.
    #'examples',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    #'django_nose',
    'piston',
    #'south',
    'systems',
    'user_systems',
    'build',
    'dhcp',
    'truth',
    'api',
    'api_v2',
    'reports',
    'tastypie',
    'tastytools',
]


# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'build',
    'admin',
    'user_systems',
    'tastytools',
]

DJANGO_TEMPLATE_APPS = [
    'admin',
    'build',
    'user_systems',
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
AUTH_PROFILE_MODULE = "systems.UserProfile"
PISTON_IGNORE_DUPE_MODELS = True
#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
