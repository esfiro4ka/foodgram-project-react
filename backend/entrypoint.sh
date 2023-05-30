#!/bin/sh
set -e

python manage.py collectstatic --no-input

python manage.py makemigrations

python manage.py migrate

python manage.py load_csv

gunicorn foodgram.wsgi:application --bind 0:8000
