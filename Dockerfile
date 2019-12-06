FROM alpine:3.9

RUN apk --no-cache add \
    bash=4.4.19-r1 \
    openssh=7.9_p1-r6

RUN wget -P / https://bitbucket.org/bitbucketpipelines/bitbucket-pipes-toolkit-bash/raw/0.4.0/common.sh

COPY pipe /
COPY LICENSE.txt README.md pipe.yml /

ENTRYPOINT ["/pipe.sh"]
