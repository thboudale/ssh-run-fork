FROM alpine:3.8

RUN apk update && apk add bash && apk add openssh && apk add curl

COPY pipe /

ENTRYPOINT ["/pipe.sh"]
