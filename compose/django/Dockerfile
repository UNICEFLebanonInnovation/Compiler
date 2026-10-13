FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_PASSWD="root:Docker!"

RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        openssh-server \
    && gcc --version \
    && echo "$SSH_PASSWD" | chpasswd \
    && mkdir -p /var/run/sshd /root/.ssh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./compose/django/sshd_config /etc/ssh/sshd_config

WORKDIR /code/

ARG REQUIREMENTS_FILE=production.txt

COPY requirements /code/requirements

RUN pip install --no-cache-dir --timeout=300 --retries=10 \
    -r /code/requirements/${REQUIREMENTS_FILE}

COPY . /code/

RUN python manage.py collectstatic --noinput --settings=config.settings.test

EXPOSE 2222 80

ENTRYPOINT ["/code/compose/django/entrypoint.sh"]
CMD ["/code/compose/django/gunicorn.sh"]
