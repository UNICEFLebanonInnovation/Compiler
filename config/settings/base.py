# -*- coding: utf-8 -*-
"""
Django settings for Student Registration project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ

ROOT_DIR = environ.Path(__file__) - 3  # (student_registration/config/settings/base.py - 3 = student_registration/)
APPS_DIR = ROOT_DIR.path('student_registration')

# Load operating system environment variables and then prepare to use them
env = environ.Env()

#Version
COMPILER_VERSION = '2.0'

# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables defined in the .env file,
    # that is to say variables from the .env files will only be used if not defined
    # as environment variables.
    env_file = str(ROOT_DIR.path('.env'))
    print('Loading : {}'.format(env_file))
    env.read_env(env_file)
    print('The .env file has been loaded. See base.py for more information')

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    'dal',
    'dal_select2',

    # Admin
    'suit',
    'django.contrib.admin',
    'markdown_deux',  # Required for Knowledgebase item formatting
    'bootstrapform',  # Required for nicer formatting of forms with the default templates
    'helpdesk',  # This is us!
    'rangefilter',
    'prettyjson',
    #'storages',
]
THIRD_PARTY_APPS = [
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'django_makemessages_xgettext',

    'bootstrap3',
    'bootstrap3_datetime',
    'import_export',
    'django_tables2',
    'django_celery_beat',
    'django_celery_results',
]

# Apps specific for this project go here.
LOCAL_APPS = [
    'student_registration.users',  # custom users app
    'student_registration.students',  # custom students app
    'student_registration.outreach',  # custom alp app
    'student_registration.alp',  # custom alp app
    'student_registration.clm',  # custom clm app
    'student_registration.attendances',  # custom attendances app
    'student_registration.enrollments',  # custom enrollments app
    'student_registration.schools',  # custom schools app
    'student_registration.locations',  # custom locations app
    'student_registration.dashboard',  # custom dashboard app
    'student_registration.winterization',  # custom winterization app
    'student_registration.backends',  # custom storage app
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'student_registration.lockout_middleware.StudentLockoutMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCKOUT_MAX_ATTEMPTS=10
LOCKOUT_TIME=600

# SECURITY CONFIGURATION
X_FRAME_OPTIONS = 'DENY'

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'student_registration.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)


IMPORT_EXPORT_USE_TRANSACTIONS = False
IMPORT_EXPORT_SKIP_ADMIN_LOG = False

# If not set default  is TempFolderStorage
# IMPORT_EXPORT_TMP_STORAGE_CLASS =

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""UNICEF Lebanon Innovation""", 'jcranwellward@unicef.org'),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///Student_Registration'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Beirut'

LANGUAGE_COOKIE_NAME = 'default_language'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ar-ar'

LANGUAGES = (
    ('ar-ar', 'arabic'),
    ('en-us', 'english'),
    # ('fr-fr', 'french'),
)

LANGUAGES_BIDI = ["ar-ar"]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {'NAME': 'student_registration.password_validators.NumberValidator',
     'OPTIONS': {
         'min_digits': 3, }},
    {'NAME': 'student_registration.password_validators.UppercaseValidator', },
    {'NAME': 'student_registration.password_validators.LowercaseValidator', },
    {'NAME': 'student_registration.password_validators.SymbolValidator', },
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'student_registration.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'student_registration.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
# LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

########## CELERY
INSTALLED_APPS += ['student_registration.taskapp.celery.CeleryConfig']
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
########## END CELERY

COUCHBASE_URL = env('COUCHBASE_URL', default='NO_URL')
COUCHBASE_USER = env('COUCHBASE_USER', default='NO_USER')
COUCHBASE_PASS = env('COUCHBASE_PASS', default='NO_PASS')

MONGODB_URI = env('MONGODB_URI', default='mongodb://localhost/education')

# django-compressor
# ------------------------------------------------------------------------------
# INSTALLED_APPS += ['compressor']
# STATICFILES_FINDERS += ['compressor.finders.CompressorFinder']

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings

LOCALE_PATHS = [
    str(APPS_DIR.path('static/locale')),
]

