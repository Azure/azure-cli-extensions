# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import time
import unittest
from unittest import mock

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.core.util import send_raw_request
from azure.cli.testsdk.scenario_tests import RecordingProcessor

LOCATION = os.environ.get("AZURE_TEST_NEUROSHIELD_LOCATION", "eastus2")


class OperationStatusSignatureProcessor(RecordingProcessor):
    """Redact the signed query parameters on ARM async operation URLs."""
    _pattern = re.compile(r"([?&][tcsh]=)[^&\s\"']+")

    def process_request(self, request):
        request.uri = self._pattern.sub(r"\1REDACTED", request.uri)
        return request

    def process_response(self, response):
        headers = response["headers"]
        for key, values in headers.items():
            headers[key] = [self._pattern.sub(r"\1REDACTED", v) for v in values]
        return response


class NeuroshieldScenario(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[OperationStatusSignatureProcessor()])
    @ResourceGroupPreparer(name_prefix="cli_test_neuroshield", location=LOCATION)
    def test_neuroshield_scenario(self, resource_group):
        self.kwargs.update({
            "ns": self.create_random_name("ns", 12),
            "loc": LOCATION,
            "vm_prefix": f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}"
                         "/providers/Microsoft.Compute/virtualMachines",
            "uami": f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}"
                    "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/uami1",
        })

        self.cmd("neuroshield create -g {rg} -n {ns} --response-mode Manual --severity-threshold Medium "
                 "--description test --tags env=test", checks=[
                     self.check("name", "{ns}"),
                     self.check("properties.provisioningState", "Succeeded"),
                     self.check("properties.responseMode", "Manual"),
                     self.check("properties.severityThreshold", "Medium"),
                     self.check("tags.env", "test"),
                 ])
        self.cmd("neuroshield update -g {rg} -n {ns} --response-mode Auto --severity-threshold High", checks=[
            self.check("properties.responseMode", "Auto"),
            self.check("properties.severityThreshold", "High"),
            self.check("properties.description", "test"),
        ])
        self.cmd("neuroshield show -g {rg} -n {ns}", checks=[self.check("properties.responseMode", "Auto")])
        self.cmd("neuroshield list -g {rg}", checks=[self.check("length(@)", 1)])
        self.cmd("neuroshield list", checks=[self.check("length([?name=='{ns}'])", 1)])

        self.cmd("neuroshield summary show -g {rg} --neuroshield-name {ns}", checks=[
            self.check("name", "default"),
            self.check("properties.protectedCount", 0),
        ])
        self.cmd("neuroshield summary list -g {rg} --neuroshield-name {ns}", checks=[self.check("length(@)", 1)])
        self.cmd("neuroshield finding list -g {rg} --neuroshield-name {ns}", checks=[self.check("length(@)", 0)])
        self.cmd("neuroshield mitigation list -g {rg} --neuroshield-name {ns}", checks=[self.check("length(@)", 0)])

        # The service does not resolve the target VM or identities, so placeholders are enough.
        self.cmd("neuroshield protected-resource create -g {rg} --neuroshield-name {ns} -n vm-sys "
                 "--target-resource-id {vm_prefix}/vm-sys --target-identity \"{{type:SystemAssigned,"
                 "principal-id:11111111-1111-1111-1111-111111111111,"
                 "tenant-id:22222222-2222-2222-2222-222222222222}}\"", checks=[
                     self.check("properties.provisioningState", "Succeeded"),
                     self.check("properties.targetIdentity.type", "SystemAssigned"),
                     self.check("properties.targetIdentity.principalId", "11111111-1111-1111-1111-111111111111"),
                 ])
        self.cmd("neuroshield protected-resource create -g {rg} --neuroshield-name {ns} -n vm-ua "
                 "--target-resource-id {vm_prefix}/vm-ua --target-identity \"{{type:UserAssigned,"
                 "user-assigned-identities:{{{uami}:{{principal-id:33333333-3333-3333-3333-333333333333,"
                 "client-id:44444444-4444-4444-4444-444444444444}}}}}}\"", checks=[
                     self.check("properties.targetIdentity.type", "UserAssigned"),
                     self.check("length(properties.targetIdentity.userAssignedIdentities)", 1),
                 ])
        self.cmd("neuroshield protected-resource wait -g {rg} --neuroshield-name {ns} -n vm-ua --created")
        self.cmd("neuroshield protected-resource show -g {rg} --neuroshield-name {ns} -n vm-sys", checks=[
            self.check("name", "vm-sys"),
            self.check("properties.targetResourceId", "{vm_prefix}/vm-sys", case_sensitive=False),
        ])
        self.cmd("neuroshield protected-resource list -g {rg} --neuroshield-name {ns}",
                 checks=[self.check("length(@)", 2)])
        self.cmd("neuroshield protected-resource trigger-inventory-upload -g {rg} --neuroshield-name {ns} -n vm-sys",
                 checks=[self.exists("requestId")])
        self.cmd("neuroshield protected-resource finding list -g {rg} --neuroshield-name {ns} "
                 "--protected-resource vm-sys", checks=[self.check("length(@)", 0)])
        self.cmd("neuroshield protected-resource mitigation list -g {rg} --neuroshield-name {ns} "
                 "--protected-resource vm-sys", checks=[self.check("length(@)", 0)])

        self.cmd("neuroshield protected-resource delete -g {rg} --neuroshield-name {ns} -n vm-sys --yes")

        # CLI output does not expose the async operation id, so issue this delete directly to read the header.
        response = send_raw_request(
            self.cli_ctx, "DELETE",
            f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/"
            f"Microsoft.NetworkSecurity/neuroShields/{self.kwargs['ns']}/protectedResources/vm-ua"
            "?api-version=2026-10-01-preview")
        async_url = response.headers["Azure-AsyncOperation"]
        self.kwargs["op_id"] = re.search(r"neuroShieldOperationStatuses/([^?]+)", async_url).group(1)
        self.cmd("neuroshield protected-resource wait -g {rg} --neuroshield-name {ns} -n vm-ua --deleted")
        self.cmd("neuroshield operation-status show -l {loc} --operation-id {op_id}", checks=[
            self.check("name", "{op_id}"),
            self.check("status", "Succeeded"),
        ])
        self.cmd("neuroshield protected-resource list -g {rg} --neuroshield-name {ns}",
                 checks=[self.check("length(@)", 0)])
        self.cmd("neuroshield delete -g {rg} -n {ns} --yes")
        self.cmd("neuroshield list -g {rg}", checks=[self.check("length(@)", 0)])

    def _mitigation(self, name):
        return self.cmd("neuroshield protected-resource mitigation show -g {rg} --neuroshield-name {ns} "
                        "--protected-resource {pr} -n " + name).get_output_in_json()["properties"]

    def _wait_mitigation(self, name, done):
        for _ in range(40):
            status = self._mitigation(name)["status"]
            if status in done:
                return status
            if self.is_live:
                time.sleep(30)
        self.fail(f"mitigation {name} did not reach {done}")

    def _poll_settled(self, names):
        """Bounded poll until none of the mitigations can still run; returns the last seen properties."""
        for _ in range(40):
            props = {name: self._mitigation(name) for name in names}
            if _settled([p["status"] for p in props.values()]):
                break
            if self.is_live:
                time.sleep(30)
        return props

    def _rollback_succeeded(self, names):
        """Failure-safe cleanup: roll back every succeeded mitigation until none of them can still run.

        Rolling back one mitigation lets the next Queued one of the finding run, so repeat until nothing new
        succeeds; each mitigation is rolled back at most once, which bounds the loop.
        """
        attempted, errors = set(), []
        while True:
            props = self._poll_settled(names)
            todo = [n for n, p in props.items() if p["status"] == "Succeeded" and n not in attempted]
            if not todo:
                break
            for name in todo:
                attempted.add(name)
                if not props[name].get("isRollbackable"):
                    errors.append(f"{name} succeeded but is not rollbackable")
                    continue
                try:
                    self.cmd("neuroshield protected-resource mitigation rollback -g {rg} --neuroshield-name {ns} "
                             "--protected-resource {pr} --mitigation-id " + name)
                    status = self._wait_mitigation(name, ("RolledBack", "RollbackFailed"))
                    if status != "RolledBack":
                        errors.append(f"{name} rollback ended {status}")
                except Exception as ex:  # pylint: disable=broad-except
                    errors.append(f"{name} rollback raised {ex!r}")
        if not _settled(p["status"] for p in props.values()):
            errors.append(f"still running: {props}")
        if errors:
            raise AssertionError("mitigation cleanup failed: " + "; ".join(errors))

    # Findings are produced by the Neuron agent on a real VM, so these tests run against a
    # service-provided NeuroShield (Manual response mode) that already has findings.
    # Mitigations are one-shot, so a live run needs fresh AwaitingApproval mitigations.
    def _use_finding(self, pr, finding):
        self.kwargs.update({
            "rg": os.environ.get("AZURE_TEST_NEUROSHIELD_FINDING_RG", "satyaTestRG"),
            "ns": os.environ.get("AZURE_TEST_NEUROSHIELD_FINDING_NS", "ns-isolated-cuap-1113-8469"),
            "pr": pr,
            "finding": finding,
        })
        return "-g {rg} --neuroshield-name {ns} --protected-resource {pr}"

    def test_neuroshield_mitigation_execute(self):
        pr_args = self._use_finding("nsisolated11158469-2", "CVE-2026-78410-nsisolated11158469-2")
        self.kwargs["mitigation"] = "CVE-2026-78410-nsisolated11158469-2-deny-bind-and-cloned-mount-operations"

        self.cmd("neuroshield protected-resource finding show " + pr_args + " -n {finding}", checks=[
            self.check("name", "{finding}"),
            self.exists("properties.cveId"),
        ])
        self.cmd("neuroshield protected-resource mitigation show " + pr_args + " -n {mitigation}", checks=[
            self.check("properties.status", "AwaitingApproval"),
            self.check("properties.isRollbackable", True),
            self.check("properties.rank", 4),
        ])

        self.addCleanup(self._rollback_succeeded, [self.kwargs["mitigation"]])
        result = self.cmd("neuroshield protected-resource mitigation execute " + pr_args + " --mitigation-id {mitigation}",
                          checks=[self.check("name", "{mitigation}")]).get_output_in_json()
        self.assertNotEqual(result["properties"]["status"], "AwaitingApproval")
        self.assertEqual(self._wait_mitigation(self.kwargs["mitigation"], ("Succeeded", "Failed", "Skipped")),
                         "Succeeded")
        self.cmd("neuroshield protected-resource mitigation rollback " + pr_args + " --mitigation-id {mitigation}",
                 checks=[self.check("name", "{mitigation}")])
        self.assertEqual(self._wait_mitigation(self.kwargs["mitigation"], ("RolledBack", "RollbackFailed")),
                         "RolledBack")

    # Mitigating a finding approves all its AwaitingApproval mitigations; they run one at a time by rank.
    # Rollback then targets the succeeded one; cleanup handles whatever runs after it (see _settled).
    def test_neuroshield_finding_mitigation(self):
        pr_args = self._use_finding("nsisolated11158469-2", "CVE-2026-82049-nsisolated11158469-2")

        pending = [m["name"] for m in self.cmd("neuroshield protected-resource mitigation list " + pr_args)
                   .get_output_in_json()
                   if m["properties"]["findingId"].endswith("/" + self.kwargs["finding"])
                   and m["properties"]["status"] == "AwaitingApproval"]
        self.assertTrue(pending, "finding has no AwaitingApproval mitigations")
        self.addCleanup(self._rollback_succeeded, pending)

        queued = self.cmd("neuroshield protected-resource finding mitigate " + pr_args + " --finding-id {finding}",
                          checks=[self.check("length(value) > `0`", True)]).get_output_in_json()["value"]
        self.assertCountEqual([m["name"] for m in queued], pending)

        props = self._poll_settled(pending)
        statuses = {n: p["status"] for n, p in props.items()}
        self.assertTrue(_settled(statuses.values()), statuses)
        succeeded = [n for n, s in statuses.items() if s == "Succeeded"]
        self.assertTrue(succeeded, statuses)

        self.cmd("neuroshield protected-resource finding rollback " + pr_args + " --finding-id {finding}",
                 checks=[self.check("value[].name", succeeded)])
        self.assertEqual(self._wait_mitigation(succeeded[0], ("RolledBack", "RollbackFailed")), "RolledBack")


