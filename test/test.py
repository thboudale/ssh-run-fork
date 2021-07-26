from bitbucket_pipes_toolkit.test import PipeTestCase
import os
import subprocess
import uuid
import tarfile
import re
import base64
from time import sleep

import pytest
from docker.errors import ContainerError
import docker

class SshRunPrivateKeyTestCase(PipeTestCase):

    ssh_config_dir = '/opt/atlassian/pipelines/agent/ssh'
    ssh_key_file = 'identity'
    test_image_name = 'test-private-key'

    @classmethod
    def tearDownClass(cls):
        dirname = os.path.dirname(__file__)
        os.remove(os.path.join(dirname, cls.ssh_key_file))
        os.remove(os.path.join(dirname, f'{cls.ssh_key_file}.pub'))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dirname = os.path.dirname(__file__)
        result = subprocess.run(['ssh-keygen', '-f', os.path.join(
            dirname, cls.ssh_key_file), '-N', ''], check=False, text=True, capture_output=True)
        cls.private_key_image = cls.docker_client.images.build(
            path=dirname, dockerfile=os.path.join(dirname, 'Dockerfile'), tag=cls.test_image_name)

    def setUp(self):

        self.api_client = self.docker_client.api
        self.ssh_key_file_container = self.docker_client.containers.run(
            self.test_image_name, detach=True)

        # wait untill sshd is up
        for i in range(10):
            if b'listening' in self.ssh_key_file_container.logs():
                break
            sleep(1)
        else:
            raise Exception('Failed to start SSHD')

    def tearDown(self):
        self.ssh_key_file_container.kill()

    def test_no_parameters(self):
        result = self.run_container()
        self.assertIn('SSH_USER variable missing',
                      result)

    def test_default_success(self):
        cwd = os.getcwd()
        contiainer_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open(os.path.join(os.path.dirname(__file__), self.ssh_key_file), 'rb') as identity_file:
            identity_content = identity_file.read()
        try:
            result = self.run_container(environment={
                'SSH_USER': 'root',
                'SERVER': contiainer_ip,
                'SSH_KEY': base64.b64encode(identity_content),
                'COMMAND': 'echo Hello $(hostname)',
                'MODE': 'command'
            },
                volumes={cwd: {'bind': cwd, 'mode': 'rw'},
                         self.ssh_config_dir: {'bind': self.ssh_config_dir, 'mode': 'rw'}})
            self.assertIn(
                f'Hello {self.ssh_key_file_container.short_id}', result)
        except ContainerError as error:
            print(error.container.logs())
            assert False

    def test_default_success_extra_args(self):
        cwd = os.getcwd()
        container_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open(os.path.join(os.path.dirname(__file__), self.ssh_key_file), 'rb') as identity_file:
            identity_content = identity_file.read()

        result = self.run_container(environment={
            'SSH_USER': 'root',
            'SERVER': container_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'COMMAND': 'echo Hello $(hostname)',
            'MODE': 'command',
            'EXTRA_ARGS': '-o ControlMaster=auto'
        },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'},
                     self.ssh_config_dir: {'bind': self.ssh_config_dir, 'mode': 'rw'}})
        self.assertIn(
            f'Hello {self.ssh_key_file_container.short_id}', result)

        result = self.run_container(environment={
            'SSH_USER': 'root',
            'SERVER': container_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'COMMAND': 'echo Hello $(hostname)',
            'MODE': 'command',
            'EXTRA_ARGS_COUNT': '1',
            'EXTRA_ARGS_0': '-o ControlMaster=auto'
        },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'},
                     self.ssh_config_dir: {'bind': self.ssh_config_dir, 'mode': 'rw'}})
        self.assertIn(
            f'Hello {self.ssh_key_file_container.short_id}', result)

    def test_success_script(self):
        cwd = os.getcwd()
        contiainer_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open('test_script.sh', 'w') as f:
            f.write('echo Script from $ENV_VAR $(hostname)')

        with open(os.path.join(os.path.dirname(__file__), 'identity'), 'rb') as identity_file:
            identity_content = identity_file.read()

        result = self.run_container(environment={
            'SSH_USER': 'root',
            'SERVER': contiainer_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'COMMAND': 'test_script.sh',
            'ENV_VARS': 'ENV_VAR="pipeline"',
            'MODE': 'script'
        },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'},
                     self.ssh_config_dir: {'bind': self.ssh_config_dir, 'mode': 'rw'}})
        self.assertIn(
            f'Script from pipeline {self.ssh_key_file_container.short_id}', result)

    def test_success_default_mode(self):
        cwd = os.getcwd()
        contiainer_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open(os.path.join(os.path.dirname(__file__), 'identity'), 'rb') as identity_file:
            identity_content = identity_file.read()

        result = self.run_container(environment={
            'SSH_USER': 'root',
            'SERVER': contiainer_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'ENV_VARS': 'ENV_VAR="pipeline"',
            'COMMAND': 'echo Hello from $ENV_VAR $(hostname)',
        },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'},
                     self.ssh_config_dir: {'bind': self.ssh_config_dir, 'mode': 'rw'}})
        self.assertIn(
            f'Hello from pipeline {self.ssh_key_file_container.short_id}', result)


