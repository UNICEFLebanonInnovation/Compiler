FROM python:3.5-alpine

ADD requirements /requirements

ARG REQUIREMENTS_FILE=production.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            libxml2-dev \
            libxslt-dev \
            jpeg-dev \
            libffi-dev \
    && pyvenv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements/$REQUIREMENTS_FILE" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk add --update postgresql-client openssh \
    && apk del .build-deps

COPY ./compose/django/*.sh /
# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

# SSH support on Azure
RUN echo "root:Docker!" | chpasswd
COPY ./compose/django/sshd_config /etc/ssh/

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN /venv/bin/python manage.py collectstatic --noinput --settings=config.settings.test

# uWSGI will listen on this port
EXPOSE 2222 80

# Start
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/gunicorn.sh"]
