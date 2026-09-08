# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
import os
import tempfile

from azure.cli.testsdk import ScenarioTest, live_only
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
    @live_only()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus2",
    )
    def test_identity_binding_usages(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        identity_name = self.create_random_name("cli", 16)
        identity_binding_name = self.create_random_name("cliib", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "identity_name": identity_name,
                "identity_binding_name": identity_binding_name,
                "location": resource_group_location,
            }
        )

        create_aks_cmd = ("aks create --resource-group={resource_group} --name={aks_name} "
                          "--location={location} --no-ssh-key -o json")
        self.cmd(create_aks_cmd, checks=[
                 self.check("provisioningState", "Succeeded")])

        list_identity_binding_cmd = ("aks identity-binding list --resource-group {resource_group} "
                                     "--cluster-name {aks_name} -o json")
        self.cmd(
            list_identity_binding_cmd,
            checks=[
                self.check("length(@)", 0)
            ]
        )

        create_identity_cmd = ("identity create --resource-group {resource_group} --name {identity_name} "
                               "--location {location} -o json")
        identity = self.cmd(create_identity_cmd).get_output_in_json()
        identity_resource_id = identity["id"]
        identity_client_id = identity["clientId"]
        identity_tenant_id = identity["tenantId"]

        identity_binding_checks = [
            self.check("properties.provisioningState", "Succeeded"),
            self.check(
                "properties.managedIdentity.resourceId",
                identity_resource_id
            ),
            self.check(
                "properties.managedIdentity.clientId",
                identity_client_id
            ),
            self.check(
                "properties.managedIdentity.tenantId",
                identity_tenant_id
            ),
            self.check(
                f"ends_with(properties.oidcIssuer.oidcIssuerUrl, '/{identity_tenant_id}/{identity_client_id}')",
                True,
            ),
        ]

        create_identity_binding_cmd = ("aks identity-binding create --resource-group {resource_group} --cluster-name {aks_name} "
                                       "-n {identity_binding_name} -o json"
                                       f" --managed-identity-resource-id {identity_resource_id}")
        self.cmd(create_identity_binding_cmd, checks=identity_binding_checks)

        self.cmd(
            list_identity_binding_cmd,
            checks=[
                self.check("length(@)", 1)
            ]
        )

        show_identity_binding_cmd = ("aks identity-binding show --resource-group {resource_group} --cluster-name {aks_name} "
                                     "-n {identity_binding_name} -o json")
        self.cmd(show_identity_binding_cmd, checks=identity_binding_checks)

        # update the identity binding with an allowed subjects list loaded from a file
        allowed_subjects = [
            {
                "namespaceSelector": {
                    "matchLabels": ["kubernetes.io/metadata.name=team-a"]
                }
            },
            {
                "namespaceSelector": {
                    "matchLabels": ["team=backend"]
                },
                "serviceAccountSelector": {
                    "matchLabels": ["app=my-workload"]
                }
            },
        ]
        fd, allowed_subjects_file = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(os.remove, allowed_subjects_file)
        with open(allowed_subjects_file, "w", encoding="utf-8") as f:
            json.dump(allowed_subjects, f)
        self.kwargs.update({"allowed_subjects_file": allowed_subjects_file})

        update_identity_binding_cmd = (
            "aks identity-binding update --resource-group {resource_group} --cluster-name {aks_name} "
            "-n {identity_binding_name} --allowed-subjects-from-file \"{allowed_subjects_file}\" -o json"
        )
        self.cmd(update_identity_binding_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
            self.check("length(properties.allowedSubjects)", 2),
            self.check(
                "properties.allowedSubjects[0].namespaceSelector.matchLabels[0]",
                "kubernetes.io/metadata.name=team-a",
            ),
            self.check(
                "properties.allowedSubjects[1].serviceAccountSelector.matchLabels[0]",
                "app=my-workload",
            ),
        ])

        delete_identity_binding_cmd = ("aks identity-binding delete --resource-group {resource_group} --cluster-name {aks_name} "
                                       "-n {identity_binding_name} -o json")
        self.cmd(delete_identity_binding_cmd)

        self.cmd(
            list_identity_binding_cmd,
            checks=[
                self.check("length(@)", 0)
            ]
        )
