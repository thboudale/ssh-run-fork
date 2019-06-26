FROM alpine:3.9

RUN apk add --update --no-cache bash openssh
RUN wget -P / https://bitbucket.org/bitbucketpipelines/bitbucket-pipes-toolkit-bash/raw/0.4.0/common.sh

COPY pipe /
COPY LICENSE.txt README.md pipe.yml /

ENTRYPOINT ["/pipe.sh"]
