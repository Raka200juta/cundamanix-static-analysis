#!/bin/bash
set -e 

python3 manage.py makemigrations && \
python3 manage.py makemigrations StaticAnalyzer && \
python3 manage.py migrate
set +e
export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-mobsf}"
export DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-mobsf}"
export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-}"
python3 manage.py createsuperuser --noinput
set -e
python3 manage.py create_roles

exec gunicorn -b 0.0.0.0:8001 "mobsf.MobSF.wsgi:application" --workers=1 --threads=10 --timeout=3600 \
    --worker-tmp-dir=/dev/shm --log-level=critical --log-file=- --access-logfile=- --error-logfile=- --capture-output
