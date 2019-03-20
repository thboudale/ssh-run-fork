FROM sickp/alpine-sshd:latest
RUN apk update && apk add bash
RUN passwd -d root
COPY identity.pub /root/.ssh/authorized_keys
