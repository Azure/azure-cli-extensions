from azure.cli.testsdk import (
    ScenarioTest,
    JMESPathCheck,
)

from azext_load.tests.latest.helper import (
    create_test_run,
    create_test,
    delete_test_run,
    delete_test,
)

import json


class LoadTestRunScenario(ScenarioTest):
    load_test_resource = "hbisht-cli-testing"
    resource_group = "hbisht-rg"
    test_id = "sampletest1"
    test_id_long = "14fc47b6-fc59-4a1f-91d2-0678944ff121"
    test_run_id = "4008685a-79ab-4007-b559-11cf9051c06f"
    load_test_config_file = r"C:\\Users\\hbisht\\Desktop\\config.yaml"
    test_plan = r"C:\\Users\\hbisht\\Desktop\\LoadTest2.jmx"
    app_component_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss"
    app_component_type = r"Microsoft.Compute/virtualMachineScaleSets"
    metric_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU"
    metric_name = r"Percentage_CPU"
    metric_namespace = r"microsoft.compute/virtualmachinescalesets"
    aggregation = r"Average"

    def testcase_load_test_run_list(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id,
            }
        )

        list_of_test_run = self.cmd(
            "az load test-run list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id}"
        ).get_output_in_json()

        assert len(list_of_test_run) > 0
        assert self.kwargs["test_run_id"] in [test["testRunId"] for test in list_of_test_run]
        assert "fake_test_run_id" not in [test["testRunId"] for test in list_of_test_run]

    def testcase_load_test_run_show(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id,
            }
        )

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}"
        ).get_output_in_json()

        assert test_run["testRunId"] == self.kwargs["test_run_id"]
    
    def testcase_load_test_run_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id+"create_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )
        create_test(self, test_plan=self.kwargs["test_plan"] ,load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"], load_test_config_file=self.kwargs["load_test_config_file"])
        test_run_id = create_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
        delete_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_run_id=test_run_id)
        delete_test(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
    
    def testcase_load_test_run_delete(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id+"delete_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )
        create_test(self, test_plan=self.kwargs["test_plan"] ,load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"], load_test_config_file=self.kwargs["load_test_config_file"])
        test_run_id = create_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
        delete_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_run_id=test_run_id)
        delete_test(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])

    def testcase_load_test_run_update(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id+"update_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )

        create_test(self, test_plan=self.kwargs["test_plan"] ,load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"], load_test_config_file=self.kwargs["load_test_config_file"])
        test_run_id = create_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
        
        test_run = self.cmd(
            "az load test-run update "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id} "
            "--description 'Udated test run description' "
        ).get_output_in_json()

        assert test_run["description"] == "Udated test run description"

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id}"
        ).get_output_in_json()

        assert test_run["description"] == "Udated test run description"
        
        delete_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_run_id=test_run_id)
        delete_test(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])

    def testcase_load_test_run_download_files(self):
        self.kwargs.update(
        {   
            "load_test_resource": LoadTestRunScenario.load_test_resource,
            "resource_group": LoadTestRunScenario.resource_group,
            "test_id": LoadTestRunScenario.test_id+"download_test_run_files",
            "test_run_id": LoadTestRunScenario.test_run_id + "download_files",
            "load_test_config_file": LoadTestRunScenario.load_test_config_file,
            "test_plan": LoadTestRunScenario.test_plan,
        }
        )

        create_test(self, test_plan=self.kwargs["test_plan"] ,load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"], load_test_config_file=self.kwargs["load_test_config_file"])
        test_run_id = create_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
        
        self.cmd(
            "az load test-run download-files "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id} "
            "--path . "
            "--input "
            "--log "
        )

        delete_test_run(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_run_id=test_run_id)
        delete_test(self, load_test_resource=self.kwargs["load_test_resource"],resource_group= self.kwargs["resource_group"], test_id=self.kwargs["test_id"])
        

    """
        def testcase_load_test_run_stop(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id + "stop",
            }
        )

        self.cmd(
            "az load test-run create "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id} "
            "--no-wait "
        )

        #assert test_run["testRunId"] is not None

        self.cmd(
            "az load test-run stop "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}"
        )

        
        """