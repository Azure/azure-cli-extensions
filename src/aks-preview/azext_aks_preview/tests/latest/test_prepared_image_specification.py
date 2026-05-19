# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.testsdk import ScenarioTest, live_only

from azext_aks_preview.tests.latest.recording_processors import KeyReplacer
from azext_aks_preview.tests.latest.custom_preparers import (
    AKSCustomResourceGroupPreparer,
)


class PreparedImageSpecificationTestCases(ScenarioTest):
    def __init__(self, method_name):
        super(PreparedImageSpecificationTestCases, self).__init__(
            method_name,
            recording_processors=[KeyReplacer()],
        )

    @live_only()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus2euap",
    )
    def test_aks_pis_crud(self, resource_group, resource_group_location):
        """
        Basic CRUD smoke test of
        Microsoft.ContainerService/preparedImageSpecifications and
        Microsoft.ContainerService/preparedImageSpecifications/versions API
        endpoints without reference to an AKS managed cluster
        """
        pis_name = self.create_random_name("pis", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "pis_name": pis_name,
            }
        )

        list_pis_cmd = ("aks prepared-image-specification list -g {resource_group}")
        self.cmd(list_pis_cmd, checks=[
            self.check("length(@)", 0),
        ])

        create_pis_v1_cmd = (
            "aks prepared-image-specification create -g {resource_group} -n {pis_name} --version v1 --container-images busybox")
        self.cmd(create_pis_v1_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
            self.check("properties.version", "v1"),
        ])

        create_pis_v2_cmd = (
            "aks prepared-image-specification create -g {resource_group} -n {pis_name} --version v2 --container-images busybox")
        self.cmd(create_pis_v2_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
            self.check("properties.version", "v2"),
        ])

        # TODO: uncomment when API is fixed
        # self.cmd(list_pis_cmd, checks=[
        #     self.check("length(@)", 1),
        # ])

        show_pis_cmd = ("aks prepared-image-specification show -g {resource_group} -n {pis_name}")
        self.cmd(show_pis_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
            self.check("properties.version", "v2"),
        ])

        # TODO: uncomment when API is implemented
        # list_pis_version_cmd = ("aks prepared-image-specification version list -g {resource_group} --pis-name {pis_name}")
        # self.cmd(list_pis_version_cmd, checks=[
        #     self.check("length(@)", 2),
        # ])

        show_pis_version_cmd = (
            "aks prepared-image-specification version show -g {resource_group} --pis-name {pis_name} -n v1")
        self.cmd(show_pis_version_cmd, checks=[
            self.check("name", "v1"),
            self.check("properties.provisioningState", "Succeeded"),
        ])

        delete_pis_version_cmd = (
            "aks prepared-image-specification version delete -g {resource_group} --pis-name {pis_name} -n v1 -y")
        self.cmd(delete_pis_version_cmd)

        # TODO: uncomment when API is fixed
        # self.cmd(list_pis_version_cmd, checks=[
        #     self.check("length(@)", 1),
        # ])

        self.cmd(list_pis_cmd, checks=[
            self.check("length(@)", 1),
        ])

        update_pis_cmd = (
            "aks prepared-image-specification update -g {resource_group} -n {pis_name} --tags k=v")
        self.cmd(update_pis_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
            self.check("properties.version", "v2"),
            self.check("tags", {"k": "v"}),
        ])

        delete_pis_cmd = ("aks prepared-image-specification delete -g {resource_group} -n {pis_name} -y")
        self.cmd(delete_pis_cmd)

        self.cmd(list_pis_cmd, checks=[
            self.check("length(@)", 0),
        ])

    @live_only()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus2euap",
    )
    def test_aks_pis(self, resource_group, resource_group_location):
        """
        Basic smoke test of PIS with an AKS managed cluster
        """

        aks_name = self.create_random_name("aks", 16)
        pis_name = self.create_random_name("pis", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "pis_name": pis_name,
            }
        )

        create_pis_cmd = (
            "aks prepared-image-specification create -g {resource_group} -n {pis_name} --version latest --container-images docker.io/library/busybox:latest")
        pis = self.cmd(create_pis_cmd, checks=[
            self.check("properties.provisioningState", "Succeeded"),
        ]).get_output_in_json()

        pis_id = pis["id"] + "/versions/latest"

        create_aks_cmd = (
            "aks create -g {resource_group} -n {aks_name} -x --prepared-image-specification-id " + pis_id)
        self.cmd(create_aks_cmd, checks=[
            self.check("agentPoolProfiles[0].preparedImageSpecificationProfile.preparedImageSpecificationId", pis_id),
            self.check("provisioningState", "Succeeded"),
        ])

        update_aks_nodepool_cmd = (
            "aks nodepool update -g {resource_group} --cluster-name {aks_name} -n nodepool1 --prepared-image-specification-id ''")
        self.cmd(update_aks_nodepool_cmd, checks=[
            self.check("preparedImageSpecificationProfile", None),
            self.check("provisioningState", "Succeeded"),
        ])

        add_aks_nodepool_cmd = (
            "aks nodepool add -g {resource_group} --cluster-name {aks_name} -n nodepool2 --prepared-image-specification-id " + pis_id)
        self.cmd(add_aks_nodepool_cmd, checks=[
            self.check("preparedImageSpecificationProfile.preparedImageSpecificationId", pis_id),
            self.check("provisioningState", "Succeeded"),
        ])


if __name__ == "__main__":
    unittest.main()
