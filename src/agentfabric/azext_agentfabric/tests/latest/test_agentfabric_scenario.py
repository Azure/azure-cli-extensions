# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import unittest
from contextlib import ExitStack

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import RecordingProcessor


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
            self.cmd("agentfabric list", checks=[
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
            self.cmd("agentfabric policy-group list", checks=[
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
            # Collection GET currently fails with ResourceReadFailed in Central US EUAP.
        finally:
            self.cmd("agentfabric delete -g {rg} -n {fabric} --yes")

    @ResourceGroupPreparer(name_prefix="clitestafmember", location=LOCATION)
    def test_agentfabric_member_lifecycle(self, resource_group):
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliaf", length=24),
            "member": self.create_random_name(prefix="cliafmember", length=24),
            "location": LOCATION,
        })
        with ExitStack() as cleanup:
            self.cmd("agentfabric create -g {rg} -n {fabric} -l {location}")
            cleanup.callback(self.cmd, "agentfabric delete -g {rg} -n {fabric} --yes")
            cleanup.callback(
                self.cmd, "agentfabric member wait -g {rg} --fabric-name {fabric} -n {member} --deleted"
            )
            cleanup.callback(
                self.cmd, "agentfabric member delete -g {rg} --fabric-name {fabric} -n {member} --yes"
            )
            self.cmd(
                "agentfabric member create -g {rg} --fabric-name {fabric} -n {member} -l {location} "
                "--fqdn {member}.example.com",
                checks=[
                    self.check("name", "{member}"),
                    self.check("properties.provisioningState", "Succeeded"),
                ],
            )
            self.cmd("agentfabric member wait -g {rg} --fabric-name {fabric} -n {member} --created")
            self.cmd("agentfabric member show -g {rg} --fabric-name {fabric} -n {member}", checks=[
                self.check("properties.fqdn", "{member}.example.com"),
            ])
            self.cmd("agentfabric member list -g {rg} --fabric-name {fabric}", checks=[
                self.check("[?name=='{member}'] | length(@)", 1),
            ])
            self.cmd(
                "agentfabric member update -g {rg} --fabric-name {fabric} -n {member} "
                "--fqdn updated.example.com --tags stage=updated --no-wait"
            )
            self.cmd("agentfabric member wait -g {rg} --fabric-name {fabric} -n {member} --updated")
            self.cmd("agentfabric member show -g {rg} --fabric-name {fabric} -n {member}", checks=[
                self.check("properties.fqdn", "updated.example.com"),
                self.check("tags.stage", "updated"),
            ])

    @ResourceGroupPreparer(name_prefix="clitestafaks", location=LOCATION, random_name_length=24)
    def test_agentfabric_aks_lifecycle(self, resource_group):
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliaf", length=24),
            "aks": self.create_random_name(prefix="cliafaks", length=24),
            "association": self.create_random_name(prefix="cliafassoc", length=24),
            "location": LOCATION,
        })
        with ExitStack() as cleanup:
            self._exercise_aks_lifecycle(cleanup)

    @live_only()
    @ResourceGroupPreparer(name_prefix="clitestafetblist", location=LOCATION)
    def test_agentfabric_egress_trust_bundle_list(self, resource_group):
        # No successful recording yet: public collection GET returned 404 ResourceReadFailed.
        self.kwargs.update({
            "fabric": self.create_random_name(prefix="cliafetb", length=24),
            "location": LOCATION,
        })
        self.cmd("agentfabric create -g {rg} -n {fabric} -l {location}")
        try:
            self.cmd("agentfabric egress-trust-bundle list -g {rg} --fabric-name {fabric}", checks=[
                self.check("[?name=='default'] | length(@)", 1),
            ])
        finally:
            self.cmd("agentfabric delete -g {rg} -n {fabric} --yes")

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
