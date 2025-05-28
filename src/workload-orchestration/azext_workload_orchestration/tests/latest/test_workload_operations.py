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
    def test_context_create_with_capabilities_and_hierarchies(self):
        # Get existing context and update capabilities
        context = self.cmd(
            f'az workload-orchestration context show --subscription {self.context_subscription_id} --resource-group {self.context_rg} --name {self.context_name}'
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
            f'--subscription {self.context_subscription_id} '
            f'--resource-group {self.context_rg} '
            f'--location {self.context_location} '
            f'--name {self.context_name} '
            f'--capabilities "@{capabilities_file}" '
            f'--hierarchies [0].name=country [0].description=Country [1].name=region [1].description=Region [2].name=factory [2].description=Factory [3].name=line [3].description=Line'
        )

        # List contexts and check for created entry
        result = self.cmd(
            f'az workload-orchestration context list --subscription {self.context_subscription_id} --resource-group {self.context_rg}'
        ).get_output_in_json()
        assert any(item.get("name") == self.context_name for item in result), f"{self.context_name} not found in context list"

        # Clean up the capabilities file
        os.remove(capabilities_file)