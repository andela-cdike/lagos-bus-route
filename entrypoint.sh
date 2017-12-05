#!/bin/sh
set -e



# Start long running process depending on what service we are running
if [[ $SERVICE == "web" ]]; then
    python manage.py migrate        # Apply database migrations
    python manage.py collectstatic --clear --noinput # clearstatic files
    python manage.py collectstatic --noinput  # collect static files
    gunicorn lagos_bus_route.wsgi:application \
        --name lagos_bus_route \
        --bind 0.0.0.0:8000
elif [[ $SERVICE == "celery" ]]; then
    celery worker -A lagos_bus_route --loglevel=debug
else
    echo "Unrecognized service: ${SERVICE}" 1>&2
    exit 1
fi