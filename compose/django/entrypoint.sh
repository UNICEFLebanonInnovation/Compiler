<<<<<<< HEAD
#!/bin/bash
set -e
# This entrypoint is used to play nicely with the current cookiecutter configuration.
# Since docker-compose relies heavily on environment variables itself for configuration, we'd have to define multiple
# environment variables just to support cookiecutter out of the box. That makes no sense, so this little entrypoint
# does all this for us.
export REDIS_URL=redis://redis:6379

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_USER

export CELERY_BROKER_URL=$REDIS_URL/0
=======
#!/bin/sh
set -e

touch /home/LogFiles/node_${WEBSITE_ROLE_INSTANCE_ID}_out.log
echo "$(date) Container started" >> /home/LogFiles/node_${WEBSITE_ROLE_INSTANCE_ID}_out.log

#until psql $DATABASE_URL -c '\l'; do
#  >&2 echo "Postgres is unavailable - sleeping"
#  sleep 1
#done
#
#>&2 echo "Postgres is up - continuing"
#
#if [ "x$DJANGO_MIGRATE" = 'xon' ]; then
#    /venv/bin/python manage.py migrate --noinput
#fi
#
#if [ "x$DJANGO_COLLECTSTATIC" = 'xon' ]; then
#    /venv/bin/python manage.py collectstatic --noinput
#fi
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

exec "$@"
