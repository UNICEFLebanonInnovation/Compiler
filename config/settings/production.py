# -*- coding: utf-8 -*-
"""
Production Configurations

- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache
- Use sentry for error logging
- Use opbeat for error reporting

"""
from __future__ import absolute_import, unicode_literals
import logging


from .base import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY', default='l^y44io8f!zr^#n(ui099rz+w2(p^ufz3j726-^6)7g2ijcp!k')


# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += ['raven.contrib.django.raven_compat','student_registration.accounts', ]

# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------


EXTRA_MIDDLEWARE = ['student_registration.middleware.AutoLogout',
                    'student_registration.cache_control_middleware.CacheControlMiddleware',
                    # 'student_registration.one_session.OneSessionPerUserMiddleware',
                    'student_registration.hsts_middleware.HSTSMiddleware',
                    'student_registration.xframe_middleware.XFrameMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE + EXTRA_MIDDLEWARE
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE

# opbeat integration
# See https://opbeat.com/languages/django/
# INSTALLED_APPS += ['opbeat.contrib.django', ]
# OPBEAT = {
#     'ORGANIZATION_ID': env('DJANGO_OPBEAT_ORGANIZATION_ID'),
#     'APP_ID': env('DJANGO_OPBEAT_APP_ID'),
#     'SECRET_TOKEN': env('DJANGO_OPBEAT_SECRET_TOKEN')
# }
# MIDDLEWARE = ['opbeat.contrib.django.middleware.OpbeatAPMMiddleware', ] + MIDDLEWARE


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_PRELOAD = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['mdb2.uniceflebanon.org', ])
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', ]


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
INSTALLED_APPS += ['storages', ]

AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME', default='NO_AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY', default='NO_AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = env('AZURE_CONTAINER', default='NO_AZURE_CONTAINER')

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
DEFAULT_FILE_FORMAT = 'xlsx'
DEFAULT_FILE_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
DEFAULT_FILE_CONTENT_LANGUAGE = 'ar'
# Static Assets
# ------------------------
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# COMPRESSOR
# ------------------------------------------------------------------------------
# COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# COMPRESS_URL = STATIC_URL
# COMPRESS_ENABLED = env.bool('COMPRESS_ENABLED', default=True)
# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='Student Registration <noreply@compiler.uniceflebanon.org>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[Student Registration]')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ['anymail', ]

ANYMAIL = {
    'MAILGUN_API_KEY': env('DJANGO_MAILGUN_API_KEY', default=''),
    'MAILGUN_SENDER_DOMAIN': env('MAILGUN_SENDER_DOMAIN', default='')
}
EMAIL_BACKEND = 'anymail.backends.mailgun.MailgunBackend'

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------

# Use the Heroku-style specification
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL', default='postgres:///student_registration')

if env.bool('DATABASE_SSL_ENABLED', default=False):
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# CACHING
# ------------------------------------------------------------------------------
# CACHES = {
#     'default': {
#         # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': ''
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)
# Heroku URL does not pass the DB number, so we parse it in
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_LOCATION,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
#                                         # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
#         }
#     }
# }

INSTALLED_APPS += ['lockout', ]

# Sentry Configuration
SENTRY_DSN = env('DJANGO_SENTRY_DSN', default='')
SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', ],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', ],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', ],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry', ],
            'propagate': False,
        },
    },
}
SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
    'DSN': SENTRY_DSN
}

# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env('DJANGO_ADMIN_URL', default='admin')

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 20  # equivalent to 20 minutes
CSRF_USE_SESSIONS = True

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 600
CSRF_COOKIE_AGE = None

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
