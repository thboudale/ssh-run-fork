# Bitbucket Pipelines Pipe: SSH run

Run a command or a bash script on your server

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
script:
  - pipe: atlassian/ssh-run:0.0.0
    variables:
      SSH_USER: '<string>'
      SERVER: '<string>'
      COMMAND: '<string>'
      MODE: '<string>' # Optional
      PORT: '<string>' # Optional
      SSH_KEY: '<string>' # Optional
      EXTRA_ARGS: '<string>' # Optional
      DEBUG: '<string>' # Optional
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| SSH_USER (*)          | SSH username. |
| SERVER (*)              | SSH server host. |
| COMMAND (*)           | Depending on the `MODE`, this can be a bash command to execute or a bash script name.|
| MODE                  | Mode of execution. This can be either bash `command` or a bash `script`. Default: `command`.|
| PORT                  | Port sshd is listening on. Default: `22`. |
| SSH_KEY               | An alternate SSH_KEY to use instead of the key configured in the Bitbucket Pipelines admin screens (which is used by default). This should be encoded as per the instructions given in the docs for [using multiple ssh keys](https://confluence.atlassian.com/bitbucket/use-ssh-keys-in-bitbucket-pipelines-847452940.html#UseSSHkeysinBitbucketPipelines-multiple_keys). |
| EXTRA_ARGS            | Additional arguments passed to the scp command (see [SSH docs](https://linux.die.net/man/1/ssh) for more details). |
| DEBUG                 | Enable extra debugging.|

_(*) = required variable._

## Prerequisites

* If you want to use the default behaviour for using the configured SSH key and known hosts file, you must have configured 
  the SSH private key and known_hosts to be used for the This pipe in your Pipelines settings
  (see [docs](https://confluence.atlassian.com/bitbucket/use-ssh-keys-in-bitbucket-pipelines-847452940.html))

## Examples

Basic example:

```yaml
script:
  - pipe: atlassian/ssh-run:0.0.0
    variables:
      SSH_USER: 'ec2-user'
      SERVER: '127.0.0.1'
      COMMAND: 'Echo $HOSTNAME'
```

Advanced example using a different SSH_KEY and executing a bash script on a remote server:

```yaml
script:
  - pipe: atlassian/ssh-run:0.0.0
    variables:
      SSH_USER: 'ec2-user'
      SERVER: '127.0.0.1'
      SSH_KEY: $MY_SSH_KEY
      MODE: 'script'
      COMMAND: 'myscript.sh'

```

## Support
If you’d like help with this pipe, or you have an issue or feature request, [let us know on Community](https://community.atlassian.com/t5/forums/postpage/choose-node/true/interaction-style/qanda?add-tags=bitbucket-pipelines,pipes,ssh).

If you’re reporting an issue, please include:

- the version of the pipe
- relevant logs and error messages
- steps to reproduce

## License
Copyright (c) 2018 Atlassian and others.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.