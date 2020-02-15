FROM alpine:latest
RUN apk update && apk add --no-cache rsyslog
CMD ["/usr/sbin/rsyslogd", "-n"]
