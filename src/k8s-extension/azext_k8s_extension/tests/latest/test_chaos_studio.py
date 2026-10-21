# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

import base64
import copy
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ServiceRequestError
from kubernetes.client.exceptions import ApiException
from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from azext_k8s_extension import custom
from azext_k8s_extension.partner_extensions.ChaosStudio import ChaosStudio, _ClusterClient
from azext_k8s_extension.vendored_sdks.models import Extension, PatchExtension

SUB = "00000000-0000-0000-0000-000000000001"
SUB2 = "00000000-0000-0000-0000-000000000006"
WORKSPACE = "/subscriptions/{}/resourceGroups/workspace/providers/Microsoft.Chaos/workspaces/test".format(SUB)
PRINCIPAL = "00000000-0000-0000-0000-000000000002"
TENANT = "00000000-0000-0000-0000-000000000003"
CLIENT = "00000000-0000-0000-0000-000000000004"
WORKSPACE_PRINCIPAL = "00000000-0000-0000-0000-000000000005"
CLUSTER = ChaosStudio._cluster_resource_id(SUB, "rg", "cluster")
LEGACY_ASSIGNMENT = CLUSTER + "/providers/Microsoft.Authorization/roleAssignments/04a346ed-1e6c-5aa1-bf46-98f14cee0bd5"
CONNECTION = "{}/connections/{}".format(
    WORKSPACE, ChaosStudio._recommended_connection_name(WORKSPACE, CLUSTER)
)
PREFIX = "azext_k8s_extension.partner_extensions.ChaosStudio."


class Arm:
    def __init__(self, events, subscription_id=SUB):
        self.subscription_id = subscription_id
        self.events = events
        self.endpoint = "https://dataplane.northeurope.chaos-test.azure.com"
        self.resources = {
            ChaosStudio._cluster_resource_id(subscription_id, "rg", "cluster"): {
                "location": "westus2", "properties": {
                    "securityProfile": {"workloadIdentity": {"enabled": True}},
                    "oidcIssuerProfile": {"enabled": True, "issuerURL": "https://issuer.test"},
                    "aadProfile": {"enableAzureRBAC": True},
                }},
            WORKSPACE: {"identity": {"type": "SystemAssigned", "principalId": WORKSPACE_PRINCIPAL}},
        }
        self.fail_connection = False
        self.lost_response = False
        self.fail_reads = set()

    def get(self, resource_id, *_args, allow_not_found=False):
        self.events.append(("arm-get", resource_id))
        if resource_id in self.fail_reads:
            error = AzureResponseError("Forbidden: AuthorizationFailed")
            error.status_code = 403
            raise error
        if resource_id not in self.resources and not allow_not_found:
            raise AzureResponseError("read failed")
        return copy.deepcopy(self.resources.get(resource_id))

    def put(self, resource_id, _api, _description, body):
        self.events.append(("arm-put", resource_id))
        if "/roleDefinitions/" in resource_id:
            raise AssertionError("The CLI must never provision role definitions.")
        if "/connections/" in resource_id:
            if self.fail_connection:
                raise AzureResponseError("grant publication failed")
            old = self.resources.get(resource_id)
            if old and any(old["properties"].get(k) != v for k, v in body["properties"].items()):
                raise AzureResponseError("immutable trust conflict")
            body = {"properties": dict(body["properties"], dataPlaneEndpoint=self.endpoint)}
        self.resources[resource_id] = copy.deepcopy(body)
        if "/connections/" in resource_id and self.lost_response:
            self.lost_response = False
            raise AzureResponseError("connection response lost")
        return copy.deepcopy(body)

    def delete(self, resource_id, *_args):
        self.events.append(("arm-delete", resource_id))
        self.resources.pop(resource_id, None)


class Poller:
    def __init__(self, client, stage):
        self.client, self.stage = client, stage

    def result(self):
        self.client.events.append(("wait", self.stage))
        self.client.extension.provisioning_state = "Succeeded"
        return self.client.extension


class Extensions:
    def __init__(self, events):
        self.events = events
        self.extension = None
        self._config = SimpleNamespace(polling_interval=0)
        self.next_states = []
        self.fail_after_create = False
        self.fail_after_update = False
        self.identity = {"principalId": PRINCIPAL, "tenantId": TENANT, "clientId": CLIENT}

    def get(self, *_args, **kwargs):
        self.events.append(("extension-get",))
        if self.extension is None:
            raise ResourceNotFoundError("not found")
        if self.next_states:
            self.extension.provisioning_state = self.next_states.pop(0)
        result = copy.deepcopy(self.extension)
        if "cls" in kwargs:
            return kwargs["cls"](SimpleNamespace(http_response=SimpleNamespace(headers={})), result, {})
        return result

    def begin_create(self, *_args):
        model = _args[-1]
        assert isinstance(model, Extension)
        assert model.configuration_settings["subscriber.enabled"] == "false"
        assert "subscriber.serverEndpoint" not in model.configuration_settings
        assert not any("Identity" in k or k.startswith("workloadIdentity.")
                       for k in model.configuration_settings if k != "workspaceManagedIdentity.objectId")
        self.events.append(("create", copy.deepcopy(model)))
        self.extension = Extension(dict(model.as_dict(), properties=dict(
            model.as_dict()["properties"], provisioningState="Creating",
            aksAssignedIdentity=self.identity,
        )))
        if self.fail_after_create:
            self.fail_after_create = False
            raise AzureResponseError("bootstrap response lost")
        return Poller(self, "bootstrap")

    def begin_update(self, *_args, **kwargs):
        model = _args[-1]
        assert isinstance(model, PatchExtension)
        assert self.extension.provisioning_state in ("Succeeded", "Failed")
        assert "configurationProtectedSettings" not in model.as_dict().get("properties", {})
        self.events.append(("update", copy.deepcopy(model)))
        if kwargs.get("polling") is False:
            self.events.append(("no-poll",))
        self.extension.configuration_settings = dict(model.configuration_settings)
        self.extension.provisioning_state = "Updating"
        if self.fail_after_update:
            self.fail_after_update = False
            raise AzureResponseError("activation response lost")
        return Poller(self, "activation")


