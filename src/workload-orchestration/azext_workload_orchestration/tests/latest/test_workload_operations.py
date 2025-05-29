from azure.cli.testsdk import *
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

import os

class WorkloadOrchestrationTest(ScenarioTest):

    @classmethod
    def setUpClass(cls):
        super(WorkloadOrchestrationTest, cls).setUpClass()
        cls.rg = "ConfigManager-CloudTest-Playground-Portal"
        cls.version = "1.0.0"
        cls.location = "eastus"
        cls.schema_file = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "sharedschema.yaml"
        )
        cls.context_subscription_id = "973d15c6-6c57-447e-b9c6-6d79b5b784ab"
        cls.context_rg = "Mehoopany"
        cls.context_location = "eastus2euap"
        cls.context_name = "Mehoopany-Context"

    def setUp(self):
        super().setUp()
        self.schema_name = self.create_random_name(prefix='cli', length=24)
        self.resource_prefix = self.create_random_name(prefix='cli', length=8)


    def test_schema_lifecycle(self):
        # Create schema
        self.cmd(
            f'az workload-orchestration schema create --name {self.version} --resource-group {self.rg} --version "{self.version}" --schema-name "{self.schema_name}" --schema-file "{self.schema_file}" -l {self.location}',
            checks=[
                self.check('properties.name', self.version),
                self.check('properties.resourceGroup', self.rg)
            ]
        )

        # Show schema
        self.cmd(
            f'az workload-orchestration schema show -g {self.rg} --name {self.schema_name}',
            checks=[self.check('name', self.schema_name)]
        )

        # List schemas and check for created schema
        result = self.cmd(
            f'az workload-orchestration schema list --resource-group {self.rg}'
        ).get_output_in_json()
        assert any(item.get("name") == self.schema_name for item in result), f"{self.schema_name} not found in schema list"

        # Remove schema version
        result = self.cmd(
            f'az workload-orchestration schema remove-version --schema-name {self.schema_name} --version {self.version} --resource-group {self.rg}'
        ).get_output_in_json()
        assert result.get("status") == "Deletion Succeeded", "Schema version deletion did not succeed"

        # Optionally, delete the schema itself if needed (uncomment if supported)
        # self.cmd(
        #     f'az workload-orchestration schema delete --resource-group {self.rg} --name {self.schema_name}'
        # )


    @AllowLargeResponse()
    def test_config_template_lifecycle(self):
        import tempfile
        import shutil

        rg = "ConfigManager-CloudTest-Playground-Portal"
        location = "eastus2euap"
        config_template_name = self.create_random_name(prefix="CommonConfig", length=20)
        version = "1.0.0"
        description = "Common configuration settings"

        # Prepare a temporary config template file
        config_content = "configs:\n  AppName: Hotmelt"
        temp_dir = tempfile.mkdtemp()
        config_template_file = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "hotmelt-config-template-hard.yaml"
        )

        with open(config_template_file, "w") as f:
            f.write(config_content)

        try:
            # Create config-template
            create_result = self.cmd(
                f"az workload-orchestration config-template create "
                f"--resource-group {rg} "
                f"--config-template-name '{config_template_name}' "
                f"-l {location} "
                f"--description '{description}' "
                f"--config-template-file '{config_template_file}' "
                f"--version {version}"
            ).get_output_in_json()
            assert create_result["status"] == "Succeeded"
            assert create_result["properties"]["id"].endswith(f"/{config_template_name}/versions/{version}")

            # Show config-template
            show_result = self.cmd(
                f"az workload-orchestration config-template show "
                f"--resource-group {rg} "
                f"--config-template-name '{config_template_name}'"
            ).get_output_in_json()
            assert show_result["name"] == config_template_name
            assert show_result["properties"]["description"] == description
            assert show_result["properties"]["provisioningState"] == "Succeeded"

   

            # List config-templates and check for created entry
            list_result = self.cmd(
                f"az workload-orchestration config-template list "
                f"--resource-group {rg}"
            ).get_output_in_json()
            assert any(item["name"] == config_template_name for item in list_result), f"{config_template_name} not found in config-template list"

            # Remove config-template version
            remove_result = self.cmd(
                f"az workload-orchestration config-template remove-version "
                f"--resource-group {rg} "
                f"--config-template-name '{config_template_name}' "
                f"--version {version}"
            ).get_output_in_json()
            assert remove_result["status"] == "Deletion Succeeded"

            # Delete config-template (auto-confirm prompt)
            self.cmd(
                f"az workload-orchestration config-template delete "
                f"--resource-group {rg} "
                f"--config-template-name '{config_template_name}' --yes",
                checks=None,
                expect_failure=False,
            )

        finally:
            shutil.rmtree(temp_dir)