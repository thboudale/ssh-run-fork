from bitbucket_pipes_toolkit.test import PipeTestCase
import os
import subprocess
import uuid
import tarfile
import re
import base64   

import pytest
from docker.errors import ContainerError
import docker

docker_image = 'bitbucketpipelines/demo-pipe-python:ci' + \
    os.getenv('BITBUCKET_BUILD_NUMBER', 'local')



class SshRunPrivateKeyTestCase(PipeTestCase):

    @classmethod
    def tearDownClass(cls):
        dirname = os.path.dirname(__file__)
        os.remove(os.path.join(dirname, cls.ssh_key_file))
        os.remove(os.path.join(dirname, cls.ssh_key_file + '.pub'))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ssh_key_file = 'identity'
        dirname = os.path.dirname(__file__)
        result = subprocess.run(['ssh-keygen', '-f', os.path.join(dirname, cls.ssh_key_file), '-N', ''], check=False, text=True, capture_output=True)
        cls.private_key_image = cls.docker_client.images.build(path=dirname, dockerfile=os.path.join(dirname, 'Dockerfile'), tag='test-private-key')

    def setUp(self):

        self.api_client = docker.APIClient()
        self.ssh_key_file_container = self.docker_client.containers.run('test-private-key', detach=True)
      

    def tearDown(self):
        self.ssh_key_file_container.kill()


    
    # def test_no_parameters(self):
    #     with self.assertRaises(ContainerError) as error:
    #         self.run_container()
    #     self.assertIn('SSH_USER variable missing',
    #                   error.exception.stderr.decode())

    def test_default_success(self):
        cwd = os.getcwd()
        contiainer_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open(os.path.join(os.path.dirname(__file__), 'identity'), 'rb') as identity_file:
            identity_content = identity_file.read()

        result = self.run_container(environment={
            'SSH_USER': 'root',
            'HOST': contiainer_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'COMMAND': 'echo Hello $(hostname)',
            'MODE': 'command'
            },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'}},
            working_dir=cwd)
        self.assertIn(
            f'Hello {self.ssh_key_file_container.short_id}', result.decode())


        assert True

    def test_success_script(self):
        cwd = os.getcwd()
        contiainer_ip = self.api_client.inspect_container(self.ssh_key_file_container.id)['NetworkSettings']['IPAddress']

        with open('test_script.sh', 'w') as f:
            f.write('echo Script $HOSTNAME')

        with open(os.path.join(os.path.dirname(__file__), 'identity'), 'rb') as identity_file:
            identity_content = identity_file.read()


        result = self.run_container(environment={
            'SSH_USER': 'root',
            'HOST': contiainer_ip,
            'SSH_KEY': base64.b64encode(identity_content),
            'COMMAND': 'test_script.sh',
            'MODE': 'script'
            },
            volumes={cwd: {'bind': cwd, 'mode': 'rw'}},
            working_dir=cwd)
        self.assertIn(
            f'Script {self.ssh_key_file_container.short_id}', result.decode())