class ChaosStudioTests(unittest.TestCase):
    def setUp(self):
        self.reset_resources()
        self.registration = patch(PREFIX + "cf_k8s_extension_types")
        factory = self.registration.start()
        self.addCleanup(self.registration.stop)
        self.versions = factory.return_value.cluster_list_versions
        self.versions.return_value = [SimpleNamespace(properties=SimpleNamespace(version="0.1.6"))]
        wait = patch(PREFIX + "LongRunningOperation", return_value=lambda poller: poller.result())
        wait.start()
        self.addCleanup(wait.stop)

    def reset_resources(self, subscription_id=SUB):
        self.events = []
        self.arm = Arm(self.events, subscription_id)
        self.client = Extensions(self.events)
        self.partner = ChaosStudio()
        self.partner._arm_client_factory = lambda _cmd: self.arm
        self.cluster = MagicMock()
        self.cluster.namespace.return_value = None
        self.partner._cluster_client_factory = lambda *_args: self.cluster
        self.cmd = SimpleNamespace(cli_ctx=SimpleNamespace())

    def prepare(self, **overrides):
        args = dict(
            cmd=self.cmd, client=self.client, resource_group_name="rg", cluster_name="cluster",
            name="chaos", cluster_type="managedClusters", cluster_rp="Microsoft.ContainerService",
            extension_type="Microsoft.ChaosStudio", scope="cluster", auto_upgrade_minor_version=None,
            auto_upgrade_mode=None, release_train=None, version=None, target_namespace=None,
            release_namespace=None, configuration_settings={"chaos-workspace-id": WORKSPACE},
            configuration_protected_settings=None, configuration_settings_file=None,
            configuration_protected_settings_file=None, plan_name=None, plan_publisher=None, plan_product=None,
        )
        args.update(overrides)
        return self.partner.Create(**args)[0]

    def run_install(self, no_wait=False, **overrides):
        return self.partner.Install(
            self.cmd, self.client, "rg", "Microsoft.ContainerService",
            "managedClusters", "cluster", "chaos", self.prepare(**overrides), no_wait,
        )

    def test_namespace_creation_input_new_and_preexisting(self):
        for current, expected in ((None, "true"), ({"metadata": {}}, "false")):
            with self.subTest(expected=expected):
                self.reset_resources()
                self.cluster.namespace.return_value = current
                self.run_install()
                create = next(event[1] for event in self.events if event[0] == "create")
                self.assertEqual(create.configuration_settings[ChaosStudio.NAMESPACE_CREATED_KEY], expected)
                self.cluster.namespace.assert_called_once_with("chaos-infrastructure")

    def test_namespace_access_failure_prevents_bootstrap_and_permission_writes(self):
        self.cluster.namespace.side_effect = AzureResponseError("namespace access forbidden")
        with self.assertRaisesRegex(AzureResponseError, "namespace access forbidden"):
            self.run_install()
        self.assertFalse(any(event[0] in ("create", "update", "arm-put") for event in self.events))
        self.cluster.close.assert_called_once()

    def test_resumed_creation_preserves_namespace_assertion(self):
        self.client.fail_after_create = True
        with self.assertRaises(AzureResponseError):
            self.run_install()
        self.cluster.namespace.reset_mock()
        self.cluster.namespace.return_value = {"metadata": {}}
        self.client.extension.provisioning_state = "Succeeded"
        final = self.run_install()
        self.assertEqual(final.configuration_settings[ChaosStudio.NAMESPACE_CREATED_KEY], "true")
        self.cluster.namespace.assert_not_called()

    def test_namespace_input_is_managed_in_public_and_protected_settings(self):
        for field in ("configuration_settings", "configuration_protected_settings"):
            values = {ChaosStudio.NAMESPACE_CREATED_KEY: "true"}
            if field == "configuration_settings":
                values["chaos-workspace-id"] = WORKSPACE
            with self.subTest(field=field), self.assertRaisesRegex(InvalidArgumentValueError, "managed"):
                self.prepare(**{field: values})
        self.run_install()
        with self.assertRaisesRegex(InvalidArgumentValueError, "managed"):
            self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                {ChaosStudio.NAMESPACE_CREATED_KEY: "true"}, {}, self.client.extension)

    def test_legacy_resume_does_not_adopt_namespace(self):
        self.run_install()
        self.client.extension.configuration_settings.pop(ChaosStudio.NAMESPACE_CREATED_KEY)
        self.client.extension.provisioning_state = "Failed"
        final = self.run_install()
        self.assertNotIn(ChaosStudio.NAMESPACE_CREATED_KEY, final.configuration_settings)

    def test_owned_namespace_cleanup_and_repeat(self):
        extension = self.owned_namespace_extension()
        namespace = {"metadata": {
            "uid": "namespace-uid", "resourceVersion": "17",
            "annotations": {ChaosStudio.NAMESPACE_OWNER: "chaos-infrastructure/chaos"},
        }}
        self.cluster.namespace.side_effect = [namespace, None]
        self.cluster.inventory.return_value = []
        for _ in range(2):
            self.partner.PostDelete(self.cmd, "rg", "cluster", "chaos", extension)
        self.cluster.request.assert_called_once_with(
            "DELETE", "/api/v1/namespaces/chaos-infrastructure",
            {"apiVersion": "v1", "kind": "DeleteOptions",
             "preconditions": {"uid": "namespace-uid", "resourceVersion": "17"}},
            allow_not_found=True,
        )
        self.cluster.wait_deleted.assert_called_once_with("chaos-infrastructure")

    def test_foreign_and_unmarked_namespaces_survive(self):
        for owner in (None, "chaos-infrastructure/other", "other/chaos"):
            with self.subTest(owner=owner):
                self.cluster.reset_mock()
                self.cluster.namespace.return_value = {"metadata": {"annotations": {
                    ChaosStudio.NAMESPACE_OWNER: owner,
                }}}
                self.partner.PostDelete(self.cmd, "rg", "cluster", "chaos", self.owned_namespace_extension())
                self.cluster.request.assert_not_called()
                self.cluster.inventory.assert_not_called()

    def test_remaining_customer_resources_and_runtime_state_are_reported(self):
        resources = [
            "chaosengines.litmuschaos.io/reservation", "configmaps/durable-broker-learned-keys",
            "secrets/customer", "widgets.example.com/customer",
        ]
        self.cluster.namespace.return_value = {"metadata": {"annotations": {
            ChaosStudio.NAMESPACE_OWNER: "chaos-infrastructure/chaos",
        }}}
        self.cluster.inventory.return_value = resources
        with patch(PREFIX + "logger") as log:
            self.partner.PostDelete(self.cmd, "rg", "cluster", "chaos", self.owned_namespace_extension())
        self.cluster.request.assert_not_called()
        self.assertEqual(log.warning.call_args.args[2], ", ".join(resources))

    def test_inventory_and_delete_failure_are_not_success(self):
        self.cluster.namespace.return_value = {"metadata": {
            "uid": "uid", "resourceVersion": "1", "annotations": {
                ChaosStudio.NAMESPACE_OWNER: "chaos-infrastructure/chaos",
            },
        }}
        for failure in ("inventory", "request", "wait_deleted"):
            with self.subTest(failure=failure):
                self.cluster.reset_mock(side_effect=True)
                self.cluster.inventory.return_value = []
                getattr(self.cluster, failure).side_effect = AzureResponseError("failed " + failure)
                with self.assertRaisesRegex(AzureResponseError, "failed " + failure):
                    self.partner.PostDelete(self.cmd, "rg", "cluster", "chaos", self.owned_namespace_extension())

    def owned_namespace_extension(self):
        extension = self.prepare()
        extension.configuration_settings[ChaosStudio.NAMESPACE_CREATED_KEY] = "true"
        return extension

    def test_namespace_marker_without_install_creation_assertion_is_not_adopted(self):
        self.cluster.namespace.return_value = {"metadata": {"annotations": {
            ChaosStudio.NAMESPACE_OWNER: "chaos-infrastructure/chaos",
        }}}
        for assertion in (None, "false"):
            with self.subTest(assertion=assertion):
                extension = self.prepare()
                if assertion is not None:
                    extension.configuration_settings[ChaosStudio.NAMESPACE_CREATED_KEY] = assertion
                self.partner.PostDelete(self.cmd, "rg", "cluster", "chaos", extension)
        self.cluster.namespace.assert_not_called()
        self.cluster.request.assert_not_called()

    def test_delete_dispatch_waits_before_post_delete(self):
        self.run_install()
        events = []
        poller = MagicMock()
        poller.result.side_effect = lambda: events.append("completed")
        with patch.object(self.partner, "Delete", side_effect=lambda *_: events.append("pre")), \
                patch.object(self.partner, "PostDelete", side_effect=lambda *_: events.append("post")), \
                patch("azext_k8s_extension.custom.ExtensionFactory", return_value=self.partner), \
                patch.object(self.client, "begin_delete", create=True, return_value=poller), \
                patch("azext_k8s_extension.custom.LongRunningOperation",
                      return_value=lambda result: result.result()):
            custom.delete_k8s_extension(self.cmd, self.client, "rg", "cluster", "chaos",
                                        "managedClusters", yes=True)
        self.assertEqual(events, ["pre", "completed", "post"])

    def test_failed_no_wait_and_force_delete_never_run_namespace_cleanup(self):
        self.run_install()
        for mode in ("begin-failed", "wait-failed", "no-wait", "force"):
            with self.subTest(mode=mode), patch.object(self.partner, "Delete"), \
                    patch.object(self.partner, "PostDelete") as post, \
                    patch("azext_k8s_extension.custom.ExtensionFactory", return_value=self.partner), \
                    patch.object(self.client, "begin_delete", create=True) as begin, \
                    patch("azext_k8s_extension.custom.LongRunningOperation",
                          return_value=lambda result: result.result()):
                if mode == "begin-failed":
                    begin.side_effect = AzureResponseError("delete failed")
                if mode == "wait-failed":
                    begin.return_value.result.side_effect = AzureResponseError("delete failed")
                if mode.endswith("failed"):
                    with self.assertRaisesRegex(AzureResponseError, "delete failed"):
                        custom.delete_k8s_extension(self.cmd, self.client, "rg", "cluster", "chaos",
                                                   "managedClusters", yes=True)
                else:
                    custom.delete_k8s_extension(self.cmd, self.client, "rg", "cluster", "chaos",
                                               "managedClusters", yes=True,
                                               no_wait=mode == "no-wait", force=mode == "force")
                post.assert_not_called()

    def test_missing_extension_is_idempotent_but_forbidden_read_is_failure(self):
        for status in (404, 403):
            error = HttpResponseError("extension read failed")
            error.status_code = status
            with self.subTest(status=status), patch.object(self.client, "get", side_effect=error), \
                    patch("azext_k8s_extension.custom.ExtensionFactory") as factory:
                if status == 404:
                    self.assertIsNone(custom.delete_k8s_extension(
                        self.cmd, self.client, "rg", "cluster", "chaos", "managedClusters", yes=True
                    ))
                else:
                    with self.assertRaises(HttpResponseError):
                        custom.delete_k8s_extension(
                            self.cmd, self.client, "rg", "cluster", "chaos", "managedClusters", yes=True
                        )
                factory.assert_not_called()

    def test_stages_use_real_identity_and_returned_cross_region_endpoint(self):
        for zone in ("chaos-test.azure.com", "chaos-prod.azure.com"):
            with self.subTest(zone=zone):
                self.reset_resources()
                self.arm.endpoint = "https://dataplane.northeurope." + zone
                result = self.run_install()
                self.assertEqual(result.configuration_settings["subscriber.serverEndpoint"], self.arm.endpoint)
                events = [event[0:2] for event in self.events]
                bootstrap_wait = events.index(("wait", "bootstrap"))
                connection_write = events.index(("arm-put", CONNECTION))
                activation = next(i for i, event in enumerate(events) if event[0] == "update")
                self.assertLess(bootstrap_wait, connection_write)
                self.assertLess(connection_write, activation)
                self.assertIn(("wait", "activation"), self.events)
                self.assertEqual(self.arm.resources[CONNECTION]["properties"]["principalId"], PRINCIPAL)
                self.assertNotEqual(PRINCIPAL, CLIENT)
                self.assertFalse(any("userAssignedIdentities" in str(e) or "federatedIdentityCredentials" in str(e)
                                     for e in self.events))

    def test_no_wait_waits_bootstrap_only(self):
        result = self.run_install(no_wait=True)
        self.assertIsInstance(result, Poller)
        self.assertIn(("wait", "bootstrap"), self.events)
        self.assertNotIn(("wait", "activation"), self.events)
        self.assertIn(("no-poll",), self.events)
        self.assertIn(CONNECTION, self.arm.resources)

    def test_actual_command_dispatch_and_other_partner_path(self):
        actual_factory = custom.ExtensionFactory

        def factory(name):
            partner = actual_factory(name)
            if isinstance(partner, ChaosStudio):
                partner._arm_client_factory = lambda _cmd: self.arm
                partner._cluster_client_factory = lambda *_args: self.cluster
            return partner

        with patch.object(custom, "ExtensionFactory", side_effect=factory), \
                patch.object(custom, "validate_cc_registration"), \
                patch.object(custom, "is_dogfood_cluster", return_value=False), \
                patch.object(custom, "__create_identity", return_value=(None, None)) as identity:
            result = custom.create_k8s_extension(
                self.cmd, self.client, "rg", "cluster", "chaos",
                "managedClusters", "Microsoft.ChaosStudio",
                configuration_settings=[{"chaos-workspace-id": WORKSPACE}],
            )
            self.assertEqual(result.configuration_settings["subscriber.enabled"], "true")
            identity.assert_not_called()
            self.assertEqual([e[0] for e in self.events if e[0] in ("create", "update")],
                             ["create", "update"])
            with patch.object(self.client, "begin_create", return_value="ordinary") as create:
                result = custom.create_k8s_extension(
                    self.cmd, self.client, "rg", "cluster", "other",
                    "managedClusters", "Other.Partner", scope="cluster", release_namespace="other",
                )
                self.assertEqual(result, "ordinary")
                create.assert_called_once()

    def test_pending_activation_no_wait_observes_without_mutation(self):
        self.run_install(no_wait=True)
        self.events.clear()
        result = self.run_install(no_wait=True)
        self.assertEqual(result.provisioning_state, "Updating")
        self.assertFalse(any(e[0] in ("create", "update", "arm-put", "wait") for e in self.events))

    def test_failed_or_canceled_bootstrap_retries_on_explicit_rerun(self):
        for state in ("Failed", "Canceled"):
            with self.subTest(state=state):
                self.reset_resources()
                self.client.fail_after_create = True
                with self.assertRaises(AzureResponseError):
                    self.run_install()
                self.client.extension.provisioning_state = state
                self.events.clear()
                self.run_install()
                self.assertEqual(sum(e[0] == "create" for e in self.events), 1)

    def test_unknown_state_and_connection_conflict_fail_without_writes(self):
        self.run_install()
        self.client.extension.provisioning_state = "Deleting"
        self.events.clear()
        with self.assertRaisesRegex(AzureResponseError, "state conflicts"):
            self.run_install(no_wait=True)
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))
        self.client.extension.provisioning_state = "Succeeded"
        self.arm.resources[CONNECTION]["properties"]["principalId"] = CLIENT
        with self.assertRaises(AzureResponseError):
            self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_bad_endpoint_never_activates(self):
        for endpoint in ("", "http://dataplane.test", "https://user@host.test", "not-a-url"):
            with self.subTest(endpoint=endpoint):
                self.reset_resources()
                self.arm.endpoint = endpoint
                with self.assertRaises(AzureResponseError):
                    self.run_install()
                self.assertFalse(any(e[0] in ("update", "arm-delete") for e in self.events))

    def test_inspection_error_does_not_become_absent_extension(self):
        for error in (AzureResponseError("access denied"), ServiceRequestError("connection lost")):
            with self.subTest(error=error), patch.object(self.client, "get", side_effect=error):
                with self.assertRaisesRegex(AzureResponseError, "inspection.*retained"):
                    self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_update_preserves_settings_and_workspace_permissions(self):
        self.run_install(configuration_settings={
            "chaos-workspace-id": WORKSPACE, "experiments.stressToolsImage": "test.invalid/image:0",
        })
        self.events.clear()
        update = self.partner.Update(
            self.cmd, "rg", "cluster", None, None, None, None,
            {"operator.logLevel": "debug"}, {}, self.client.extension,
        )
        self.assertEqual(update.configuration_settings["subscriber.enabled"], "true")
        self.assertEqual(update.configuration_settings["subscriber.serverEndpoint"], self.arm.endpoint)
        self.assertEqual(update.configuration_settings["experiments.stressToolsImage"], "test.invalid/image:0")
        self.assertEqual(update.configuration_settings["workspaceManagedIdentity.objectId"], WORKSPACE_PRINCIPAL)
        self.assertFalse(any(e[0] in ("arm-put", "arm-delete") for e in self.events))
        for changes in ({"chaos-workspace-id": WORKSPACE + "-other"}, {"namespace": "different"},
                        {"subscriber.enabled": "false"}):
            with self.subTest(changes=changes), self.assertRaises(InvalidArgumentValueError):
                self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                    changes, {}, self.client.extension)

    def test_protected_settings_only_sent_at_bootstrap(self):
        self.run_install(configuration_protected_settings={"custom.secret": "synthetic"})
        create = next(e[1] for e in self.events if e[0] == "create")
        update = next(e[1] for e in self.events if e[0] == "update")
        self.assertEqual(create.configuration_protected_settings, {"custom.secret": "synthetic"})
        self.assertNotIn("configurationProtectedSettings", update.as_dict()["properties"])

    @staticmethod
    def role_id(subscription_id, guid):
        return "/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/{}".format(
            subscription_id, guid)

    def assigned_role(self):
        assignment = next(v for k, v in self.arm.resources.items() if "/roleAssignments/" in k)
        return assignment["properties"]["roleDefinitionId"]

    def test_new_installs_assign_builtin_without_custom_role_reads_or_writes(self):
        for subscription in (SUB, SUB2):
            with self.subTest(subscription=subscription):
                self.reset_resources(subscription)
                self.run_install()
                self.assertEqual(self.assigned_role(), self.role_id(
                    subscription, "681440c1-3630-4424-a530-0305ac721cfd"))
                self.assertFalse(any("/roleDefinitions/" in event[1]
                                     for event in self.events if event[0].startswith("arm-")))

    def test_existing_installs_add_builtin_and_preserve_legacy_until_delete(self):
        for mode in ("create", "update"):
            for legacy, guid in (
                ("fixed", "f8c5a7b1-8383-51b3-8d63-bcc642505edd"),
                ("subscription", "1a5f27eb-d6e5-52b5-bf86-2d6d80133664"),
                ("explicit", "11111111-2222-3333-4444-555555555555"),
            ):
                with self.subTest(mode=mode, legacy=legacy):
                    self.reset_resources()
                    self.run_install()
                    builtin_assignment = next(key for key in self.arm.resources if "/roleAssignments/" in key)
                    role_id = self.role_id(SUB, guid)
                    original_role = {"properties": {"type": "CustomRole", "permissions": []}}
                    self.arm.resources[role_id] = copy.deepcopy(original_role)
                    self.arm.resources[LEGACY_ASSIGNMENT] = copy.deepcopy(self.arm.resources.pop(builtin_assignment))
                    self.arm.resources[LEGACY_ASSIGNMENT]["properties"]["roleDefinitionId"] = role_id
                    if legacy == "explicit":
                        self.client.extension.configuration_settings[ChaosStudio.EXISTING_ROLE_KEY] = role_id
                    self.events.clear()
                    if mode == "create":
                        self.run_install()
                    else:
                        self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                            {}, {}, self.client.extension)
                    self.assertEqual(self.arm.resources[builtin_assignment]["properties"]["roleDefinitionId"],
                                     self.role_id(SUB, "681440c1-3630-4424-a530-0305ac721cfd"))
                    self.assertIn(LEGACY_ASSIGNMENT, self.arm.resources)
                    self.assertFalse(any(e[0] == "arm-delete" for e in self.events))
                    with patch("azext_k8s_extension.partner_extensions.DefaultExtension.DefaultExtension.Delete"):
                        self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                            "managedClusters", "Microsoft.ContainerService", True)
                    self.assertNotIn(builtin_assignment, self.arm.resources)
                    self.assertNotIn(LEGACY_ASSIGNMENT, self.arm.resources)
                    self.assertEqual(self.arm.resources[role_id], original_role)

    def test_delete_preserves_foreign_assignments_at_both_deterministic_ids(self):
        for legacy in (False, True):
            for foreign in ("role", "description"):
                with self.subTest(legacy=legacy, foreign=foreign):
                    self.reset_resources()
                    self.run_install()
                    builtin_assignment = next(key for key in self.arm.resources if "/roleAssignments/" in key)
                    assignment_id = LEGACY_ASSIGNMENT if legacy else builtin_assignment
                    assignment = copy.deepcopy(self.arm.resources[builtin_assignment])
                    if foreign == "role":
                        assignment["properties"]["roleDefinitionId"] = self.role_id(
                            SUB, "11111111-2222-3333-4444-555555555555")
                    else:
                        assignment["properties"]["description"] = "Customer-owned"
                    self.arm.resources[assignment_id] = copy.deepcopy(assignment)
                    with patch("azext_k8s_extension.partner_extensions.DefaultExtension.DefaultExtension.Delete"):
                        self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                            "managedClusters", "Microsoft.ContainerService", True)
                    self.assertEqual(self.arm.resources[assignment_id], assignment)

    def test_conflicting_workspace_assignment_is_not_overwritten(self):
        self.run_install()
        assignment_id = next(key for key in self.arm.resources if "/roleAssignments/" in key)
        self.arm.resources[assignment_id]["properties"]["principalId"] = CLIENT
        self.client.extension.provisioning_state = "Failed"
        self.events.clear()
        with self.assertRaises(AzureResponseError):
            self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put", "arm-delete") for e in self.events))

    def test_delete_conflict_stops_before_cleanup_and_retry_is_safe(self):
        self.run_install()
        self.arm.resources[CONNECTION]["properties"]["principalId"] = CLIENT
        self.events.clear()
        with patch("azext_k8s_extension.partner_extensions.DefaultExtension.DefaultExtension.Delete"):
            with self.assertRaises(InvalidArgumentValueError):
                self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                    "managedClusters", "Microsoft.ContainerService", True)
            self.assertFalse(any(e[0] == "arm-delete" for e in self.events))
            self.arm.resources[CONNECTION]["properties"]["principalId"] = PRINCIPAL
            for _ in range(2):
                self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                    "managedClusters", "Microsoft.ContainerService", True)
        self.assertEqual(sum(e == ("arm-delete", CONNECTION) for e in self.events), 1)

    def test_active_rerun_does_not_mutate(self):
        self.run_install()
        self.events.clear()
        self.run_install()
        self.assertFalse(any(e[0] in ("arm-put", "create", "update") for e in self.events))

    def test_resume_after_lost_connection_response(self):
        self.arm.lost_response = True
        with self.assertRaisesRegex(AzureResponseError, "connection.*retained"):
            self.run_install()
        self.events.clear()
        self.run_install()
        self.assertFalse(any(e[0] == "create" for e in self.events))
        self.assertTrue(any(e[0] == "update" for e in self.events))

    def test_resume_pending_bootstrap_without_second_put(self):
        self.client.fail_after_create = True
        with self.assertRaises(AzureResponseError):
            self.run_install()
        self.events.clear()
        self.client.next_states = ["Creating", "Creating", "Succeeded"]
        self.run_install()
        self.assertFalse(any(e[0] == "create" for e in self.events))

    def test_resume_pending_activation_without_reset(self):
        self.client.fail_after_update = True
        with self.assertRaises(AzureResponseError):
            self.run_install()
        self.events.clear()
        self.client.next_states = ["Updating", "Succeeded"]
        self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_missing_platform_identity_and_connection_failure_prevent_activation(self):
        self.client.identity = {}
        with self.assertRaisesRegex(AzureResponseError, "aksAssignedIdentity"):
            self.run_install()
        self.assertNotIn(CONNECTION, self.arm.resources)
        self.assertFalse(any(e[0] == "update" for e in self.events))

    def test_publication_failure_retains_bootstrap_and_permissions(self):
        self.arm.fail_connection = True
        with self.assertRaisesRegex(AzureResponseError, "grant publication"):
            self.run_install()
        self.assertEqual(self.client.extension.configuration_settings["subscriber.enabled"], "false")
        self.assertFalse(any(e[0] in ("update", "arm-delete") for e in self.events))

    def test_failed_activation_can_retry_without_bootstrap(self):
        self.run_install()
        self.client.extension.provisioning_state = "Failed"
        self.events.clear()
        self.run_install()
        self.assertFalse(any(e[0] == "create" for e in self.events))
        self.assertTrue(any(e[0] == "update" for e in self.events))

    def test_endpoint_mismatch_fails_before_writes(self):
        self.run_install()
        self.arm.resources[CONNECTION]["properties"]["dataPlaneEndpoint"] = "https://different.test"
        self.events.clear()
        with self.assertRaisesRegex(AzureResponseError, "conflicts"):
            self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def registered(self, *versions):
        self.versions.return_value = [SimpleNamespace(properties=SimpleNamespace(version=v)) for v in versions]

    def test_unregistered_version_rejected_before_writes(self):
        self.registered("0.1.6")
        with self.assertRaisesRegex(AzureResponseError, "not registered"):
            self.run_install(version="0.1.3")
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_omitted_version_resolves_to_latest_registered(self):
        self.registered("0.2.10")
        extension = self.prepare()
        self.assertEqual(extension.version, "0.2.10")
        self.assertIsNone(extension.release_train)
        self.assertFalse(extension.auto_upgrade_minor_version)
        self.versions.assert_called_with("rg", "Microsoft.ContainerService", "managedClusters", "cluster",
                                         "Microsoft.ChaosStudio", release_train=None, show_latest=True)
        self.registered()
        with self.assertRaisesRegex(InvalidArgumentValueError, "No Microsoft.ChaosStudio version"):
            self.prepare()

    def test_create_update_delete_at_registered_non_pinned_version(self):
        self.registered("0.1.6", "0.2.0", "0.3.0")
        result = self.run_install(version="0.2.0")
        self.assertEqual(result.version, "0.2.0")
        create = next(e[1] for e in self.events if e[0] == "create")
        self.assertEqual(create.version, "0.2.0")
        update = self.partner.Update(self.cmd, "rg", "cluster", None, None, None, "0.3.0",
                                     {}, {}, self.client.extension)
        self.assertEqual(update.version, "0.3.0")
        update = self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                     {}, {}, self.client.extension)
        self.assertEqual(update.version, "0.2.0")
        self.events.clear()
        with patch("azext_k8s_extension.partner_extensions.DefaultExtension.DefaultExtension.Delete"):
            self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                "managedClusters", "Microsoft.ContainerService", True)
        self.assertIn(("arm-delete", CONNECTION), [e[0:2] for e in self.events])

    def test_resume_rejects_version_mismatch(self):
        self.registered("0.2.0", "0.3.0")
        self.client.fail_after_create = True
        with self.assertRaises(AzureResponseError):
            self.run_install(version="0.2.0")
        self.events.clear()
        with self.assertRaisesRegex(AzureResponseError, "version or state conflicts"):
            self.run_install(version="0.3.0")
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_customer_cannot_override_stage_identity_or_endpoint(self):
        for key in ChaosStudio.MANAGED_KEYS:
            with self.subTest(key=key), self.assertRaises(InvalidArgumentValueError):
                self.prepare(configuration_settings={"chaos-workspace-id": WORKSPACE, key: "override"})

    def test_prerequisite_failure_precedes_writes(self):
        self.arm.resources[CLUSTER]["properties"]["aadProfile"]["enableAzureRBAC"] = False
        with self.assertRaisesRegex(AzureResponseError, "Azure RBAC"):
            self.run_install()
        self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_delete_only_owned_connection_and_workspace_permissions(self):
        self.run_install()
        self.events.clear()
        with patch("azext_k8s_extension.partner_extensions.DefaultExtension.DefaultExtension.Delete"):
            self.partner.Delete(self.cmd, self.client, "rg", "cluster", "chaos",
                                "managedClusters", "Microsoft.ContainerService", True)
        deletes = [e[1] for e in self.events if e[0] == "arm-delete"]
        self.assertEqual(deletes[0], CONNECTION)
        self.assertEqual(len(deletes), 2)
        self.assertIn("roleAssignments", deletes[1])

    SAFEGUARDS = CLUSTER + "/providers/Microsoft.ContainerService/deploymentSafeguards/default"

    def set_safeguards(self, level, excluded=None, system_excluded=None):
        properties = {"level": level}
        if excluded is not None:
            properties["excludedNamespaces"] = excluded
        if system_excluded is not None:
            properties["systemExcludedNamespaces"] = system_excluded
        self.arm.resources[self.SAFEGUARDS] = {"properties": properties}

    def daemon_settings(self):
        create = next(e[1] for e in self.events if e[0] == "create")
        update = next(e[1] for e in self.events if e[0] == "update")
        return (create.configuration_settings["chaosDaemon.enabled"],
                update.configuration_settings["chaosDaemon.enabled"])

    def test_safeguards_enforce_without_exclusion_skips_daemon_before_bootstrap(self):
        self.set_safeguards("Enforce", excluded=["other"], system_excluded=["kube-system"])
        with patch(PREFIX + "logger") as log:
            result = self.run_install()
        self.assertEqual(self.daemon_settings(), ("false", "false"))
        self.assertEqual(result.configuration_settings["chaosDaemon.enabled"], "false")
        events = [e[0:2] for e in self.events]
        self.assertLess(events.index(("arm-get", self.SAFEGUARDS)),
                        next(i for i, e in enumerate(self.events) if e[0] == "create"))
        call = log.warning.call_args_list[0]
        warning = call.args[0] % call.args[1:]
        for text in ("'chaos-infrastructure'", "PodNetworkLatency and PodNetworkLoss",
                     "PodDelete, PodCpuHog and PodMemoryHog still work", "az k8s-extension update"):
            self.assertIn(text, warning)

    def test_safeguards_exclusion_or_warn_or_absent_keeps_daemon(self):
        cases = {
            "customer exclusion": dict(level="Enforce", excluded=["chaos-infrastructure"]),
            "system exclusion": dict(level="Enforce", system_excluded=["chaos-infrastructure"]),
            "warn": dict(level="Warn"),
            "not configured": None,
        }
        for name, safeguards in cases.items():
            with self.subTest(name):
                self.reset_resources()
                if safeguards:
                    self.set_safeguards(**safeguards)
                self.run_install()
                self.assertEqual(self.daemon_settings(), ("true", "true"))

    def test_safeguards_uses_custom_release_namespace(self):
        self.set_safeguards("Enforce", excluded=["chaos-infrastructure"])
        self.run_install(release_namespace="custom-chaos")
        self.assertEqual(self.daemon_settings(), ("false", "false"))
        self.reset_resources()
        self.set_safeguards("Enforce", excluded=["custom-chaos"])
        self.run_install(release_namespace="custom-chaos")
        self.assertEqual(self.daemon_settings(), ("true", "true"))

    def test_safeguards_read_failure_or_malformed_response_fails_before_writes(self):
        cases = {
            "forbidden": None,
            "unknown level": {"properties": {"level": "Audit"}},
            "missing properties": {},
            "malformed exclusions": {"properties": {"level": "Enforce", "excludedNamespaces": "chaos-infrastructure"}},
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.reset_resources()
                if body is None:
                    self.arm.fail_reads.add(self.SAFEGUARDS)
                else:
                    self.arm.resources[self.SAFEGUARDS] = body
                with self.assertRaises(AzureResponseError):
                    self.run_install()
                self.assertFalse(any(e[0] in ("create", "update", "arm-put") for e in self.events))

    def test_safeguards_forbidden_names_required_permission(self):
        self.arm.fail_reads.add(self.SAFEGUARDS)
        with self.assertRaises(AzureResponseError) as raised:
            self.run_install()
        self.assertIn("Microsoft.ContainerService/deploymentSafeguards/read", str(raised.exception))
        self.assertIn("Reader", str(raised.exception))

    def test_safeguards_daemon_setting_cannot_be_overridden(self):
        for value in ("true", "false"):
            with self.subTest(value=value), self.assertRaises(InvalidArgumentValueError):
                self.prepare(configuration_settings={"chaos-workspace-id": WORKSPACE, "chaosDaemon.enabled": value})
        self.set_safeguards("Enforce")
        self.run_install()
        with self.assertRaises(InvalidArgumentValueError):
            self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                {"chaosDaemon.enabled": "true"}, {}, self.client.extension)

    def test_safeguards_update_reevaluates_and_recovers(self):
        self.set_safeguards("Enforce")
        self.run_install()
        self.assertEqual(self.client.extension.configuration_settings["chaosDaemon.enabled"], "false")
        self.set_safeguards("Enforce", excluded=["chaos-infrastructure"])
        update = self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                     {}, {}, self.client.extension)
        self.assertEqual(update.configuration_settings["chaosDaemon.enabled"], "true")
        self.client.extension.configuration_settings = dict(update.configuration_settings)
        self.set_safeguards("Enforce")
        update = self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                     {}, {}, self.client.extension)
        self.assertEqual(update.configuration_settings["chaosDaemon.enabled"], "false")
        del self.arm.resources[self.SAFEGUARDS]
        update = self.partner.Update(self.cmd, "rg", "cluster", None, None, None, None,
                                     {}, {}, self.client.extension)
        self.assertEqual(update.configuration_settings["chaosDaemon.enabled"], "true")

    def test_workspace_identity_variants(self):
        self.assertEqual(ChaosStudio._workspace_principal_id(
            {"identity": {"type": "SystemAssigned", "principalId": PRINCIPAL}}), PRINCIPAL)
        with self.assertRaises(InvalidArgumentValueError):
            ChaosStudio._workspace_principal_id({"identity": {"type": "UserAssigned", "userAssignedIdentities": {}}})

    def test_connection_name_is_canonical(self):
        self.assertEqual(ChaosStudio._recommended_connection_name(WORKSPACE, CLUSTER),
                         ChaosStudio._recommended_connection_name(WORKSPACE.upper() + "/", CLUSTER.upper()))


