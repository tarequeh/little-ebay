# Django settings for little ebay project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

import os

SITE_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), '.')))
MEDIA_ROOT = os.path.realpath(os.path.abspath(os.path.join(SITE_ROOT, 'media')))
DB_ROOT = os.path.realpath(os.path.abspath(os.path.join(SITE_ROOT, 'db')))

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '%s/database.db' % DB_ROOT
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

SITE_URL = 'http://127.0.0.1:8000/'
MEDIA_URL = '%smedia/' % SITE_URL

ADMIN_MEDIA_PREFIX = '/admin-media/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = SITE_URL

SECRET_KEY = '_s7to88u2ap$tr@-qpmk3ebk_mldwj0e2_4p(812+y7e$%rj%g'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
)                               

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    os.path.realpath(os.path.abspath(os.path.join(SITE_ROOT, 'templates'))) 
)

ACCOUNT_ACTIVATION_DAYS = 10

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'lebay.apps.lebay',
    'uni_form',
)
