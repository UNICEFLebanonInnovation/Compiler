#!/bin/sh
gunicorn config.wsgi -w 4 -b 0.0.0.0:80
