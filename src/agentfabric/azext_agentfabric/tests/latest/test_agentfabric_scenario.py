# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.mgmt.core.tools import parse_resource_id


LOCATION = os.environ.get("AZURE_TEST_AGENTFABRIC_LOCATION", "centraluseuap")


class OperationStatusSignatureReplacer(RecordingProcessor):
    _pattern = re.compile(r"(\b[0-9a-f-]{36}(?:\*|%2a))[0-9a-f]{64}\b", re.IGNORECASE)
    _query_pattern = re.compile(r"""([?&](?:t|c|s|h)=)[^&\s"'<>\\]+""", re.IGNORECASE)

    @classmethod
    def redact(cls, value):
        if isinstance(value, str):
            value = cls._pattern.sub(lambda match: match[1] + "0" * 64, value)
            return cls._query_pattern.sub(lambda match: match[1] + "REDACTED", value)
        if isinstance(value, bytes):
            return cls.redact(value.decode("utf-8")).encode("utf-8")
        if isinstance(value, list):
            return [cls.redact(item) for item in value]
        if isinstance(value, dict):
            return {key: cls.redact(item) for key, item in value.items()}
        return value

    def process_request(self, request):
        request.uri = self.redact(request.uri)
        request.body = self.redact(request.body)
        return request

    def process_response(self, response):
        return self.redact(response)


class OperationStatusSignatureReplacerTest(unittest.TestCase):

    def test_operation_status_signatures_are_redacted_consistently(self):
        operation_id = "11111111-2222-3333-4444-555555555555"
        url = "https://management.azure.com/operationStatuses/" + operation_id + "*" + "a" * 64
        scrubbed = OperationStatusSignatureReplacer.redact({
            "uri": url,
            "headers": {"location": [url]},
            "body": url.encode("utf-8"),
        })
        expected = url[:-64] + "0" * 64
        self.assertEqual(scrubbed["uri"], expected)
        self.assertEqual(scrubbed["headers"]["location"], [expected])
        self.assertEqual(scrubbed["body"], expected.encode("utf-8"))
        self.assertEqual(OperationStatusSignatureReplacer.redact(scrubbed), scrubbed)
        self.assertEqual(
            OperationStatusSignatureReplacer.redact(url + "?api-version=2026-06-01&t=123&c=cert&s=signature&h=hash"),
            expected + "?api-version=2026-06-01&t=REDACTED&c=REDACTED&s=REDACTED&h=REDACTED",
        )


class AksPrerequisiteClientTest(unittest.TestCase):

    def test_prerequisite_api_version_is_pinned(self):
        cli_ctx = object()
        with patch(__name__ + ".get_mgmt_service_client") as factory:
            client = AgentfabricResourceScenario._aks_prerequisite_client(cli_ctx, "test-subscription")
        factory.assert_called_once_with(
            cli_ctx, ResourceType.MGMT_CONTAINERSERVICE,
            subscription_id="test-subscription", api_version="2026-06-01"
        )
        self.assertIs(client, factory.return_value)


