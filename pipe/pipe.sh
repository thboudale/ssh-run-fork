#!/usr/bin/env bash
#
# Run a command or script on your server
#
# Required globals:
#   NAME
#
# Optional globals:
#   DEBUG (default: "false")

# source "$(dirname "$0")/common.sh"

source <(curl -s https://bitbucket.org/bitbucketpipelines/bitbucket-pipes-toolkit-bash/raw/0.0.0/common.sh)

info "Executing the pipe..."

enable_debug() {
  if [[ "${DEBUG}" == "true" ]]; then
    info "Enabling debug mode."
    set -x
  fi
}
enable_debug

validate() {
  # required parameters
  # : USER=${USER:?'SSH_USER variable missing.'}
  : SSH_USER=${SSH_USER:?'SSH_USER variable missing.'}
  : HOST=${HOST:?'HOST variable missing.'}
}

setup_ssh_dir() {
  INJECTED_SSH_CONFIG_DIR="/opt/atlassian/pipelines/agent/ssh"
  # The default ssh key with open perms readable by alt uids
  IDENTITY_FILE="${INJECTED_SSH_CONFIG_DIR}/id_rsa_tmp"
  # The default known_hosts file
  KNOWN_HOSTS_FILE="${INJECTED_SSH_CONFIG_DIR}/known_hosts"

  mkdir -p ~/.ssh || debug "adding ssh keys to existing ~/.ssh"
  touch ~/.ssh/authorized_keys

  # If given, use SSH_KEY, otherwise check if the default is configured and use it
  if [ "${SSH_KEY}" != "" ]; then
     info "Using passed SSH_KEY"
     (umask  077 ; echo ${SSH_KEY} | base64 -d > ~/.ssh/pipelines_id)
  elif [ ! -f ${IDENTITY_FILE} ]; then
     fail "No default SSH key configured in Pipelines."
  else
     info "Using default ssh key"
     cp ${IDENTITY_FILE} ~/.ssh/pipelines_id
  fi

  # ssh-add ~/.ssh/pipelines_id

  # if [ ! -f ${KNOWN_HOSTS_FILE} ]; then
  #     fail "No SSH known_hosts configured in Pipelines."
  # fi

  # cat ${KNOWN_HOSTS_FILE} >> ~/.ssh/known_hosts

  if [ -f ~/.ssh/config ]; then
      debug "Appending to existing ~/.ssh/config file"
  fi
  echo "IdentityFile ~/.ssh/pipelines_id" >> ~/.ssh/config
  chmod -R go-rwx ~/.ssh/
}

# default parameters
DEBUG=${DEBUG:="false"}

run_pipe() {
  info "Starting executing a command on ${SERVER}"
  run ssh -A -tt -i ~/.ssh/pipelines_id -o 'StrictHostKeyChecking=no' -p ${PORT:-22} root@$HOST "$COMMAND" 

  if [[ "${status}" == "0" ]]; then
    success "Deployment finished."
  else
    fail "Deployment failed."
  fi
}

setup_ssh_dir
validate
run_pipe