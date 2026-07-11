"""
WSGI config for Student Registration project.
This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.
Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.
"""
import logging
import os
import sys

from django.core.wsgi import get_wsgi_application
ENV = os.getenv("ENVIRONMENT", "dev")         # "production" in prod
SERVICE = os.getenv("SERVICE_NAME", "bma-api")        # e.g., "bma-api"
VERSION = os.getenv("RELEASE_VERSION", "2.5")     # e.g., git sha/semver
ROLE = f"{SERVICE}-{ENV}"

# 1) Resource attributes (read by Azure Monitor)
# These OTEL_* env vars are picked up by azure.monitor.opentelemetry.
os.environ.setdefault("OTEL_SERVICE_NAME", ROLE)
os.environ.setdefault(
    "OTEL_RESOURCE_ATTRIBUTES",
    f"deployment.environment={ENV},service.version={VERSION},cloud.role={ROLE}"
)

# 2) Sampling per env (keep prod high, dev lower)
SAMPLING = 1.0 if ENV == "production" else 0.2

# ---------------- Azure Application Insights (OpenTelemetry) ----------------
# Configure BEFORE Django imports its app.
AZURE_MONITOR_CONNECTION_STRING = os.getenv("AZURE_MONITOR_CONNECTION_STRING")

if AZURE_MONITOR_CONNECTION_STRING:
    from azure.monitor.opentelemetry import configure_azure_monitor

    try:
        configure_azure_monitor(
            connection_string=AZURE_MONITOR_CONNECTION_STRING,
            sampling_ratio=SAMPLING,
            enable_live_metrics=True,
            enable_standard_metrics=True,
            enable_tracing=True,
            enable_metrics=True,
            enable_logging=True,
            disable_offline_storage=False,
            logger_name=ROLE
        )
    except Exception as _appins_exc:
        logging.getLogger(__name__).warning(
            "Azure Monitor telemetry disabled: %s", _appins_exc
        )
else:
    logging.getLogger(__name__).info(
        "AZURE_MONITOR_CONNECTION_STRING not set; skipping Azure Monitor configuration."
    )
# ---------------------------------------------------------------------------


# This allows easy placement of apps within the interior
# student_registration directory.
app_path = os.path.dirname(os.path.abspath(__file__)).replace('/config', '')
sys.path.append(os.path.join(app_path, 'student_registration'))

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()
# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
