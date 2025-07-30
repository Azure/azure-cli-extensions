# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from azext_aks_preview.tests.latest.recording_processors import KeyReplacer
from azext_aks_preview.tests.latest.custom_preparers import (
    AKSCustomResourceGroupPreparer,
)


class IdentityBindingTestCases(ScenarioTest):
    
    def __init__(self, method_name):
        super(IdentityBindingTestCases, self).__init__(
            method_name,
            recording_processors=[KeyReplacer()],
        )


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
    )
    def test_identity_binding_usages(self, resource_group):
        aks_name = self.create_random_name("cliakstest", 16)
        identity_name = self.create_random_name("cli", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "identity_name": identity_name,
            }
        )

        create_aks_cmd = ("aks create --resource-group={resource_group} --name={aks_name} "
                          "--location={location} --no-ssh-key -o json")
        self.cmd(create_aks_cmd, checks=[self.check("provisioningState", "Succeeded")])

        list_identity_binding_cmd = ("aks identity-binding list --resource-group {resource_group} "
                                     "--cluster-name {aks_name} -o json")
        self.cmd(list_identity_binding_cmd, checks=[self.check("length(@)", 0)])

        create_identity_cmd = ("identity create --resource-group {resource_group} --name {identity_name} "
                               "--location {location} -o json")
        identity = self.cmd(create_identity_cmd, checks=[self.check("provisioningState", "Succeeded")]).get_output_in_json()
        identity_resource_id = identity["id"]

        create_identity_binding_cmd = ("aks identity-binding create --resource-group {resource_group} --cluster-name {aks_name} -o json"
                                       f" --managed-identity-resource-id {identity_resource_id}")
        self.cmd(create_identity_binding_cmd, checks=[self.check("provisioningState", "Succeeded")])

        self.cmd(list_identity_binding_cmd, checks=[self.check("length(@)", 1)])

        show_identity_binding_cmd = ("aks identity-binding show --resource-group {resource_group} --cluster-name {aks_name} -o json")
        self.cmd(show_identity_binding_cmd, checks=[
            self.check("provisioningState", "Succeeded"),
        ])