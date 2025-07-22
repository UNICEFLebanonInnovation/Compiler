#!/bin/sh
set -ex

export DJANGO_SETTINGS_MODULE=config.settings.test

# Determine the project directory of this script so it can be executed
# from anywhere and still locate the requirements files.  In the CI
# environment the repository is mounted at ``/code`` while in local
# runs it may live elsewhere.
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install the main and test requirements.  The production requirements
# include the base dependencies such as Django which are needed for
# running the test suite.
pip install -r "$PROJECT_DIR/requirements/production.txt" \
            -r "$PROJECT_DIR/requirements/test.txt"
# Ensure there are no missing migrations
# python manage.py makemigrations --dry-run | grep 'No changes detected' || (echo 'There are changes which require migrations.' && exit 1)

# Run unittests and coverage report
# coverage erase
# coverage run manage.py test --noinput --keepdb --settings="$DJANGO_SETTINGS_MODULE" "$@"
#coverage html -d reports

# Check code style
#/venv/bin/flake8 .