# Service behavior (NeuroShield team, verified live): mitigations of a finding run one at a time by rank.
# While one is Succeeded or Skipped, the remaining Queued ones do not run. A Failed one, or rolling back
# the Succeeded one, lets the next Queued mitigation run.
_DONE = {"AwaitingApproval", "Succeeded", "Failed", "Skipped", "RolledBack", "RollbackFailed"}
_BLOCKS_QUEUE = {"Succeeded", "Skipped"}


def _settled(statuses):
    statuses = list(statuses)
    blocked = bool(_BLOCKS_QUEUE.intersection(statuses))
    return all(s in _DONE or (s == "Queued" and blocked) for s in statuses)


class MitigationCleanupTest(unittest.TestCase):

    def test_cleanup_rolls_back_after_failure(self):
        finding = "/findings/CVE-2026-82049-nsisolated11158469-2"
        state = {"m1": "AwaitingApproval", "m2": "AwaitingApproval"}

        def cmd(command, checks=None):  # pylint: disable=unused-argument
            name = command.split()[-1]
            if "mitigation list" in command:
                body = [{"name": n, "properties": {"status": s, "findingId": finding}} for n, s in state.items()]
            elif "finding mitigate" in command:
                state.update(m1="Succeeded", m2="Queued")
                body = {"value": [{"name": n} for n in state]}
            elif "finding rollback" in command:
                raise AssertionError("simulated failure")
            elif "mitigation rollback" in command:
                state[name] = "RolledBack"
                state.update({n: "Succeeded" for n, s in state.items() if s == "Queued"})  # queue resumes
                body = {}
            else:
                body = {"properties": {"status": state[name], "isRollbackable": True}}
            return mock.Mock(get_output_in_json=lambda: body)

        test = NeuroshieldScenario("test_neuroshield_finding_mitigation")
        test.cmd = cmd
        with self.assertRaisesRegex(AssertionError, "simulated failure"):
            test.test_neuroshield_finding_mitigation()
        self.assertTrue(test.doCleanups())
        self.assertEqual(state, {"m1": "RolledBack", "m2": "RolledBack"})
