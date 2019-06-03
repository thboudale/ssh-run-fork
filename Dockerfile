FROM alpine:3.9

RUN apk update && apk add bash && apk add openssh && apk add curl
RUN curl -s https://bitbucket.org/bitbucketpipelines/bitbucket-pipes-toolkit-bash/raw/0.3.0/common.sh > /common.sh

COPY pipe /

ENTRYPOINT ["/pipe.sh"]
