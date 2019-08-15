# -*- coding: utf-8 -*-
"""
Local settings

- Run in Debug mode

- Use console backend for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='u1zvr)oodenne1(e9^6gp1r_9yt+yj0t4_hk_jquo)g)zwpxul')

# Mail settings
# ------------------------------------------------------------------------------

# EMAIL_PORT = 1025
#
# EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
#CACHES = {
#   'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',#
#        'LOCATION': ''
#    }
#}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------

MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware',
                           'student_registration.middleware.AutoLogout',
                           'student_registration.cache_control_middleware.CacheControlMiddleware',
                           'student_registration.one_session.OneSessionPerUserMiddleware',
                           'student_registration.hsts_middleware.HSTSMiddleware',
                           'student_registration.xframe_middleware.XFrameMiddleware',
                           ]
INSTALLED_APPS += ['debug_toolbar','lockout','student_registration.accounts', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

# SECURITY CONFIGURATION
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_PRELOAD = True
# SECURE_REDIRECT_EXEMPT
# SECURE_SSL_HOST
X_FRAME_OPTIONS = 'DENY'

import socket
import os
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1']

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions', ]

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

########## CELERY
# In development, all tasks will be executed locally by blocking until the task returns
CELERY_ALWAYS_EAGER = True
########## END CELERY

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', ],
        'level': 'INFO'
    },
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 20 # equivalent to 20 minutes
#CSRF_USE_SESSIONS = True
LOCKOUT_MAX_ATTEMPTS = 5
LOCKOUT_TIME = 15



