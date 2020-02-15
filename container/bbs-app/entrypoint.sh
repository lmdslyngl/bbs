#!/bin/sh

echo "Waiting PostgreSQL..."
until psql -h postgres -U bbsrole -d bbsdb; do
    sleep 1
done
echo "PostgreSQL is up!"

echo "Starting uwsgi server..."
uwsgi --ini /etc/uwsgi/uwsgi.ini

