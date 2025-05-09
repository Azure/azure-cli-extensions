# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.testsdk import (ScenarioTest)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class AsaJobScenarioTest(ScenarioTest):
    def setUp(self):
        _fake_rg_name = 'fake-resource-group-name'
        _fake_service_name = 'fake-asa-service-name'
        _fake_job_name = 'fake-job-name'
        self.kwargs.update({
            'g': _fake_rg_name,
            's': _fake_service_name,
            'j': _fake_job_name,
            'trigger_type': 'Manual'
        })

    @mock.patch('azext_spring.jobs.job.wait_till_end', autospec=True)
    @mock.patch('azext_spring.jobs.job_validators._ensure_job_not_exist', autospec=True)
    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    def test_asa_job_create(self, cf_spring_mock, only_support_enterprise_mock, _ensure_job_not_exist_mock,
                            wait_till_end_mock):
        """
        In this test case, we mainly check the request payload to create the job.
        """

        def verify_http_put_request(resource_group, service, name, job: models.JobResource, **kwargs):
            self.assertEqual(resource_group, self.kwargs['g'])
            self.assertEqual(service, self.kwargs['s'])
            self.assertEqual(name, self.kwargs['j'])
            self.assertEqual(kwargs.get('cpu'), job.properties.template.resource_requests.cpu)
            self.assertEqual(kwargs.get('memory'), job.properties.template.resource_requests.memory)
            self.assertTrue(isinstance(job.properties.trigger_config, models.ManualJobTriggerConfig))
            self.assertEqual(kwargs.get('parallelism'), job.properties.trigger_config.parallelism)
            self.assertEqual(kwargs.get('retry_limit'), job.properties.trigger_config.retry_limit)
            self.assertEqual(kwargs.get('timeout'), job.properties.trigger_config.timeout_in_seconds)
            self.assertEqual(kwargs.get('trigger_type'), job.properties.trigger_config.trigger_type)

        def construct_job_create_command_str(cpu,
                                             memory,
                                             parallelism,
                                             retry_limit,
                                             timeout,
                                             envs=None,
                                             secret_envs=None,
                                             args=None):
            command_str = 'spring job create -g {g} -s {s} -n {j}'
            if cpu is not None:
                command_str += f' --cpu {cpu}'
            if memory is not None:
                command_str += f' --memory {memory}'
            if parallelism is not None:
                command_str += f' --parallelism {parallelism}'
            if retry_limit is not None:
                command_str += f' --retry-limit {retry_limit}'
            if timeout is not None:
                command_str += f' --timeout {timeout}'
            if envs is not None:
                command_str += f' --envs {envs}'
            if secret_envs is not None:
                command_str += f' --envs {secret_envs}'
            if args is not None:
                command_str += f' --args {args}'
            return command_str

        client = mock.MagicMock()
        client.job.get.return_value = None
        cf_spring_mock.return_value = client

        only_support_enterprise_mock.return_value = True
        _ensure_job_not_exist_mock.return_value = None
        wait_till_end_mock.return_value = None

        for cpu in [None, "1"]:
            for memory in [None, "1Gi"]:
                for parallelism in [None, 1, 2]:
                    for retry_limit in [None, 0, 2]:
                        for timeout in [-1, None, 3600]:
                            expected_values_kwargs = {
                                'cpu': cpu if cpu is not None else "1",
                                'memory': memory if memory is not None else "2Gi",
                                'parallelism': parallelism,
                                'retry_limit': retry_limit,
                                'timeout': None if timeout == -1 else timeout,
                                'trigger_type': 'Manual'
                            }
                            client.job.begin_create_or_update = lambda rg, svc, n, job: \
                                verify_http_put_request(rg, svc, n, job, **expected_values_kwargs)
                            command_str = construct_job_create_command_str(
                                              cpu=cpu,
                                              memory=memory,
                                              parallelism=parallelism,
                                              retry_limit=retry_limit,
                                              timeout=timeout)
                            self.cmd(command_str)

    @mock.patch('azext_spring.jobs.job.wait_till_end', autospec=True)
    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    def test_asa_job_update(self, cf_spring_mock, only_support_enterprise_mock, wait_till_end_mock):
        """
        In this test case, we mainly check the request payload to create the job.
        """

        def mock_job_get(resource_group, service, job_name):
            job_resource = models.JobResource(
                name=self.kwargs.get('j'),
                id='fake-job-resource-id',
                type='Microsoft.AppPlatform/Spring/jobs',
                properties=models.JobResourceProperties(
                    provisioning_state='Succeeded',
                    template=models.JobExecutionTemplate(
                        environment_variables=[
                            models.EnvVar(
                                name='prop1',
                                value='plain text 1',
                                secret_value=None
                            ),
                            models.EnvVar(
                                name='prop2',
                                value='',  # Empty string on purpose
                                secret_value=None
                            ),
                            models.EnvVar(
                                name='secret1',
                                value=None,
                                secret_value=None,
                            ),
                            models.EnvVar(
                                name='secret2',
                                value=None,
                                secret_value=None,
                            )
                        ],
                        args=['a', 'naive args', '--sleep', '30'],
                        resource_requests=models.JobResourceRequests(
                            cpu=None,
                            memory=None,
                        )
                    ),
                    source=models.BuildResultUserSourceInfo(
                        type="BuildResult",
                        build_result_id="<default>",
                        version=None
                    ),
                    managed_component_references=[],
                    trigger_config=models.ManualJobTriggerConfig(
                        parallelism=None,
                        retry_limit=None,
                        timeout_in_seconds=3600
                    )
                )
            )
            return job_resource

        def mock_job_list_env_secrets(resource_group, service, job_name):
            result = models.EnvSecretsCollection(
                value=[
                    models.Secret(
                        name="secret1",
                        value="secret_value_1"
                    ),
                    models.Secret(
                        name="secret2",
                        value="secret_value_2"
                    )
                ]
            )
            return result

        def verify_http_put_request(resource_group,
                                    service,
                                    name,
                                    job: models.JobResource,
                                    cpu_verifier,
                                    memory_verifier,
                                    parallelism_verifier,
                                    retry_limit_verifier,
                                    timeout_verifier,
                                    all_envs_verifier,
                                    args_verifier):
            self.assertEqual(resource_group, self.kwargs['g'])
            self.assertEqual(service, self.kwargs['s'])
            self.assertEqual(name, self.kwargs['j'])
            cpu_verifier(job)
            memory_verifier(job)
            parallelism_verifier(job)
            retry_limit_verifier(job)
            timeout_verifier(job)
            all_envs_verifier(job)
            args_verifier(job)

        def construct_job_update_command_str(cpu, memory, parallelism, retry_limit, timeout, envs, secret_envs, args):
            command_str = 'spring job update -g {g} -s {s} -n {j}'
            if cpu is not None:
                command_str += f' --cpu {cpu}'
            if memory is not None:
                command_str += f' --memory {memory}'
            if parallelism is not None:
                command_str += f' --parallelism {parallelism}'
            if retry_limit is not None:
                command_str += f' --retry-limit {retry_limit}'
            if timeout is not None:
                command_str += f' --timeout {timeout}'
            if envs is not None:
                command_str += f' --envs {envs}'
            if secret_envs is not None:
                command_str += f' --secret-envs {secret_envs}'
            if args is not None:
                command_str += f' --args {args}'
            return command_str

        def cpu_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            """cpu_param_input is the command line input.
            None indicates not specified, for example, `az spring job update -n fake-job`, `--cpu` is not set at all.
            Empty string indicates only param is set, like `--cpu` in `az spring job update -n fake-job --envs`
            """
            expected_value = param_input if param_input is not None else \
                job_current.properties.template.resource_requests.cpu
            self.assertEqual(expected_value, job_for_put.properties.template.resource_requests.cpu)

        def memory_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            expected_value = param_input if param_input is not None else \
                job_current.properties.template.resource_requests.memory
            self.assertEqual(expected_value, job_for_put.properties.template.resource_requests.memory)

        def parallelism_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            expected_value = param_input if param_input is not None else \
                job_current.properties.trigger_config.parallelism
            self.assertEqual(expected_value, job_for_put.properties.trigger_config.parallelism)

        def retry_limit_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            expected_value = param_input if param_input is not None else \
                job_current.properties.trigger_config.retry_limit
            self.assertEqual(expected_value, job_for_put.properties.trigger_config.retry_limit)

        def timeout_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            expected_value = job_current.properties.trigger_config.timeout_in_seconds
            if param_input == -1:
                expected_value = None
            elif param_input is not None:
                expected_value = param_input
            self.assertEqual(expected_value, job_for_put.properties.trigger_config.timeout_in_seconds)

        def all_envs_verifier(envs_param_input, secret_envs_param_input, job_current: models.JobResource,
                              job_for_put: models.JobResource):
            """Verifiy envs and secret envs
            """
            expected_envs = [x for x in job_current.properties.template.environment_variables if
                             x.value is not None]
            if envs_param_input == '':
                expected_envs = []
            elif envs_param_input is not None:
                expected_envs = [
                    models.EnvVar(
                        name='prop3',
                        value='value3'
                    )
                ]
            expected_secret_envs = [
                models.EnvVar(
                    name='secret1',
                    secret_value='secret_value_1'
                ),
                models.EnvVar(
                    name='secret2',
                    secret_value='secret_value_2'
                )
            ]
            if secret_envs_param_input == '':
                expected_secret_envs = []
            elif secret_envs_param_input is not None:
                expected_secret_envs = [
                    models.EnvVar(
                        name='secret3',
                        secret_value='secret_value_3'
                    )
                ]
            expected_all_envs = expected_envs + expected_secret_envs
            self.assertEqual(len(expected_all_envs), len(job_for_put.properties.template.environment_variables))
            if len(expected_all_envs) == 0:
                return

            for env in job_for_put.properties.template.environment_variables:
                v = [x for x in expected_all_envs if
                     x.name == env.name and x.value == env.value and x.secret_value == env.secret_value]
                self.assertTrue(len(v) == 1)

        def args_verifier(param_input, job_current: models.JobResource, job_for_put: models.JobResource):
            expected_args = job_for_put.properties.template.args
            if param_input is not None:
                expected_args = [
                    'a', 'b', 'c:e', 'hello world', '--sleep=30'
                ]
            for arg in expected_args:
                self.assertIn(arg, job_for_put.properties.template.args)

        client = mock.MagicMock()
        client.job.get = mock_job_get
        client.job.list_env_secrets = mock_job_list_env_secrets
        cf_spring_mock.return_value = client

        only_support_enterprise_mock.return_value = True
        wait_till_end_mock.return_value = None

        job_current = mock_job_get(self.kwargs['g'], self.kwargs['s'], self.kwargs['j'])

        for cpu in [None, "6"]:
            for memory in [None, "1Gi"]:
                for parallelism in [None, 2]:
                    for retry_limit in [None, 2]:
                        for timeout in [-1, None, 3600]:
                            for envs in [None, '', 'prop3=value3']:  # Use empty space to reset
                                for secret_envs in [None, '', 'secret3=secret_value_3']:  # Use empty space to reset
                                    for args in [None, '\'a b c:e "hello world" --sleep=30\'']:
                                        client.job.begin_create_or_update = \
                                            lambda rg, svc, n, job: \
                                                verify_http_put_request(rg, svc, n, job,
                                                                        cpu_verifier=lambda x: \
                                                                            cpu_verifier(cpu, job_current, x),
                                                                        memory_verifier=lambda x: \
                                                                            memory_verifier(memory, job_current, x),
                                                                        parallelism_verifier=lambda x: \
                                                                            parallelism_verifier(parallelism,
                                                                                                 job_current, x),
                                                                        retry_limit_verifier=lambda x: \
                                                                            retry_limit_verifier(retry_limit,
                                                                                                 job_current, x),
                                                                        timeout_verifier=lambda x: \
                                                                            timeout_verifier(timeout, job_current, x),
                                                                        all_envs_verifier=lambda x: \
                                                                            all_envs_verifier(envs, secret_envs,
                                                                                              job_current, x),
                                                                        args_verifier=lambda x: \
                                                                            args_verifier(args, job_current, x)
                                                                        )
                                        command_str = construct_job_update_command_str(
                                            cpu=cpu,
                                            memory=memory,
                                            parallelism=parallelism,
                                            retry_limit=retry_limit,
                                            timeout=timeout,
                                            envs=envs,
                                            secret_envs=secret_envs,
                                            args=args
                                        )
                                        self.cmd(command_str)
