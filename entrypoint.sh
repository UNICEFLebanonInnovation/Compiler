#!/bin/sh
set -e

until psql $DATABASE_URL -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

if [ "x$DJANGO_MIGRATE" = 'xon' ]; then
    python manage.py migrate --noinput
fi

if [ "x$DJANGO_COLLECTSTATIC" = 'xon' ]; then
    python manage.py collectstatic --noinput
fi

exec "$@"

/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000
