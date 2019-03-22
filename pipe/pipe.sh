#!/usr/bin/env bash
#
# Run a command or script on your server
#
# Required globals:
#   SSH_USER
#   SERVER
#   COMMAND
#
# Optional globals:
#   DEBUG (default: "false")
#   MODE (default: "command")
#   SSH_KEY (default: null)
#   PORT (default: 22)
#   

source "$(dirname "$0")/common.sh"

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
  : SSH_USER=${SSH_USER:?'SSH_USER variable missing.'}
  : SERVER=${SERVER:?'SERVER variable missing.'}
  : MODE=${MODE:-command}
  : COMMAND=${COMMAND:?'COMMAND varialbe missing.'}
}

setup_ssh_dir() {
  INJECTED_SSH_CONFIG_DIR="/opt/atlassian/pipelines/agent/ssh"
  # The default ssh key with open perms readable by alt uids
  IDENTITY_FILE="${INJECTED_SSH_CONFIG_DIR}/id_rsa_tmp"
  # The default known_hosts file
  KNOWN_SERVERS_FILE="${INJECTED_SSH_CONFIG_DIR}/known_hosts"

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

  if [ ! -f ${KNOWN_SERVERS_FILE} ]; then
      fail "No SSH known_hosts configured in Pipelines."
  fi

  cat ${KNOWN_SERVERS_FILE} >> ~/.ssh/known_hosts

  if [ -f ~/.ssh/config ]; then
      debug "Appending to existing ~/.ssh/config file"
  fi
  echo "IdentityFile ~/.ssh/pipelines_id" >> ~/.ssh/config
  chmod -R go-rwx ~/.ssh/
}

# default parameters
DEBUG=${DEBUG:="false"}

run_pipe() {
  if [[ ${MODE} = "command" ]]; then
  	info "Starting executing a ${MODE} on ${SERVER}"
    run ssh -A -tt -i ~/.ssh/pipelines_id -o 'StrictHostKeyChecking=no' -p ${PORT:-22} $SSH_USER@$SERVER "$COMMAND" 
  elif [[ ${MODE} = "script" ]]; then
  	info "Executing script ${COMMAND} on ${SERVER}"
  	run ssh -i ~/.ssh/pipelines_id -o 'StrictHostKeyChecking=no' -p ${PORT:-22} ${EXTRA_ARGS} $SSH_USER@$SERVER 'bash -s' < "$COMMAND"
  else
  	fail "Invalid MODE ${MODE}, valid values are: command, script"
  fi

  if [[ "${status}" == "0" ]]; then
    success "Exccution finished."
  else
    fail "Execution failed."
  fi
}

validate
setup_ssh_dir
run_pipe