REST_FRAMEWORK = {
    # this setting fixes the bug where user can be logged in as AnonymousUser
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

SWAGGER_SETTINGS = {
    'is_authenticated': True,
    'is_superuser': True,
}

# Django Suit configuration
SUIT_CONFIG = {
    'ADMIN_NAME': 'Compiler',
    'CONFIRM_UNSAVED_CHANGES': False,

    'MENU': (
        {'label': 'View site', 'icon': 'icon-home', 'url': "/"},
        {'app': 'helpdesk', 'label': 'HelpDesk Config', 'icon': 'icon-info-sign'},
        {'label': 'HelpDesk Public', 'icon': 'icon-info-sign', 'url': '/helpdesk/dashboard/'},
        {'label': 'Dashboard', 'icon': 'icon-home', 'models': [
            {'url': '/dashboard/exporter/', 'label': 'Full data export'},
            {'url': '/dashboard/2ndshift-governorate-grade/', 'label': '2nd Shift by Governorate by Grade'},
            {'url': '/dashboard/2ndshift-governorate-age/', 'label': '2nd Shift by Governorate by Age'},
            {'url': '/dashboard/2ndshift-governorate-nationality/', 'label': '2nd Shift by Governorate by Nationality'},
            {'url': '/dashboard/2ndshift-grade-age/', 'label': '2nd Shift by Grade by Age'},
            {'url': '/dashboard/2ndshift-grade-nationality/', 'label': '2nd Shift by Grade by Nationality'},
            {'url': '/dashboard/2ndshift-nationality-age/', 'label': '2nd Shift by Nationality by Age'},
            {'url': '/dashboard/2ndshift-school-grade/', 'label': '2nd Shift by School by Grade'},
            {'url': '/dashboard/2ndshift-school-nationality/', 'label': '2nd Shift by School by Nationality'},
            # {'url': '/dashboard/2ndshift-overall/', 'label': '2nd Shift Overall'},
            {'url': '/dashboard/alp-overall/', 'label': 'ALP Overall'},
            {'url': '/dashboard/registrations-alp/', 'label': 'ALP Current round'},
            {'url': '/dashboard/registrations-alp-outreach/', 'label': 'ALP Outreach'},
            {'url': '/dashboard/registrations-alp-pre-test/', 'label': 'ALP Pre-test'},
            {'url': '/dashboard/registrations-alp-post-test/', 'label': 'ALP Post-test'},
        ]},
        {'app': 'auth', 'label': 'Groups', 'icon': 'icon-user'},
        {'app': 'users', 'label': 'Users', 'icon': 'icon-user'},
        {'app': 'clm', 'label': 'CLM', 'icon': 'icon-th-list'},
        {'label': 'ALP', 'icon': 'icon-th-list', 'models': (
            'alp.CurrentRound',
            'alp.CurrentOutreach',
            'alp.PreTest',
            'alp.PostTest',
            'alp.outreach',
            'alp.ALPRound',
        )},
        {'label': '2nd Shift', 'icon': 'icon-th-list', 'models': (
            'enrollments.enrollment',
            'enrollments.enrollmentgrading',
            'enrollments.dropout',
            'enrollments.disabled',
            'enrollments.LoggingStudentMove',
            'enrollments.LoggingProgramMove',
        )},
        {'label': 'Students', 'icon': 'icon-th-list', 'models': (
            'students.Student',
            'students.Nationality',
            'students.IDType',
            'students.Language',
            'students.StudentMatching',
        )},
        {'label': 'Schools', 'icon': 'icon-th-list', 'models': (
            'schools.School',
            'schools.EducationLevel',
            'schools.ClassLevel',
            'schools.ALPReferMatrix',
            'schools.ALPAssignmentMatrix',
            'schools.ClassRoom',
            'schools.EducationYear',
            'schools.Section',
        )},
        {'app': 'attendances', 'label': 'Attendances', 'icon': 'icon-th-list'},
        {'app': 'winterization', 'label': 'Winterization', 'icon': 'icon-th-list'},
        {'app': 'locations', 'label': 'Locations', 'icon': 'icon-globe'},
    )
}

HELPDESK_TRANSLATE_TICKET_COMMENTS = True
HELPDESK_SHOW_DELETE_BUTTON_SUPERUSER_FOLLOW_UP = True
HELPDESK_STAFF_ONLY_TICKET_OWNERS = True
HELPDESK_STAFF_ONLY_TICKET_CC = True
HELPDESK_CREATE_TICKET_HIDE_ASSIGNED_TO = True
HELPDESK_ENABLE_PER_QUEUE_PERMISSION = True
HELPDESK_VIEW_A_TICKET_PUBLIC = False
HELPDESK_SUBMIT_A_TICKET_PUBLIC = False
