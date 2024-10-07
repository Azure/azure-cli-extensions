# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import json
import unittest

from azext_spring.jobs.job import (job_create, job_update, job_start, _update_args, _update_envs,
                                   _update_job_properties,
                                   _update_secrets,
                                   _is_job_execution_in_final_state,
                                   _patch_job_trigger_config)
from azext_spring.vendored_sdks.appplatform.v2024_05_01_preview.models import (EnvVar,
                                                                               JobExecutionTemplate,
                                                                               JobResource,
                                                                               JobResourceProperties,
                                                                               ManualJobTriggerConfig,
                                                                               Secret)

from .asa_job_test_utils import (sample_job_resource, expected_create_job_payload,
                                 expected_start_job_payload, UpdateJobCase1Data, UpdateJobCase2Data, UpdateJobCaseData)
from ..common.test_utils import get_test_cmd

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class TestAsaJobs(unittest.TestCase):

    def setUp(self) -> None:
        self.envs_dict = {
            "prop1": "value1",
            "prop2": "value2"
        }
        self.secrets_dict = {
            "secret1": "secret_value1",
            "secret2": "secret_value2"
        }
        self.args_str = "random-args sleep 2"
        self.resource_group = "myResourceGroup"
        self.service = "myService"
        self.job_name = "test-job"

    def test_create_env_list(self):
        env_list = _update_envs(None, self.envs_dict, self.secrets_dict)

        self.assertEqual(4, len(env_list))
        for env in env_list:
            self.assertTrue(isinstance(env, EnvVar))

        self._verify_env_var(env_list[0], "prop1", "value1", None)
        self._verify_env_var(env_list[1], "prop2", "value2", None)
        self._verify_env_var(env_list[2], "secret1", None, "secret_value1")
        self._verify_env_var(env_list[3], "secret2", None, "secret_value2")

    def test_update_env_props_only(self):
        existed_env_list = [
            EnvVar(name="prop1", value="value1"),
            EnvVar(name="prop2", value="value1"),
            EnvVar(name="prop3", value=""),  # This is the case when only key is set
            EnvVar(name="secret1", secret_value="secret_value1"),
            EnvVar(name="secret2", secret_value="secret_value2"),
            EnvVar(name="secret3", secret_value=None),  # Backend won't response value of secret
        ]

        envs_dict = {
            "prop4": "value4"
        }

        secrets_dict = None

        env_list = _update_envs(existed_env_list, envs_dict, secrets_dict)

        self.assertEqual(4, len(env_list))
        for env in env_list:
            self.assertIsNotNone(env)
            self.assertTrue(isinstance(env, EnvVar))

        self._verify_env_var(env_list[0], "prop4", "value4", None)
        self._verify_env_var(env_list[1], "secret1", None, "secret_value1")
        self._verify_env_var(env_list[2], "secret2", None, "secret_value2")
        self._verify_env_var(env_list[3], "secret3", None, None)

    def test_update_env_secrets_only(self):
        existed_env_list = [
            EnvVar(name="prop1", value="value1"),
            EnvVar(name="prop2", value="value2"),
            EnvVar(name="secret1", secret_value="secret_value1"),
            EnvVar(name="secret2", secret_value="secret_value2"),
        ]

        secrets_dict = {
            "secret3": "secret_value3"
        }

        env_list = _update_envs(existed_env_list, None, secrets_dict)

        self.assertEqual(3, len(env_list))
        for env in env_list:
            self.assertIsNotNone(env)
            self.assertTrue(isinstance(env, EnvVar))

        self._verify_env_var(env_list[0], "prop1", "value1", None)
        self._verify_env_var(env_list[1], "prop2", "value2", None)
        self._verify_env_var(env_list[2], "secret3", None, "secret_value3")

    def test_update_secrets(self):
        existed_env_list = [
            EnvVar(name="prop1", value="value1"),
            EnvVar(name="prop2", value="value2"),
            EnvVar(name="secret1", secret_value="secret_value1"),
            EnvVar(name="secret2", secret_value="secret_value2"),
        ]

        secrets = [
            Secret(name="secret3", value="secret_value3")
        ]

        env_list = _update_secrets(existed_env_list, secrets)
        self._verify_env_var(env_list[0], "prop1", "value1", None)
        self._verify_env_var(env_list[1], "prop2", "value2", None)
        self._verify_env_var(env_list[2], "secret3", None, "secret_value3")

    def test_patch_job_trigger_config(self):
        test_data_list = [
            {
                "existed": None,
                "patch": None,
                "expected": None
            },
            {
                "existed": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=None,
                    retry_limit=None
                ),
                "patch": None,
                "expected": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=None,
                    retry_limit=None
                )
            },
            {
                "existed": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=None,
                    retry_limit=None
                ),
                "patch": ManualJobTriggerConfig(
                    parallelism=None,
                    timeout_in_seconds=15,
                    retry_limit=10
                ),
                "expected": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=15,
                    retry_limit=10
                )
            },
            {
                "existed": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=15,
                    retry_limit=None
                ),
                "patch": ManualJobTriggerConfig(
                    parallelism=None,
                    timeout_in_seconds=-1,
                    retry_limit=10
                ),
                "expected": ManualJobTriggerConfig(
                    parallelism=1,
                    timeout_in_seconds=None,
                    retry_limit=10
                )
            }
        ]

        for test_data in test_data_list:
            self._test_patch_job_trigger_config(test_data["existed"], test_data["patch"], test_data["expected"])

    def test_create_args(self):
        args = self.args_str
        target_args = _update_args(None, args)
        self.assertEqual(["random-args", "sleep", "2"], target_args)

    def test_update_args(self):
        args = self.args_str
        target_args = _update_args(["current-args"], args)
        self.assertEqual(["random-args", "sleep", "2"], target_args)

    def test_create_job_properties(self):
        existed_properties = None
        envs = self.envs_dict
        secret_envs = self.secrets_dict
        args = self.args_str
        target_properties = _update_job_properties(existed_properties, None, envs, secret_envs, args, None, None)

        self._verify_env_var(target_properties.template.environment_variables[0], "prop1", "value1", None)
        self._verify_env_var(target_properties.template.environment_variables[1], "prop2", "value2", None)
        self._verify_env_var(target_properties.template.environment_variables[2], "secret1", None, "secret_value1")
        self._verify_env_var(target_properties.template.environment_variables[3], "secret2", None, "secret_value2")
        self.assertEqual(["random-args", "sleep", "2"], target_properties.template.args)

    def test_update_job_properties(self):
        existed_properties = JobResourceProperties(
            template=JobExecutionTemplate(
                environment_variables=[
                    EnvVar(name="prop1", value="value1"),
                    EnvVar(name="secret1", secret_value="secret_value1"),
                ],
                args=["arg1", "arg2"]
            )
        )
        envs = self.envs_dict
        secret_envs = None
        args = self.args_str
        target_properties = _update_job_properties(existed_properties, None, envs, secret_envs, args, None, None)
        self.assertEqual(3, len(target_properties.template.environment_variables))
        self._verify_env_var(target_properties.template.environment_variables[0], "prop1", "value1", None)
        self._verify_env_var(target_properties.template.environment_variables[1], "prop2", "value2", None)
        self._verify_env_var(target_properties.template.environment_variables[2], "secret1", None, "secret_value1")
        self.assertEqual(["random-args", "sleep", "2"], target_properties.template.args)

    def test_is_job_execution_in_final_state(self):
        for status in ("Running", "Pending"):
            self.assertFalse(_is_job_execution_in_final_state(status))

        for status in ("Canceled", "Failed", "Completed"):
            self.assertTrue(_is_job_execution_in_final_state(status))

    @mock.patch('azext_spring.jobs.job.wait_till_end', autospec=True)
    def test_create_asa_job(self, wait_till_end_mock):
        wait_till_end_mock.return_value = None

        client_mock = mock.MagicMock()
        client_mock.job.begin_create_or_update = self._mock_begin_create_or_update
        client_mock.job.get.return_value = sample_job_resource()

        result_job = job_create(get_test_cmd(), client_mock, self.resource_group, self.service, self.job_name,
                                cpu="500m")
        self.assertEqual(json.dumps(result_job.serialize()), json.dumps(sample_job_resource().serialize()))

    def _mock_begin_create_or_update(self, resource_group, service, name, job_resource: JobResource):
        """
        To validate the request payload is expected.
        """
        self._verify_group_service_job_name(resource_group, service, name)
        self.assertEqual(json.dumps(job_resource.serialize(keep_readonly=True)),
                          json.dumps(JobResource.deserialize(json.loads(expected_create_job_payload)).serialize(
                              keep_readonly=True)))
        poller_mock = mock.Mock()
        return poller_mock

    @mock.patch('azext_spring.jobs.job.wait_till_end', autospec=True)
    def test_update_asa_job(self, wait_till_end_mock):
        wait_till_end_mock.return_value = None
        self._test_update_asa_job(UpdateJobCase1Data())
        self._test_update_asa_job(UpdateJobCase2Data())

    def _test_update_asa_job(self, test_case_data: UpdateJobCaseData):
        counter_job_get_in_test_update_asa_job = 0

        client_mock = mock.MagicMock()
        client_mock.job.get = lambda rg, service, name: \
            self._get_job_for_update_job_mock(rg, service, name,
                                              test_case_data.get_job_before(),
                                              test_case_data.get_job_after())
        client_mock.job.list_env_secrets = lambda rg, service, name: \
            self._list_env_secrets_for_update_job_mock(rg,
                                                       service,
                                                       name,
                                                       test_case_data.list_env_secrets_collection())
        client_mock.job.begin_create_or_update = lambda rg, service, name, job_resource: \
            self._begin_create_or_update_for_update_job_mock(rg, service, name, job_resource,
                                                             test_case_data.expected_update_job_payload())

        self.counter_job_get_in_test_update_asa_job = 0

        updated_job = job_update(get_test_cmd(), client_mock, self.resource_group, self.service, self.job_name,
                                 envs=test_case_data.envs(), secret_envs=test_case_data.secret_envs(),
                                 args=test_case_data.args())
        self.assertEqual(json.dumps(updated_job.serialize(keep_readonly=True)),
                          json.dumps(test_case_data.get_job_after().serialize(keep_readonly=True)))

    def _get_job_for_update_job_mock(self, resource_group, service, name, job_before, job_after):
        """
        client.job.get will be called multiple times when update the job. So use the workaround with a counter to route.
        """
        self._verify_group_service_job_name(resource_group, service, name)
        self.counter_job_get_in_test_update_asa_job += 1
        if self.counter_job_get_in_test_update_asa_job == 1:
            return job_before
        else:
            return job_after

    def _list_env_secrets_for_update_job_mock(self, resource_group, service, name, list_env_secrets_collection):
        self._verify_group_service_job_name(resource_group, service, name)
        return list_env_secrets_collection

    def _begin_create_or_update_for_update_job_mock(self, resource_group, service, name, job_resource: JobResource,
                                                    expected_update_job_payload):
        self._verify_group_service_job_name(resource_group, service, name)
        # Don't need to compare the readonly properties.
        self.assertEqual(json.dumps(expected_update_job_payload.serialize()), json.dumps(job_resource.serialize()))
        return None

    def test_job_start(self):
        client_mock = mock.MagicMock()
        client_mock.job.begin_start = self._begin_start_for_start_job_mock

        job_start(get_test_cmd(), client_mock, self.resource_group, self.service, self.job_name,
                  envs={"prop1", "v_prop1"},
                  secret_envs={"secret1", "v_secret1"},
                  cpu="1",
                  memory="512Mi",
                  args="sleep 30",
                  wait_until_finished=False)

    def _begin_start_for_start_job_mock(self, resource_group, service, name,
                                        job_execution_template: JobExecutionTemplate):
        self._verify_group_service_job_name(resource_group, service, name)
        self.assertEqual(
            json.dumps(JobExecutionTemplate.deserialize(json.loads(expected_start_job_payload)).serialize()),
            json.dumps(job_execution_template.serialize()))
        name_mock = mock.MagicMock()
        name_mock.return_value = "fake-execution-name"
        poller_mock = mock.MagicMock()
        poller_mock.result.return_value = name_mock
        return poller_mock

    def _verify_env_var(self, env: EnvVar, name, value, secret_value):
        self.assertIsNotNone(env)
        self.assertEqual(name, env.name)
        if value is not None:
            self.assertEqual(value, env.value)
            self.assertIsNone(env.secret_value)
        elif secret_value is not None:
            self.assertIsNone(env.value)
            self.assertEqual(secret_value, env.secret_value)

    def _verify_group_service_job_name(self, resource_group, service, name):
        self.assertEqual(self.resource_group, resource_group)
        self.assertEqual(self.service, service)
        self.assertEqual(self.job_name, name)

    def _test_patch_job_trigger_config(self, existed: ManualJobTriggerConfig, patch: ManualJobTriggerConfig,
                                       expected: ManualJobTriggerConfig):
        actual_result = _patch_job_trigger_config(existed, patch)
        if expected is None:
            self.assertIsNone(actual_result)
        else:
            self.assertIsNotNone(actual_result)
            self.assertEqual(actual_result.parallelism, expected.parallelism)
            self.assertEqual(actual_result.timeout_in_seconds, expected.timeout_in_seconds)
            self.assertEqual(actual_result.retry_limit, expected.retry_limit)
