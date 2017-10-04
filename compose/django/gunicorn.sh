#!/bin/sh
service ssh start
gunicorn config.wsgi -w 4 -b 0.0.0.0:80 --log-level=info
