# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *
from azure.core.exceptions import HttpResponseError

@record_only()
class MdpScenario(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(MdpScenario, self).__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "subscriptionId": self.get_subscription_id(),
                "location": "eastus2",
            }
        )

    @ResourceGroupPreparer(
        name_prefix="clitest_mdp", key="rg", parameter_name="rg"
    )
    def test_mdp_scenario(self):
        self.kwargs.update(
            {
                "poolName": self.create_random_name(prefix="cli", length=24),
                "poolName2": self.create_random_name(prefix="cli", length=24),
                "identityResourceId": "/subscriptions/a2e95d27-c161-4b61-bda4-11512c14c2c2/resourceGroups/ajaykn/providers/Microsoft.ManagedIdentity/userAssignedIdentities/ajaykn-msi",
                "devcenterProjectResourceId": "/subscriptions/21af6cf1-77ad-42cd-ad19-e193de033071/resourceGroups/ajaykn-wus/providers/Microsoft.DevCenter/projects/ajaykn-p1",
                "azureDevOpsOrgUrl": "https://dev.azure.com/managed-org-demo",
                "imageResourceId": "/Subscriptions/a2e95d27-c161-4b61-bda4-11512c14c2c2/Providers/Microsoft.Compute/Locations/eastus2/Publishers/canonical/ArtifactTypes/VMImage/Offers/0001-com-ubuntu-server-focal/Skus/20_04-lts-gen2/versions/latest"
            }
        )

        # List pools
        self.cmd(
            "az mdp pool list --resource-group \"{rg}\" ",
            checks=[
                self.check("length(@)", 0),
            ],
        )
        
        # Create new pool
        self.cmd(
            "az mdp pool create \
            --name \"{poolName}\" \
            --location \"{location}\" \
            --resource-group \"{rg}\" \
            --maximum-concurrency 3 \
            --identity \"type=userAssigned\" \"user-assigned-identities={{'{identityResourceId}':{{}}}}\" \
            --devcenter-project-resource-id \"{devcenterProjectResourceId}\" \
            --agent-profile \"stateless={{}}\" \
            --organization-profile \"azure-dev-ops={{organizations:[{{url:'{azureDevOpsOrgUrl}',parallelism:2}}],permissionProfile:{{kind:'CreatorOnly'}}}}\" \
            --fabric-profile \"vmss={{sku:{{name:Standard_D2ads_v5}},storageProfile:{{osDiskStorageAccountType:Standard}},images:[{{resourceId:'{imageResourceId}',buffer:*}}],osProfile:{{secretsManagementSettings:{{observedCertificates:[],keyExportable:false}},logonType:Service}}}}\" \
            ",
            checks=[
                self.check("identity.type", "UserAssigned"),
                self.check("name", "{poolName}"),
                self.check("location", "{location}"),
                self.check("resourceGroup", "{rg}"),
                self.check("provisioningState", "Succeeded"),
                self.check("maximumConcurrency", 3)
            ]
        )

        # List pools
        self.cmd(
            "az mdp pool list --resource-group \"{rg}\" ",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{poolName}")
            ],
        )

        # Show pool
        self.cmd(
            "az mdp pool show \
            --name \"{poolName}\" \
            --resource-group \"{rg}\" \
            ",
            checks=[
                self.check("identity.type", "UserAssigned"),
                self.check("name", "{poolName}"),
                self.check("location", "{location}"),
                self.check("resourceGroup", "{rg}"),
                self.check("provisioningState", "Succeeded"),
                self.check("agentProfile.kind", "Stateless"),
                self.check("maximumConcurrency", 3)
            ]
        )

        # Create or update pool
        self.cmd(
            "az mdp pool create \
            --name \"{poolName}\" \
            --location \"{location}\" \
            --resource-group \"{rg}\" \
            --tags CostCode=123 \
            --maximum-concurrency 1 \
            --identity \"type=userAssigned\" \"user-assigned-identities={{'{identityResourceId}':{{}}}}\" \
            --devcenter-project-resource-id \"{devcenterProjectResourceId}\" \
            --agent-profile \"stateless={{}}\" \
            --organization-profile \"azure-dev-ops={{organizations:[{{url:'{azureDevOpsOrgUrl}',parallelism:2}}],permissionProfile:{{kind:'CreatorOnly'}}}}\" \
            --fabric-profile \"vmss={{sku:{{name:Standard_D2ads_v5}},storageProfile:{{osDiskStorageAccountType:Standard}},images:[{{resourceId:'{imageResourceId}',buffer:*}}],osProfile:{{secretsManagementSettings:{{observedCertificates:[],keyExportable:false}},logonType:Service}}}}\" \
            ",
            checks=[
                self.check("identity.type", "UserAssigned"),
                self.check("name", "{poolName}"),
                self.check("location", "{location}"),
                self.check("resourceGroup", "{rg}"),
                self.check("provisioningState", "Succeeded"),
                self.check("maximumConcurrency", 1),
                self.check("tags.CostCode", "123")
            ]
        )

        # List pools
        self.cmd(
            "az mdp pool list --resource-group \"{rg}\" ",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{poolName}")
            ],
        )

        # Update the pool
        self.cmd(
            "az mdp pool update \
            --name \"{poolName}\" \
            --resource-group \"{rg}\" \
            --tags CostCode=234 \
            ",
            checks=[
                self.check("name", "{poolName}"),
                self.check("resourceGroup", "{rg}"),
                self.check("tags.CostCode", "234")
            ],
        )

        # Create another pool
        self.cmd(
            "az mdp pool create \
            --name \"{poolName2}\" \
            --location \"{location}\" \
            --resource-group \"{rg}\" \
            --maximum-concurrency 1 \
            --identity \"type=userAssigned\" \"user-assigned-identities={{'{identityResourceId}':{{}}}}\" \
            --devcenter-project-resource-id \"{devcenterProjectResourceId}\" \
            --agent-profile \"stateless={{}}\" \
            --organization-profile \"azure-dev-ops={{organizations:[{{url:'{azureDevOpsOrgUrl}',parallelism:2}}],permissionProfile:{{kind:'CreatorOnly'}}}}\" \
            --fabric-profile \"vmss={{sku:{{name:Standard_D2ads_v5}},storageProfile:{{osDiskStorageAccountType:Standard}},images:[{{resourceId:'{imageResourceId}',buffer:*}}],osProfile:{{secretsManagementSettings:{{observedCertificates:[],keyExportable:false}},logonType:Service}}}}\" \
            ",
            checks=[
                self.check("identity.type", "UserAssigned"),
                self.check("name", "{poolName2}"),
                self.check("location", "{location}"),
                self.check("resourceGroup", "{rg}"),
                self.check("provisioningState", "Succeeded"),
                self.check("maximumConcurrency", 1)
            ]
        )

        # List pools
        self.cmd(
            "az mdp pool list --resource-group \"{rg}\" ",
            checks=[
                self.check("length(@)", 2),
            ],
        )

        # Delete first pool
        self.cmd(
            "az mdp pool delete --yes \
            --name \"{poolName}\" \
            --resource-group \"{rg}\" "
        )

        # List pools
        self.cmd(
            "az mdp pool list --resource-group \"{rg}\" ",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "{poolName2}")
            ],
        )

    @ResourceGroupPreparer(
        name_prefix="clitest_mdp", key="rg", parameter_name="rg"
    )
    def test_mdp_create_error_scenario(self):
        self.kwargs.update(
            {
                "poolName": self.create_random_name(prefix="cli", length=24),
                "identityName": self.create_random_name(prefix="testid_", length=24),
            }
        )

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd(
                "az mdp pool create "
                '--name "{poolName}" '
                '--location "{location}" '
                '--resource-group "{rg}"',
            ).get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'ResourceCreationValidateFailed' in str(raises.exception)
