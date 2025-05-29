from azure.cli.testsdk import *
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import shutil
import os
import tempfile
import json

class WorkloadOrchestrationTest(ScenarioTest):

    @classmethod
    def setUpClass(cls):
        super(WorkloadOrchestrationTest, cls).setUpClass()
        cls.rg = "ConfigManager-CloudTest-Playground-Portal"
        cls.version = "1.0.0"
        cls.location = "eastus2euap"
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
        self.resource_prefix = "cliwdx6u"


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
    def test_full_wom_workflow(self):
        # Get existing context and update capabilities
        context = self.cmd(
            f'az workload-orchestration context show --resource-group {self.context_rg} --name {self.context_name}'
        ).get_output_in_json()

        # Add new capabilities
        capabilities = context["properties"]["capabilities"] + [
            {"name": f"{self.resource_prefix}-Shampoo", "description": f"{self.resource_prefix}-Shampoo"},
            {"name": f"{self.resource_prefix}-Soap", "description": f"{self.resource_prefix}-Soap"}
        ]
        # Remove duplicates by name/description
        unique_capabilities = { (c["name"], c["description"]): c for c in capabilities }.values()

        # Write capabilities to a JSON file
        import json
        capabilities_file = os.path.join(os.path.dirname(__file__), "context-capabilities.json")
        with open(capabilities_file, "w") as f:
            json.dump(list(unique_capabilities), f, separators=(',', ':'))

        # Act: create context with updated capabilities and hierarchies
        self.cmd(
            f'az workload-orchestration context create '
            f'--resource-group {self.context_rg} '
            f'--location {self.context_location} '
            f'--name {self.context_name} '
            f'--capabilities "@{capabilities_file}" '
            f'--hierarchies [0].name=country [0].description=Country [1].name=region [1].description=Region [2].name=factory [2].description=Factory [3].name=line [3].description=Line'
        )

        # List contexts and check for created entry
        result = self.cmd(
            f'az workload-orchestration context list --resource-group {self.context_rg}'
        ).get_output_in_json()
        assert any(item.get("name") == self.context_name for item in result), f"{self.context_name} not found in context list"
        rg = self.rg
        location = self.location
        solution_template_name = f"{self.resource_prefix}-solution23456"
        capability = f"{self.resource_prefix}-Shampoo"
        version = "1.0.0"
        description = "This is Holtmelt Solution"

        # Prepare a temporary config template file for the solution template
        config_template_file = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "hotmelt-config-template-hard.yaml"
        )
        specs = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "specs.json"
        )

            # Create solution-template
        create_result = self.cmd(
            f"az workload-orchestration solution-template create "
            f"--solution-template-name '{solution_template_name}' "
            f"-g {rg} "
            f"-l eastus2euap --specification \"@{specs}\" "
            f"--capabilities '{capability}' "
            f"--description '{description}' "
            f"--config-template-file '{config_template_file}' "
            f"--version '{version}'"
        ).get_output_in_json()
        assert create_result["status"] == "Succeeded"
        assert create_result["properties"]["solutionTemplateId"].endswith(f"/{solution_template_name}")

        # Show solution-template
        show_result = self.cmd(
            f"az workload-orchestration solution-template show "
            f"-g {rg} --solution-template-name '{solution_template_name}'"
        ).get_output_in_json()
        assert show_result["name"] == solution_template_name
        assert show_result["properties"]["description"] == description
        assert show_result["properties"]["provisioningState"] == "Succeeded"
        assert capability in show_result["properties"]["capabilities"]

        # List solution-templates and check for created entry
        list_result = self.cmd(
            f"az workload-orchestration solution-template list --resource-group {rg}"
        ).get_output_in_json()
        assert any(item["name"] == solution_template_name for item in list_result), f"{solution_template_name} not found in solution-template list"


        target_name = f"{self.resource_prefix}-mk72"
        display_name = target_name
        hierarchy_level = "line"
        capability = f"{self.resource_prefix}-soap"
        description = "This is MK-71 Site"
        solution_scope = "new"

        # Prepare target-specification and extended-location files
        temp_dir = tempfile.mkdtemp()
        target_spec_file = os.path.join(temp_dir, "targetspecs.json")
        custom_location_file = os.path.join(temp_dir, "custom-location.json")

        # Example target specification content
        target_spec_content = {
            "scope": "default",
            "topologies": [
                {
                    "bindings": [
                        {
                            "provider": "providers.target.helm",
                            "role": "helm.v3",
                            "config": {
                                "inCluster": "true"
                            }
                        }
                    ]
                }
            ]
        }
        # Example custom location content
        custom_location_content = {
            "name": "/subscriptions/973d15c6-6c57-447e-b9c6-6d79b5b784ab/resourceGroups/configmanager-cloudtest-playground-canary/providers/Microsoft.ExtendedLocation/customLocations/BVT-Test-WOM-Location",
            "type": "CustomLocation"
        }

        with open(target_spec_file, "w") as f:
            json.dump(target_spec_content, f)
        with open(custom_location_file, "w") as f:
            json.dump(custom_location_content, f)

            # Create target
        create_result = self.cmd(
            f"az workload-orchestration target create "
            f"--resource-group {rg} "
            f"--location {location} "
            f"--name '{target_name}' "
            f"--display-name '{display_name}' "
            f"--hierarchy-level {hierarchy_level} "
            f"--capabilities '{capability}' "
            f"--description '{description}' "
            f"--solution-scope '{solution_scope}' "
            f"--target-specification \"@{target_spec_file}\" "
            f"--extended-location \"@{custom_location_file}\" "
        ).get_output_in_json()
        assert create_result["name"] == target_name
        assert create_result["properties"]["displayName"] == display_name
        assert create_result["properties"]["hierarchyLevel"] == hierarchy_level
        assert create_result["properties"]["provisioningState"] == "Succeeded"
        assert capability in create_result["properties"]["capabilities"]
        assert create_result["properties"]["description"] == description
        assert create_result["properties"]["solutionScope"] == solution_scope

        # Show target
        show_result = self.cmd(
            f"az workload-orchestration target show "
            f"--resource-group {rg} --target-name '{target_name}'"
        ).get_output_in_json()
        assert show_result["name"] == target_name
        assert show_result["properties"]["displayName"] == display_name
        assert show_result["properties"]["hierarchyLevel"] == hierarchy_level
        assert show_result["properties"]["provisioningState"] == "Succeeded"
        assert capability in show_result["properties"]["capabilities"]

        # List targets and check for created entry
        list_result = self.cmd(
            f"az workload-orchestration target list --resource-group {rg}"
        ).get_output_in_json()
        assert any(item["name"] == target_name for item in list_result), f"{target_name} not found in target list"


        # Remove solution-template version
        remove_result = self.cmd(
            f"az workload-orchestration solution-template remove-version "
            f"--solution-template-name '{solution_template_name}' --version {version} --resource-group {rg}"
        )

        # Delete solution-template (auto-confirm prompt)
        self.cmd(
            f"az workload-orchestration solution-template delete "
            f"--solution-template-name '{solution_template_name}' "
            f"--resource-group {rg} --yes",
            checks=None            )

        # Clean up the capabilities file
        os.remove(capabilities_file)




    @AllowLargeResponse()
    def test_target_lifecycle(self):
        import tempfile
        import json
        import shutil

        rg = self.rg
        location = self.location
        resource_prefix = self.resource_prefix


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


