FROM alpine:3.9

RUN apk --no-cache add \
    bash~=4.4 \
    openssh~=7.9 \
    curl~=7.64 && \
    curl -fsSL -o /common.sh https://bitbucket.org/bitbucketpipelines/bitbucket-pipes-toolkit-bash/raw/0.6.0/common.sh

COPY pipe /
COPY LICENSE.txt README.md pipe.yml /

ENTRYPOINT ["/pipe.sh"]
