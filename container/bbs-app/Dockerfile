FROM alpine:latest

RUN apk update && \
    apk add python3 python3-dev uwsgi uwsgi-python3 py3-psycopg2 postgresql-client gcc musl-dev libffi-dev && \
    python3 -m pip install flask bcrypt && \
    apk del gcc musl-dev libffi-dev

CMD ["/bbs/entrypoint.sh"]

