# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.helper import create_test, delete_test
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    create_random_name,
)

rg_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}


class LoadTestScenario(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenario, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_create(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        checks=[JMESPathCheck("testId", self.kwargs["test_id"]),
                    JMESPathCheck("loadTestConfiguration.engineInstances", 1),
                    JMESPathCheck("environmentVariables.rps", '10')]
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" '
            "--env rps=10 ",
            checks=checks,
        ).get_output_in_json()

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()
        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_list(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LIST_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert len(tests) > 0
        assert "fake_test_id" not in [test["testId"] for test in tests]
        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_show(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.SHOW_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        test = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_delete(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.DELETE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_download_files(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.DOWNLOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"path": temp_dir})

            create_test(self)

            self.cmd(
                "az load test download-files "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{path}"'
            )

            files = self.cmd(
                "az load test file list "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
            ).get_output_in_json()

            files_in_dir = [
                f
                for f in os.listdir(temp_dir)
                if os.path.isfile(os.path.join(temp_dir, f))
            ]
            for file in files:
                assert file["fileName"] in files_in_dir

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_create_with_args(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_WITH_ARGS_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "display_name": "Create_with_args_test",
                "test_description": "This is a load test created with arguments",
                "test_plan": LoadTestConstants.TEST_PLAN,
                "engine_instances": "1",
                "env": "a=2 b=3",
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 1),
            JMESPathCheck("environmentVariables.a", 2),
            JMESPathCheck("environmentVariables.b", 3),
        ]

        test = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--display-name '{display_name}' "
            "--description '{test_description}' "
            '--test-plan "{test_plan}" '
            "--engine-instances {engine_instances} "
            "--env {env} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_update(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.UPDATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )

        create_test(self)

        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instances 11 ",
            checks=[JMESPathCheck("loadTestConfiguration.engineInstances", 11)],
        ).get_output_in_json()

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_app_component(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.APP_COMPONENT_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "app_component_id": LoadTestConstants.APP_COMPONENT_ID.format(subscription_id=self.kwargs["subscription_id"]),
                "app_component_name": LoadTestConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestConstants.APP_COMPONENT_TYPE,
            }
        )

        create_test(self)

        # TODO: Create an Azure resource for app component
        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        self.cmd(
            "az load test app-component remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-id "{app_component_id}" '
            "--yes"
        )

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_server_metric(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.SERVER_METRIC_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "app_component_id": LoadTestConstants.APP_COMPONENT_ID.format(subscription_id=self.kwargs["subscription_id"]),
                "app_component_name": LoadTestConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestConstants.APP_COMPONENT_TYPE,
                "server_metric_id": LoadTestConstants.SERVER_METRIC_ID.format(subscription_id=self.kwargs["subscription_id"]),
                "server_metric_name": LoadTestConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestConstants.AGGREGATION,
            }
        )

        create_test(self)

        # TODO: Create an Azure resource for app component
        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        self.cmd(
            "az load test server-metric add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            '--metric-name " {server_metric_name}" '
            '--metric-namespace "{server_metric_namespace}" '
            "--aggregation {aggregation} "
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        server_metric = server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )
        assert server_metric is not None
        # assert self.kwargs[
        #     "server_metric_id"
        # ] == server_metric.get("id")

        self.cmd(
            "az load test server-metric remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            "--yes"
        )

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_file(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.FILE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "file_name": LoadTestConstants.FILE_NAME,
            }
        )

        create_test(self)

        self.cmd(
            "az load test file delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--yes"
        )

        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] not in [file["fileName"] for file in files]

        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{test_plan}" '
        )

        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] in [file["fileName"] for file in files]

        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"download_path": temp_dir})

            self.cmd(
                "az load test file download "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--file-name {file_name} "
                '--path "{download_path}" '
            )

            assert os.path.exists(os.path.join(temp_dir, self.kwargs["file_name"]))
