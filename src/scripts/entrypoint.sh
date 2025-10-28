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

# Choose a worker tmp directory. On Linux (and many containers) /dev/shm exists and is preferred.
# On macOS /dev/shm typically does not exist, which causes gunicorn to error out. Fall back to /tmp.
WORKER_TMP_DIR=${WORKER_TMP_DIR:-/dev/shm}
if [ ! -d "$WORKER_TMP_DIR" ]; then
    WORKER_TMP_DIR=/tmp
fi

exec gunicorn -b 0.0.0.0:5001 "mobsf.MobSF.wsgi:application" --workers=1 --threads=10 --timeout=3600 \
    --worker-tmp-dir="$WORKER_TMP_DIR" --log-level=critical --log-file=- --access-logfile=- --error-logfile=- --capture-output