class ClusterNamespaceTests(unittest.TestCase):
    def setUp(self):
        self.cluster = _ClusterClient.__new__(_ClusterClient)
        self.cluster.client = MagicMock()
        self.cluster.deadline = time.monotonic() + 210

    def test_target_user_credentials_not_current_context_or_admin(self):
        arm = MagicMock(subscription_id=SUB)
        arm.post.return_value = {"kubeconfigs": [{
            "value": base64.b64encode(b"apiVersion: v1\ncurrent-context: target\n").decode("ascii"),
        }]}
        with patch(PREFIX + "config.new_client_from_config_dict") as load:
            cluster = _ClusterClient(None, arm, "rg", "cluster")
        arm.post.assert_called_once_with(
            CLUSTER + "/listClusterUserCredential", ChaosStudio.AKS_API_VERSION,
            "AKS user credentials", query={"format": "exec"},
        )
        load.assert_called_once_with({"apiVersion": "v1", "current-context": "target"})
        cluster.close()
        load.return_value.close.assert_called_once()

    def test_only_404_is_absence(self):
        for status in (404, 403, 401, 500):
            self.cluster.client.call_api.side_effect = ApiException(status=status)
            if status == 404:
                self.assertIsNone(self.cluster.namespace("chaos"))
            else:
                with self.subTest(status=status), self.assertRaises(AzureResponseError):
                    self.cluster.namespace("chaos")
        self.cluster.client.call_api.side_effect = None
        self.cluster.client.call_api.return_value = {"metadata": {"name": "chaos"}}
        self.assertEqual(self.cluster.namespace("chaos")["metadata"]["name"], "chaos")

    def test_discovery_pagination_includes_secrets_configmaps_and_custom_kinds(self):
        def resource(name):
            return {"name": name, "namespaced": True, "verbs": ["list"]}

        responses = {
            "/api": {"versions": ["v1"]},
            "/apis": {"groups": [{"name": "example.com",
                                  "preferredVersion": {"groupVersion": "example.com/v1"},
                                  "versions": [{"groupVersion": "example.com/v1"},
                                               {"groupVersion": "example.com/v2"}]}]},
            "/api/v1": {"resources": [resource("secrets"), resource("configmaps"),
                                      resource("pods/status"),
                                      {"name": "bindings", "namespaced": True, "verbs": ["create"]}]},
            "/apis/example.com/v1": {"resources": [resource("widgets")]},
            "/apis/example.com/v2": {"resources": [resource("widgets"), resource("otherwidgets")]},
        }

        def request(_method, path):
            if path in responses:
                return responses[path]
            if "continue=next" in path:
                return {"items": [{"metadata": {"name": "second"}}], "metadata": {}}
            return {"items": [{"metadata": {"name": "first"}}], "metadata": {"continue": "next"}}

        self.cluster.request = MagicMock(side_effect=request)
        actual = self.cluster.inventory("chaos")
        self.assertEqual(actual, sorted([
            resource + "/" + name
            for resource in ("secrets", "configmaps", "widgets.example.com", "otherwidgets.example.com")
            for name in ("first", "second")
        ]))
        calls = [call.args[1] for call in self.cluster.request.call_args_list]
        self.assertTrue(any("/secrets?limit=100&continue=next" in path for path in calls))
        self.assertFalse(any("pods/status?" in path for path in calls))
        self.assertFalse(any("/bindings?" in path for path in calls))
        self.assertFalse(any("/example.com/v2/namespaces/chaos/widgets?" in path for path in calls))

    def test_namespace_events_do_not_block_cleanup_but_customer_state_does(self):
        def resource(name):
            return {"name": name, "namespaced": True, "verbs": ["list"]}

        responses = {
            "/api": {"versions": ["v1"]},
            "/apis": {"groups": [
                {"name": group, "preferredVersion": {"groupVersion": group + "/v1"},
                 "versions": [{"groupVersion": group + "/v1"}]}
                for group in ("events.k8s.io", "example.com")
            ]},
            "/api/v1": {"resources": [resource("events"), resource("configmaps")]},
            "/apis/events.k8s.io/v1": {"resources": [resource("events")]},
            "/apis/example.com/v1": {"resources": [resource("events")]},
        }

        def request(_method, path):
            if path in responses:
                return responses[path]
            if "/configmaps?" in path:
                return {"items": [{"metadata": {"name": "durable-broker-learned-keys"}}]}
            return {"items": [{"metadata": {"name": "retained-event"}}]}

        self.cluster.request = MagicMock(side_effect=request)
        self.assertEqual(self.cluster.inventory("chaos"), [
            "configmaps/durable-broker-learned-keys", "events.example.com/retained-event",
        ])
        calls = [call.args[1] for call in self.cluster.request.call_args_list]
        self.assertTrue(any("/api/v1/namespaces/chaos/events?" in path for path in calls))
        self.assertTrue(any("/apis/events.k8s.io/v1/namespaces/chaos/events?" in path for path in calls))

    def test_readable_kind_without_list_is_not_treated_as_empty(self):
        self.cluster.request = MagicMock(side_effect=[
            {"versions": ["v1"]}, {"groups": []},
            {"resources": [{"name": "widgets", "namespaced": True, "verbs": ["get", "create"]}]},
        ])
        with self.assertRaisesRegex(AzureResponseError, "Cannot inventory"):
            self.cluster.inventory("chaos")

    def test_inventory_failure_never_proves_empty(self):
        responses = [
            {"versions": ["v1"]}, {"groups": []},
            {"resources": [{"name": "secrets", "namespaced": True, "verbs": ["list"]}]},
            AzureResponseError("secrets forbidden"),
        ]
        self.cluster.request = MagicMock(side_effect=responses)
        with self.assertRaisesRegex(AzureResponseError, "secrets forbidden"):
            self.cluster.inventory("chaos")
        self.assertEqual(self.cluster.request.call_count, 4)

    def test_controller_defaults_require_positive_unmodified_ownership(self):
        for kind, name in (("serviceaccounts", "default"), ("configmaps", "kube-root-ca.crt")):
            with self.subTest(kind=kind):
                obj = {"metadata": {"name": name, "managedFields": [{"manager": "kube-controller-manager"}]},
                       "data": {"ca.crt": "synthetic-ca"}}
                self.assertTrue(_ClusterClient._namespace_default("", kind, obj))
                changed = copy.deepcopy(obj)
                changed["metadata"]["managedFields"].append({"manager": "kubectl"})
                self.assertFalse(_ClusterClient._namespace_default("", kind, changed))
                changed["metadata"].pop("managedFields")
                self.assertEqual(_ClusterClient._namespace_default("", kind, changed), kind == "serviceaccounts")
                obj["metadata"]["finalizers"] = ["customer"]
                self.assertFalse(_ClusterClient._namespace_default("", kind, obj))
        secret = {"metadata": {"name": "default", "managedFields": [{"manager": "kube-controller-manager"}]}}
        self.assertFalse(_ClusterClient._namespace_default("", "secrets", secret))
        secret["data"] = {"ca.crt": "synthetic-ca", "customer": "preserve"}
        secret["metadata"]["name"] = "kube-root-ca.crt"
        self.assertFalse(_ClusterClient._namespace_default("", "configmaps", secret))
        for field, value in (("secrets", [{"name": "customer"}]),
                             ("imagePullSecrets", [{"name": "customer"}]),
                             ("automountServiceAccountToken", False)):
            service_account = {
                "metadata": {"name": "default", "managedFields": [{"manager": "kube-controller-manager"}]},
                field: value,
            }
            self.assertFalse(_ClusterClient._namespace_default("", "serviceaccounts", service_account))

    def test_aks_default_serviceaccount_without_managed_fields_preserves_customer_metadata(self):
        service_account = {"apiVersion": "v1", "kind": "ServiceAccount", "metadata": {"name": "default"}}
        self.assertTrue(_ClusterClient._namespace_default("", "serviceaccounts", service_account))
        for field, value in (("annotations", {"customer": "value"}), ("labels", {"customer": "value"}),
                             ("ownerReferences", [{"uid": "customer"}])):
            with self.subTest(field=field):
                changed = copy.deepcopy(service_account)
                changed["metadata"][field] = value
                self.assertFalse(_ClusterClient._namespace_default("", "serviceaccounts", changed))

    def test_deadline_is_explicit_failure_and_namespace_finalization_is_observed(self):
        self.cluster.deadline = 0
        with self.assertRaisesRegex(AzureResponseError, "budget"):
            self.cluster.namespace("chaos")
        self.cluster.client.call_api.assert_not_called()
        self.cluster.namespace = MagicMock(side_effect=[{"metadata": {"name": "chaos"}}, None])
        with patch(PREFIX + "time.sleep") as sleep:
            self.cluster.wait_deleted("chaos")
        self.assertEqual(self.cluster.namespace.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