class AgentfabricResourceScenario(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[OperationStatusSignatureReplacer()])

    @ResourceGroupPreparer(name_prefix="clitestaf", location=LOCATION)
    def test_agentfabric_fabric_lifecycle(self, resource_group):
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliaf", length=24),
            "location": LOCATION,
        })
        self.cmd(
            "agentfabric create -g {rg} -n {fabric} -l {location} "
            "--trust-domain cli.agentfabric.example --identity type=SystemAssigned",
            checks=[
                self.check("name", "{fabric}"),
                self.check("location", "{location}"),
                self.check("properties.provisioningState", "Succeeded"),
                self.check("identity.type", "SystemAssigned"),
            ],
        )
        try:
            self.cmd("agentfabric wait -g {rg} -n {fabric} --created")
            self.cmd("agentfabric show -g {rg} -n {fabric}", checks=[
                self.check("name", "{fabric}"),
                self.check("properties.trustDomain", "cli.agentfabric.example"),
            ])
            self.cmd("agentfabric list -g {rg}", checks=[
                self.check("[?name=='{fabric}'] | length(@)", 1),
            ])
            self.cmd("agentfabric update -g {rg} -n {fabric} --tags stage=updated --no-wait")
            self.cmd("agentfabric wait -g {rg} -n {fabric} --updated")
            self.cmd("agentfabric show -g {rg} -n {fabric}", checks=[
                self.check("tags.stage", "updated"),
            ])
        finally:
            self.cmd("agentfabric delete -g {rg} -n {fabric} --yes")
        self.cmd("agentfabric wait -g {rg} -n {fabric} --deleted")
        self.cmd("agentfabric list -g {rg}", checks=[self.is_empty()])

    @ResourceGroupPreparer(name_prefix="clitestafpg", location=LOCATION)
    def test_agentfabric_policy_group_lifecycle(self, resource_group):
        self.kwargs.update({
            "policy": self.create_random_name(prefix="cliafpg", length=24),
            "location": LOCATION,
        })
        self.cmd(
            "agentfabric policy-group create -g {rg} -n {policy} -l {location} "
            "--display-name 'CLI scenario policy group' --description 'Disposable CLI test' --priority 100",
            checks=[
                self.check("name", "{policy}"),
                self.check("properties.priority", 100),
                self.check("properties.provisioningState", "Succeeded"),
            ],
        )
        try:
            self.cmd("agentfabric policy-group wait -g {rg} -n {policy} --created")
            self.cmd("agentfabric policy-group show -g {rg} -n {policy}", checks=[
                self.check("properties.displayName", "CLI scenario policy group"),
            ])
            self.cmd("agentfabric policy-group list -g {rg}", checks=[
                self.check("[?name=='{policy}'] | length(@)", 1),
            ])
            self.cmd("agentfabric policy-group update -g {rg} -n {policy} --tags stage=updated --no-wait")
            self.cmd("agentfabric policy-group wait -g {rg} -n {policy} --updated")
            self.cmd("agentfabric policy-group show -g {rg} -n {policy}", checks=[
                self.check("tags.stage", "updated"),
            ])
        finally:
            self.cmd("agentfabric policy-group delete -g {rg} -n {policy} --yes")
        self.cmd("agentfabric policy-group wait -g {rg} -n {policy} --deleted")
        self.cmd("agentfabric policy-group list -g {rg}", checks=[self.is_empty()])

    @ResourceGroupPreparer(name_prefix="clitestafetb", location=LOCATION)
    def test_agentfabric_egress_trust_bundle_show(self, resource_group):
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliafetb", length=24),
            "location": LOCATION,
        })
        self.cmd("agentfabric create -g {rg} -n {fabric} -l {location}")
        try:
            self.cmd("agentfabric egress-trust-bundle show -g {rg} --fabric-name {fabric}", checks=[
                self.check("name", "default"),
                self.check("type", "Microsoft.NetworkSecurity/agentFabrics/egressTrustBundles", case_sensitive=False),
            ])
        finally:
            self.cmd("agentfabric delete -g {rg} -n {fabric} --yes")

    def test_agentfabric_member_read(self):
        member_id = os.environ.get("AZURE_TEST_AGENTFABRIC_MEMBER_ID") if self.is_live else (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/clitestafmember000001/providers/Microsoft.NetworkSecurity"
            "/agentFabrics/cliaf000002/members/cliafmember000003"
        )
        if not member_id:
            self.skipTest("Set AZURE_TEST_AGENTFABRIC_MEMBER_ID to an existing member for read-only live tests.")
        resource = parse_resource_id(member_id)
        self.assertEqual(resource.get("namespace", "").lower(), "microsoft.networksecurity")
        self.assertEqual(resource.get("type", "").lower(), "agentfabrics")
        self.assertEqual(resource.get("child_type_1", "").lower(), "members")
        self.kwargs.update({
            "subscription": resource["subscription"],
            "rg": resource["resource_group"],
            "fabric": resource["name"],
            "member": resource["child_name_1"],
        })
        self.cmd(
            "agentfabric member wait --subscription {subscription} -g {rg} "
            "--fabric-name {fabric} -n {member} --created --timeout 30"
        )
        self.cmd(
            "agentfabric member show --subscription {subscription} -g {rg} --fabric-name {fabric} -n {member}",
            checks=[self.check("name", "{member}")],
        )
        self.cmd(
            "agentfabric member list --subscription {subscription} -g {rg} --fabric-name {fabric}",
            checks=[self.check("[?name=='{member}'] | length(@)", 1)],
        )

    @ResourceGroupPreparer(name_prefix="clitestafaks", location=LOCATION, random_name_length=24)
    def test_agentfabric_aks_lifecycle(self, resource_group):
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliaf", length=24),
            "aks": self.create_random_name(prefix="cliafaks", length=24),
            "association": self.create_random_name(prefix="cliafassoc", length=24),
            "location": LOCATION,
        })
        # Pin prerequisite requests to the real recording, independent of core CLI defaults.
        with patch(
            "azure.cli.command_modules.acs._client_factory.get_container_service_client",
            self._aks_prerequisite_client,
        ), ExitStack() as cleanup:
            self._exercise_aks_lifecycle(cleanup)

    def test_agentfabric_egress_trust_bundle_list(self):
        recorded_group = "clitestafetblist000001"
        recorded_fabric = "cliafetb000002"
        fabric_id = os.environ.get("AZURE_TEST_AGENTFABRIC_FABRIC_ID") if self.is_live else (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            f"/resourceGroups/{recorded_group}/providers/Microsoft.NetworkSecurity"
            f"/agentFabrics/{recorded_fabric}"
        )
        if not fabric_id:
            self.skipTest("Set AZURE_TEST_AGENTFABRIC_FABRIC_ID to an existing fabric for read-only live tests.")
        resource = parse_resource_id(fabric_id)
        self.assertEqual(resource.get("namespace", "").lower(), "microsoft.networksecurity")
        self.assertEqual(resource.get("type", "").lower(), "agentfabrics")
        self.assertNotIn("child_type_1", resource)
        self.name_replacer.register_name_pair(resource["resource_group"], recorded_group)
        self.name_replacer.register_name_pair(resource["name"], recorded_fabric)
        self.kwargs.update({
            "subscription": resource["subscription"],
            "rg": resource["resource_group"],
            "fabric": resource["name"],
        })
        bundles = self.cmd(
            "agentfabric egress-trust-bundle list --subscription {subscription} -g {rg} --fabric-name {fabric}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].name", "default"),
                self.check("[0].type", "Microsoft.NetworkSecurity/agentFabrics/egressTrustBundles", case_sensitive=False),
            ],
        ).get_output_in_json()
        bundle = self.cmd(
            "agentfabric egress-trust-bundle show --subscription {subscription} -g {rg} --fabric-name {fabric}",
            checks=[self.check("name", "default")],
        ).get_output_in_json()
        self.assertEqual(bundles[0]["id"].lower(), bundle["id"].lower())
        self.assertEqual(bundle["id"].lower(), (fabric_id.rstrip("/") + "/egressTrustBundles/default").lower())
        self.assertGreater(len(bundles[0]["properties"]["certificates"]), 0)
        self.assertGreater(len(bundle["properties"]["certificates"]), 0)

    @staticmethod
    def _aks_prerequisite_client(cli_ctx, subscription_id=None):
        return get_mgmt_service_client(
            cli_ctx, ResourceType.MGMT_CONTAINERSERVICE,
            subscription_id=subscription_id, api_version="2026-06-01"
        )

    def _exercise_aks_lifecycle(self, cleanup):
        self.cmd(
            "agentfabric create -g {rg} -n {fabric} -l {location} --identity type=SystemAssigned"
        )
        cleanup.callback(self.cmd, "agentfabric wait -g {rg} -n {fabric} --deleted")
        cleanup.callback(self.cmd, "agentfabric delete -g {rg} -n {fabric} --yes")
        cluster = self.cmd(
            "aks create -g {rg} -n {aks} -l {location} --node-count 1 "
            "--node-vm-size Standard_D2s_v5 --tier free --enable-managed-identity --enable-aad --no-ssh-key",
            checks=[self.check("provisioningState", "Succeeded")],
        ).get_output_in_json()
        self.kwargs["aks_id"] = cluster["id"]
        cleanup.callback(self.cmd, "aks delete -g {rg} -n {aks} --yes")
        cleanup.callback(
            self.cmd, "agentfabric aks wait -g {rg} --fabric-name {fabric} -n {association} --deleted"
        )
        cleanup.callback(
            self.cmd, "agentfabric aks detach -g {rg} --fabric-name {fabric} -n {association} --yes"
        )
        self.cmd(
            "agentfabric aks attach -g {rg} --fabric-name {fabric} -n {association} "
            "-l {location} --cluster-resource-id {aks_id} --sku Standard",
            checks=[
                self.check("name", "{association}"),
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.clusterResourceId", "{aks_id}", case_sensitive=False),
                self.check("properties.sku", "Standard"),
            ],
        )
        self.cmd("agentfabric aks wait -g {rg} --fabric-name {fabric} -n {association} --created")
        self.cmd("agentfabric aks show -g {rg} --fabric-name {fabric} -n {association}", checks=[
            self.check("properties.clusterResourceId", "{aks_id}", case_sensitive=False),
        ])
        self.cmd("agentfabric aks list -g {rg} --fabric-name {fabric}", checks=[
            self.check("[?name=='{association}'] | length(@)", 1),
        ])
        self.cmd(
            "agentfabric aks update -g {rg} --fabric-name {fabric} -n {association} --sku Premium --no-wait"
        )
        self.cmd("agentfabric aks wait -g {rg} --fabric-name {fabric} -n {association} --updated")
        self.cmd("agentfabric aks show -g {rg} --fabric-name {fabric} -n {association}", checks=[
            self.check("properties.sku", "Premium"),
        ])
