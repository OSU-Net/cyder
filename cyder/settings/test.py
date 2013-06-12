# Copy to local.py.
import sys
import os


DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cyder.middleware.authentication.AuthenticationMiddleware',
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chili',
        'USER': 'root',
        'PASSWORD': 'yoursql',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset': 'utf8',
            'use_unicode': True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

SECRET_KEY = ''

SERVICES_URL = SITE_URL = STATIC_URL = 'http://localhost:8000/'

API_ACCESS = ('GET', 'POST', 'PUT', 'DELETE')
SCRIPT_URL = 'https://localhost.com'
DESKTOP_EMAIL_ADDRESS = 'desktop@example.com'
FROM_EMAIL_ADDRESS = 'inventory@example.com'
DHCP_CONFIG_OUTPUT_DIRECTORY = '/data/dhcpconfig-autodeploy'
UNAUTHORIZED_EMAIL_ADDRESS = ('manager@example.com')
