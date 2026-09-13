# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

import copy
import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from knack.util import CLIError

from azext_k8s_extension.partner_extensions.ChaosStudio import (
    ChaosStudio,
    _ArmClient,
)
from azext_k8s_extension.partner_extensions.DefaultExtension import (
    DefaultExtension,
)
from azext_k8s_extension.partner_extensions.PartnerExtensionModel import (
    PartnerExtensionModel,
)


SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000001"
RESOURCE_GROUP = "test-rg"
CLUSTER_NAME = "test-cluster"
WORKSPACE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000002/"
    "resourceGroups/workspace-rg/providers/Microsoft.Chaos/workspaces/test"
)
WORKSPACE_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000003"
ISSUER = "https://oidc.test/"
CLIENT_ID = "00000000-0000-0000-0000-000000000004"
TENANT_ID = "00000000-0000-0000-0000-000000000005"
SUBSCRIBER_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000006"
DATA_PLANE_ENDPOINT = "https://dataplane.westus2.chaos-test.azure.com"
EXAMPLE_WORKSPACE_ID = (
    "/subscriptions/6b052e15-03d3-4f17-b2e1-be7f07588291/"
    "resourceGroups/exampleRG/providers/Microsoft.Chaos/"
    "workspaces/exampleWorkspace"
)
EXAMPLE_CLUSTER_ID = (
    "/subscriptions/6b052e15-03d3-4f17-b2e1-be7f07588291/"
    "resourceGroups/exampleRG/providers/Microsoft.ContainerService/"
    "managedClusters/exampleCluster"
)


def _valid_cluster():
    return {
        "location": "westus2",
        "properties": {
            "securityProfile": {"workloadIdentity": {"enabled": True}},
            "oidcIssuerProfile": {
                "enabled": True,
                "issuerURL": ISSUER,
            },
            "aadProfile": {"enableAzureRBAC": True},
        },
    }


def _valid_workspace():
    return {
        "identity": {
            "type": "UserAssigned",
            "userAssignedIdentities": {
                "/subscriptions/x/resourceGroups/x/providers/"
                "Microsoft.ManagedIdentity/userAssignedIdentities/workspace": {
                    "clientId": "workspace-client",
                    "principalId": WORKSPACE_PRINCIPAL_ID,
                }
            },
        }
    }


class ControlledArmClient:
    def __init__(self, resources=None):
        self.subscription_id = SUBSCRIPTION_ID
        self.resources = {
            key.lower(): copy.deepcopy(value)
            for key, value in (resources or {}).items()
        }
        self.calls = []
        self.failures = {}
        self.delete_failures = {}

    @property
    def writes(self):
        return [call for call in self.calls if call[0] in ("PUT", "DELETE")]

    def get(self, resource_id, api_version, description, allow_not_found=False):
        self.calls.append(("GET", resource_id, api_version, description))
        if resource_id.lower() in self.failures:
            raise self.failures[resource_id.lower()]
        resource = self.resources.get(resource_id.lower())
        if resource is None and not allow_not_found:
            raise AzureResponseError(
                "Failed to GET {} '{}': not found".format(
                    description, resource_id
                )
            )
        return copy.deepcopy(resource)

    def put(self, resource_id, api_version, description, body):
        self.calls.append(
            ("PUT", resource_id, api_version, description, copy.deepcopy(body))
        )
        resource = copy.deepcopy(body)
        if "/providers/microsoft.chaos/workspaces/" in resource_id.lower() and (
            "/connections/" in resource_id.lower()
        ):
            existing = self.resources.get(resource_id.lower())
            if existing is not None:
                existing_properties = existing.get("properties") or {}
                request_properties = resource["properties"]
                if any(
                    str(existing_properties.get(key, "")).lower()
                    != str(value).lower()
                    for key, value in request_properties.items()
                ):
                    raise AzureResponseError(
                        "Failed to PUT Chaos Studio workspace connection "
                        "'{}': conflict".format(resource_id)
                    )
                return copy.deepcopy(existing)
            resource = {
                "name": resource_id.rsplit("/", 1)[-1],
                "properties": {
                    **resource["properties"],
                    "dataPlaneEndpoint": DATA_PLANE_ENDPOINT,
                },
            }
        elif (
            "/userassignedidentities/" in resource_id.lower()
            and "/federatedidentitycredentials/" not in resource_id.lower()
        ):
            resource["properties"] = {
                "clientId": CLIENT_ID,
                "principalId": SUBSCRIBER_PRINCIPAL_ID,
                "tenantId": TENANT_ID,
            }
        self.resources[resource_id.lower()] = resource
        return copy.deepcopy(resource)

    def delete(self, resource_id, api_version, description):
        self.calls.append(("DELETE", resource_id, api_version, description))
        if resource_id.lower() in self.delete_failures:
            raise self.delete_failures[resource_id.lower()]
        self.resources.pop(resource_id.lower(), None)


class ControlledExtensionClient:
    def __init__(self, configuration_settings=None, calls=None):
        self.extension = SimpleNamespace(
            configuration_settings=configuration_settings or {}
        )
        self.calls = calls

    def get(
        self,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
    ):
        if self.calls is not None:
            self.calls.append(
                (
                    "EXTENSION_GET",
                    resource_group_name,
                    cluster_rp,
                    cluster_type,
                    cluster_name,
                    name,
                )
            )
        return self.extension


def _cluster_id():
    return ChaosStudio._cluster_resource_id(
        SUBSCRIPTION_ID, RESOURCE_GROUP, CLUSTER_NAME
    )


def _connection_id():
    connection_name = ChaosStudio._recommended_connection_name(
        WORKSPACE_ID, _cluster_id()
    )
    return "{}/connections/{}".format(WORKSPACE_ID, connection_name)


def _base_resources(cluster=None, workspace=None):
    return {
        _cluster_id(): cluster or _valid_cluster(),
        WORKSPACE_ID: workspace or _valid_workspace(),
    }


def _instance(arm):
    instance = ChaosStudio()
    instance._arm_client_factory = lambda cmd: arm
    return instance


def _create(instance, **overrides):
    kwargs = {
        "cmd": SimpleNamespace(),
        "client": ControlledExtensionClient(),
        "resource_group_name": RESOURCE_GROUP,
        "cluster_name": CLUSTER_NAME,
        "name": "chaos",
        "cluster_type": "managedClusters",
        "cluster_rp": "Microsoft.ContainerService",
        "extension_type": "Microsoft.ChaosStudio",
        "scope": "cluster",
        "auto_upgrade_minor_version": None,
        "auto_upgrade_mode": None,
        "release_train": None,
        "version": None,
        "target_namespace": None,
        "release_namespace": None,
        "configuration_settings": {},
        "configuration_protected_settings": {},
        "configuration_settings_file": None,
        "configuration_protected_settings_file": None,
        "plan_name": None,
        "plan_publisher": None,
        "plan_product": None,
    }
    kwargs.update(overrides)
    return instance.Create(**kwargs)


def _update(instance, **overrides):
    kwargs = {
        "cmd": SimpleNamespace(),
        "resource_group_name": RESOURCE_GROUP,
        "cluster_name": CLUSTER_NAME,
        "auto_upgrade_minor_version": None,
        "auto_upgrade_mode": None,
        "release_train": None,
        "version": None,
        "configuration_settings": {},
        "configuration_protected_settings": {},
        "original_extension": None,
        "yes": True,
    }
    kwargs.update(overrides)
    return instance.Update(**kwargs)


def _delete(instance, **overrides):
    kwargs = {
        "cmd": SimpleNamespace(),
        "client": None,
        "resource_group_name": RESOURCE_GROUP,
        "cluster_name": CLUSTER_NAME,
        "name": "chaos",
        "cluster_type": "managedClusters",
        "cluster_rp": "Microsoft.ContainerService",
        "yes": True,
    }
    kwargs.update(overrides)
    return instance.Delete(**kwargs)


class TestChaosStudio(unittest.TestCase):
    def test_factory_selects_chaos_studio_and_preserves_default(self):
        from azext_k8s_extension.custom import ExtensionFactory

        self.assertIsInstance(ExtensionFactory("microsoft.chaosstudio"), ChaosStudio)
        self.assertIsInstance(ExtensionFactory("unknown.extension"), DefaultExtension)

    def test_explicit_existing_role_lifecycle(self):
        role_id = (
            "/subscriptions/" + SUBSCRIPTION_ID
            + "/providers/Microsoft.Authorization/roleDefinitions/"
            "c0e99fe5-44cb-429b-b4e1-a5af97f813e2"
        )
        role = ChaosStudio._role_definition_body(SUBSCRIPTION_ID)
        role["properties"]["permissions"][0]["dataActions"] = (
            ChaosStudio.ROLE_DATA_ACTIONS
            + ["Microsoft.ContainerService/managedClusters/namespaces/read"]
        )
        resources = _base_resources()
        resources[role_id] = role
        arm = ControlledArmClient(resources)
        instance = _instance(arm)
        extension, _, _ = _create(instance, configuration_settings={
            ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID,
            ChaosStudio.EXISTING_ROLE_KEY: role_id,
        })
        _update(instance, original_extension=extension)
        self.assertFalse(any(
            call[1].lower() == role_id.lower() for call in arm.writes
        ))
        assignment = next(
            value for key, value in arm.resources.items()
            if "/roleassignments/" in key
        )
        self.assertEqual(assignment["properties"]["roleDefinitionId"], role_id)
        with patch.object(DefaultExtension, "Delete", return_value=None):
            _delete(instance, client=ControlledExtensionClient(
                extension.configuration_settings
            ))
        self.assertIn(role_id.lower(), arm.resources)
        self.assertFalse(any("/roleassignments/" in key for key in arm.resources))

        role["properties"]["permissions"][0]["dataActions"].append("*")
        arm = ControlledArmClient(resources)
        with self.assertRaises(InvalidArgumentValueError):
            _create(_instance(arm), configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID,
                ChaosStudio.EXISTING_ROLE_KEY: role_id,
            })
        self.assertEqual(arm.writes, [])

    def test_workspace_identity_selection(self):
        self.assertEqual(
            ChaosStudio._workspace_principal_id(_valid_workspace()),
            WORKSPACE_PRINCIPAL_ID,
        )
        self.assertEqual(
            ChaosStudio._workspace_principal_id({"identity": {
                "type": "SystemAssigned",
                "principalId": WORKSPACE_PRINCIPAL_ID,
                "userAssignedIdentities": {},
            }}),
            WORKSPACE_PRINCIPAL_ID,
        )
        combined = _valid_workspace()
        combined["identity"]["type"] = "SystemAssigned, UserAssigned"
        combined["identity"]["principalId"] = WORKSPACE_PRINCIPAL_ID
        multiple = _valid_workspace()
        multiple["identity"]["userAssignedIdentities"]["second"] = {}
        for workspace in (
            combined, multiple,
            {"identity": {"type": "SystemAssigned"}},
        ):
            with self.subTest(workspace=workspace):
                arm = ControlledArmClient(_base_resources(workspace=workspace))
                with self.assertRaises(InvalidArgumentValueError):
                    _create(_instance(arm), configuration_settings={
                        ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID,
                    })
                self.assertEqual(arm.writes, [])

    def test_recommended_connection_name_matches_d66_vector(self):
        self.assertEqual(
            ChaosStudio._recommended_connection_name(
                EXAMPLE_WORKSPACE_ID, EXAMPLE_CLUSTER_ID
            ),
            "chaos-1bc1407c317f3febaad66247c6d564f21f90f99980af47242cb6fc3c84764984",
        )
        self.assertEqual(
            ChaosStudio._recommended_connection_name(
                EXAMPLE_WORKSPACE_ID.upper() + "/",
                EXAMPLE_CLUSTER_ID.upper() + "/",
            ),
            ChaosStudio._recommended_connection_name(
                EXAMPLE_WORKSPACE_ID, EXAMPLE_CLUSTER_ID
            ),
        )

    def test_create_without_workspace_keeps_partner_defaults(self):
        instance = ChaosStudio()

        extension, name, create_identity = _create(instance)

        self.assertEqual(ChaosStudio.DEFAULT_VERSION, "0.1.0")
        self.assertEqual(extension.extension_type, "Microsoft.ChaosStudio")
        self.assertEqual(extension.release_train, ChaosStudio.DEFAULT_RELEASE_TRAIN)
        self.assertEqual(extension.version, ChaosStudio.DEFAULT_VERSION)
        self.assertEqual(
            extension.scope.cluster.release_namespace,
            ChaosStudio.DEFAULT_RELEASE_NAMESPACE,
        )
        self.assertEqual(
            extension.configuration_settings,
            {"namespace": ChaosStudio.DEFAULT_RELEASE_NAMESPACE},
        )
        self.assertEqual(name, "chaos")
        self.assertFalse(create_identity)

    def test_create_validates_all_prerequisites_before_writes(self):
        cases = []
        cluster = _valid_cluster()
        cluster["properties"]["securityProfile"]["workloadIdentity"][
            "enabled"
        ] = False
        cases.append(("Workload Identity", cluster, _valid_workspace()))

        cluster = _valid_cluster()
        cluster["properties"]["oidcIssuerProfile"]["issuerURL"] = ""
        cases.append(("OIDC issuer", cluster, _valid_workspace()))

        cluster = _valid_cluster()
        cluster["properties"]["aadProfile"]["enableAzureRBAC"] = False
        cases.append(("Azure RBAC", cluster, _valid_workspace()))

        cases.append(("user-assigned", _valid_cluster(), {"identity": {}}))

        for expected, cluster, workspace in cases:
            with self.subTest(expected=expected):
                arm = ControlledArmClient(
                    _base_resources(cluster=cluster, workspace=workspace)
                )
                with self.assertRaisesRegex(
                    InvalidArgumentValueError, expected
                ):
                    _create(
                        _instance(arm),
                        configuration_settings={
                            ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                        },
                    )
                self.assertEqual(
                    arm.writes, []
                )

    def test_create_provisions_exact_resources_and_is_idempotent(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        settings = {
            ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID,
            "subscriber.serverEndpoint": "https://caller-supplied",
        }

        extension, _, _ = _create(
            instance, configuration_protected_settings=settings
        )

        puts = [call for call in arm.calls if call[0] == "PUT"]
        self.assertEqual(len(puts), 5)
        role_definition = next(
            call for call in puts if "/roleDefinitions/" in call[1]
        )
        identity = next(
            call
            for call in puts
            if "/userAssignedIdentities/" in call[1]
            and "/federatedIdentityCredentials/" not in call[1]
        )
        federated_credential = next(
            call
            for call in puts
            if "/federatedIdentityCredentials/" in call[1]
        )
        role_assignment = next(
            call for call in puts if "/roleAssignments/" in call[1]
        )
        connection = next(
            call for call in puts if "/connections/" in call[1]
        )

        permissions = role_definition[4]["properties"]["permissions"]
        self.assertEqual(
            permissions,
            [
                {
                    "actions": [
                        "Microsoft.ContainerService/managedClusters/read"
                    ],
                    "notActions": [],
                    "dataActions": [
                        "Microsoft.ContainerService/managedClusters/"
                        "serviceaccounts/impersonate/action",
                        "Microsoft.ContainerService/managedClusters/pods/read",
                    ],
                    "notDataActions": [],
                }
            ],
        )
        self.assertEqual(
            role_definition[4]["properties"]["assignableScopes"],
            ["/subscriptions/{}".format(SUBSCRIPTION_ID)],
        )
        self.assertTrue(role_assignment[1].startswith(_cluster_id() + "/"))
        self.assertEqual(
            role_assignment[4]["properties"]["principalId"],
            WORKSPACE_PRINCIPAL_ID,
        )
        self.assertNotEqual(
            role_assignment[4]["properties"]["principalId"],
            SUBSCRIBER_PRINCIPAL_ID,
        )
        self.assertEqual(
            federated_credential[4]["properties"],
            {
                "issuer": ISSUER,
                "subject": (
                    "system:serviceaccount:chaos-infrastructure:"
                    "chaos-subscriber"
                ),
                "audiences": ["api://AzureADTokenExchange"],
            },
        )
        self.assertEqual(
            identity[4]["tags"][ChaosStudio.CLUSTER_TAG], _cluster_id()
        )

        helm = extension.configuration_settings
        self.assertNotIn(ChaosStudio.WORKSPACE_ID_KEY, helm)
        self.assertNotIn(
            ChaosStudio.WORKSPACE_ID_KEY,
            extension.configuration_protected_settings,
        )
        self.assertEqual(helm["workloadIdentity.clientId"], CLIENT_ID)
        self.assertEqual(helm["workloadIdentity.tenantId"], TENANT_ID)
        self.assertEqual(
            helm["workspaceManagedIdentity.objectId"],
            WORKSPACE_PRINCIPAL_ID,
        )
        self.assertEqual(helm["subscriber.workspaceId"], WORKSPACE_ID)
        self.assertEqual(helm["subscriber.clusterResourceId"], _cluster_id())
        self.assertEqual(
            helm["subscriber.serverEndpoint"], DATA_PLANE_ENDPOINT
        )
        self.assertNotIn(
            "subscriber.serverEndpoint",
            extension.configuration_protected_settings,
        )
        self.assertEqual(connection[1], _connection_id())
        self.assertEqual(
            connection[2], ChaosStudio.CONNECTION_API_VERSION
        )
        self.assertEqual(
            connection[4],
            {
                "properties": {
                    "kind": "AksExtension",
                    "targetResourceId": _cluster_id(),
                    "principalId": SUBSCRIBER_PRINCIPAL_ID,
                    "tenantId": TENANT_ID,
                }
            },
        )

        first_resource_ids = [call[1] for call in puts]
        arm.calls.clear()
        _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        self.assertEqual(
            [call[1] for call in arm.writes], [_connection_id()]
        )
        second_resource_ids = [
            call[1] for call in arm.calls if call[0] == "GET"
        ]
        for resource_id in first_resource_ids:
            if resource_id != _connection_id():
                self.assertIn(resource_id, second_resource_ids)

    def test_existing_connection_requires_service_assigned_endpoint(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        arm.resources[_connection_id().lower()]["properties"].pop(
            "dataPlaneEndpoint"
        )
        arm.calls.clear()

        with self.assertRaisesRegex(
            AzureResponseError, "properties.dataPlaneEndpoint"
        ):
            _create(
                instance,
                configuration_settings={
                    ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                },
            )

        self.assertEqual(
            [call[1] for call in arm.writes], [_connection_id()]
        )

    def test_existing_connection_with_different_trust_keys_is_not_overwritten(
        self,
    ):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        arm.resources[_connection_id().lower()]["properties"][
            "principalId"
        ] = "00000000-0000-0000-0000-000000000099"
        arm.calls.clear()

        with self.assertRaisesRegex(
            AzureResponseError, "conflict"
        ):
            _create(
                instance,
                configuration_settings={
                    ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                },
            )

        self.assertEqual(
            [call[1] for call in arm.writes], [_connection_id()]
        )

    def test_successful_put_with_mismatched_response_is_reported_as_invalid(self):
        arm = ControlledArmClient(_base_resources())
        original_put = arm.put

        def put_with_mismatched_response(
            resource_id, api_version, description, body
        ):
            if "/connections/" in resource_id.lower():
                arm.calls.append(
                    (
                        "PUT",
                        resource_id,
                        api_version,
                        description,
                        copy.deepcopy(body),
                    )
                )
                return {
                    "properties": {
                        **body["properties"],
                        "principalId": (
                            "00000000-0000-0000-0000-000000000099"
                        ),
                        "dataPlaneEndpoint": DATA_PLANE_ENDPOINT,
                    }
                }
            return original_put(resource_id, api_version, description, body)

        with patch.object(arm, "put", side_effect=put_with_mismatched_response):
            with self.assertRaisesRegex(
                AzureResponseError,
                "response did not match the requested immutable trust keys",
            ):
                _create(
                    _instance(arm),
                    configuration_settings={
                        ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                    },
                )

    def test_existing_incompatible_resource_is_not_overwritten(self):
        arm = ControlledArmClient(_base_resources())
        resource_ids = ChaosStudio._prerequisite_resource_ids(
            SUBSCRIPTION_ID,
            RESOURCE_GROUP,
            CLUSTER_NAME,
            _cluster_id(),
        )
        arm.resources[resource_ids["identity"].lower()] = {
            "location": "westus2",
            "tags": {"owner": "someone-else"},
            "properties": {"clientId": CLIENT_ID, "tenantId": TENANT_ID},
        }

        with self.assertRaisesRegex(
            InvalidArgumentValueError, "not overwritten"
        ):
            _create(
                _instance(arm),
                configuration_settings={
                    ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                },
            )

        self.assertEqual(arm.writes, [])

    def test_custom_release_namespace_drives_and_reuses_federated_credential(
        self,
    ):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)

        extension, _, _ = _create(
            instance,
            release_namespace="custom-release",
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )

        federated_credential = next(
            call
            for call in arm.writes
            if "/federatedIdentityCredentials/" in call[1]
        )
        self.assertEqual(
            federated_credential[4]["properties"]["subject"],
            "system:serviceaccount:custom-release:chaos-subscriber",
        )
        self.assertEqual(
            extension.scope.cluster.release_namespace, "custom-release"
        )
        self.assertEqual(
            extension.configuration_settings["namespace"], "custom-release"
        )

        arm.calls.clear()
        _update(instance, original_extension=extension)

        self.assertEqual(
            [call[1] for call in arm.writes], [_connection_id()]
        )

    def test_arm_failure_is_actionable_and_precedes_writes(self):
        arm = ControlledArmClient(_base_resources())
        arm.failures[_cluster_id().lower()] = AzureResponseError(
            "Failed to GET AKS cluster '{}': forbidden".format(_cluster_id())
        )

        with self.assertRaisesRegex(
            AzureResponseError, "Failed to GET AKS cluster.*forbidden"
        ):
            _create(
                _instance(arm),
                configuration_settings={
                    ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
                },
            )

        self.assertEqual(arm.writes, [])

    def test_arm_transport_wraps_failures_with_operation_and_resource(self):
        error = CLIError("authorization denied")
        error.response = SimpleNamespace(status_code=403)
        arm = _ArmClient.__new__(_ArmClient)
        arm.cli_ctx = SimpleNamespace()
        arm.endpoint = "https://management.azure.com"

        with patch(
            "azext_k8s_extension.partner_extensions.ChaosStudio."
            "send_raw_request",
            side_effect=error,
        ):
            with self.assertRaisesRegex(
                AzureResponseError,
                "Failed to GET AKS cluster.*/managedClusters/test-cluster.*"
                "authorization denied",
            ):
                arm.get(
                    _cluster_id(),
                    ChaosStudio.AKS_API_VERSION,
                    "AKS cluster",
                )

        not_found = CLIError("resource not found")
        not_found.response = SimpleNamespace(status_code=404)
        with patch(
            "azext_k8s_extension.partner_extensions.ChaosStudio."
            "send_raw_request",
            side_effect=not_found,
        ):
            self.assertIsNone(
                arm.get(
                    _cluster_id(),
                    ChaosStudio.AKS_API_VERSION,
                    "optional resource",
                    allow_not_found=True,
                )
            )

    def test_update_reconciles_same_resources_without_identity_changes(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        resource_ids = ChaosStudio._prerequisite_resource_ids(
            SUBSCRIPTION_ID,
            RESOURCE_GROUP,
            CLUSTER_NAME,
            _cluster_id(),
        )
        arm.resources.pop(resource_ids["federated_credential"].lower())
        arm.calls.clear()

        patch_extension = _update(
            instance, original_extension=extension
        )

        self.assertEqual(
            [call[1] for call in arm.writes],
            [
                resource_ids["federated_credential"],
                _connection_id(),
            ],
        )
        self.assertEqual(
            patch_extension.configuration_settings[
                "workloadIdentity.clientId"
            ],
            CLIENT_ID,
        )
        self.assertEqual(
            patch_extension.configuration_settings[
                "subscriber.workspaceId"
            ],
            WORKSPACE_ID,
        )
        self.assertNotIn(
            ChaosStudio.WORKSPACE_ID_KEY,
            patch_extension.configuration_settings,
        )
        self.assertEqual(
            patch_extension.configuration_settings[
                "subscriber.clusterResourceId"
            ],
            _cluster_id(),
        )

    def test_update_preserves_original_settings_and_replaces_endpoint(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID,
                "custom.setting": "original",
            },
        )

        patch_extension = _update(
            instance,
            original_extension=extension,
            configuration_settings={"another.setting": "new"},
            configuration_protected_settings={
                ChaosStudio.SERVER_ENDPOINT_KEY: "https://caller-supplied"
            },
        )

        self.assertEqual(
            patch_extension.configuration_settings["custom.setting"],
            "original",
        )
        self.assertEqual(
            patch_extension.configuration_settings["another.setting"], "new"
        )
        self.assertEqual(
            patch_extension.configuration_settings[
                ChaosStudio.SERVER_ENDPOINT_KEY
            ],
            DATA_PLANE_ENDPOINT,
        )
        self.assertNotIn(
            ChaosStudio.SERVER_ENDPOINT_KEY,
            patch_extension.configuration_protected_settings,
        )

    def test_delete_revokes_owned_connection_before_prerequisites(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        resource_ids = ChaosStudio._prerequisite_resource_ids(
            SUBSCRIPTION_ID,
            RESOURCE_GROUP,
            CLUSTER_NAME,
            _cluster_id(),
        )
        arm.calls.clear()
        client = ControlledExtensionClient(
            extension.configuration_settings, arm.calls
        )

        with patch.object(
            DefaultExtension,
            "Delete",
            side_effect=lambda *args: arm.calls.append(("CONFIRM",)),
        ) as confirmation:
            _delete(instance, client=client)

        confirmation.assert_called_once()
        self.assertEqual(
            [call[1] for call in arm.calls if call[0] == "DELETE"],
            [
                _connection_id(),
                resource_ids["role_assignment"],
                resource_ids["identity"],
            ],
        )
        self.assertIn(
            resource_ids["role_definition"].lower(), arm.resources
        )
        self.assertNotIn(_connection_id().lower(), arm.resources)
        self.assertIn(
            (
                "EXTENSION_GET",
                RESOURCE_GROUP,
                "Microsoft.ContainerService",
                "managedClusters",
                CLUSTER_NAME,
                "chaos",
            ),
            arm.calls,
        )
        self.assertLess(
            next(i for i, call in enumerate(arm.calls) if call[0] == "CONFIRM"),
            next(
                i
                for i, call in enumerate(arm.calls)
                if call[0] == "EXTENSION_GET"
            ),
        )

    def test_delete_absent_connection_still_removes_owned_prerequisites(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        resource_ids = ChaosStudio._prerequisite_resource_ids(
            SUBSCRIPTION_ID,
            RESOURCE_GROUP,
            CLUSTER_NAME,
            _cluster_id(),
        )
        arm.resources.pop(_connection_id().lower())
        arm.calls.clear()

        with patch.object(DefaultExtension, "Delete"):
            _delete(
                instance,
                client=ControlledExtensionClient(
                    extension.configuration_settings
                ),
            )

        self.assertEqual(
            [call[1] for call in arm.calls if call[0] == "DELETE"],
            [
                resource_ids["role_assignment"],
                resource_ids["identity"],
            ],
        )

    def test_delete_retry_succeeds_after_owned_resources_are_already_removed(
        self,
    ):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        client = ControlledExtensionClient(extension.configuration_settings)

        with patch.object(DefaultExtension, "Delete"):
            _delete(instance, client=client)
            arm.calls.clear()
            _delete(instance, client=client)

        self.assertEqual(
            [call for call in arm.calls if call[0] == "DELETE"], []
        )

    def test_delete_allows_manual_shared_identity_when_connection_is_absent(
        self,
    ):
        arm = ControlledArmClient(_base_resources())
        settings = {
            "subscriber.workspaceId": WORKSPACE_ID,
            "subscriber.clusterResourceId": _cluster_id(),
            "workloadIdentity.clientId": "shared-client",
            "workloadIdentity.tenantId": "shared-tenant",
        }

        with patch.object(DefaultExtension, "Delete") as confirmation:
            _delete(
                _instance(arm),
                client=ControlledExtensionClient(settings),
            )

        confirmation.assert_called_once()
        self.assertEqual(
            [call for call in arm.calls if call[0] == "DELETE"], []
        )

    def test_delete_mismatched_connection_stops_before_cleanup(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        arm.resources[_connection_id().lower()]["properties"][
            "principalId"
        ] = "00000000-0000-0000-0000-000000000099"
        arm.calls.clear()

        with patch.object(DefaultExtension, "Delete"):
            with self.assertRaisesRegex(
                InvalidArgumentValueError, "does not match"
            ):
                _delete(
                    instance,
                    client=ControlledExtensionClient(
                        extension.configuration_settings
                    ),
                )

        self.assertEqual(
            [call for call in arm.calls if call[0] == "DELETE"], []
        )
        self.assertIn(_connection_id().lower(), arm.resources)

    def test_delete_connection_failure_stops_before_cleanup(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        extension, _, _ = _create(
            instance,
            configuration_settings={
                ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID
            },
        )
        arm.delete_failures[_connection_id().lower()] = AzureResponseError(
            "Failed to DELETE Chaos Studio workspace connection"
        )
        arm.calls.clear()

        with patch.object(DefaultExtension, "Delete"):
            with self.assertRaisesRegex(
                AzureResponseError, "Failed to DELETE"
            ):
                _delete(
                    instance,
                    client=ControlledExtensionClient(
                        extension.configuration_settings
                    ),
                )

        self.assertEqual(
            [call[1] for call in arm.calls if call[0] == "DELETE"],
            [_connection_id()],
        )

    def test_delete_preserves_unowned_deterministic_collisions(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        resource_ids = ChaosStudio._prerequisite_resource_ids(
            SUBSCRIPTION_ID,
            RESOURCE_GROUP,
            CLUSTER_NAME,
            _cluster_id(),
        )
        arm.resources[resource_ids["identity"].lower()] = {
            "location": "westus2",
            "tags": {"owner": "someone-else"},
            "properties": {"clientId": "other", "tenantId": "other"},
        }
        arm.resources[resource_ids["role_assignment"].lower()] = {
            "properties": {
                "roleDefinitionId": resource_ids["role_definition"],
                "description": "owned by someone else",
            }
        }

        with patch.object(DefaultExtension, "Delete") as confirmation:
            _delete(instance, client=ControlledExtensionClient())

        confirmation.assert_called_once()
        self.assertEqual(
            [call for call in arm.calls if call[0] == "DELETE"], []
        )
        self.assertIn(resource_ids["identity"].lower(), arm.resources)
        self.assertIn(
            resource_ids["role_assignment"].lower(), arm.resources
        )

    def test_update_rejects_workspace_identity_change_before_writes(self):
        arm = ControlledArmClient(_base_resources())
        instance = _instance(arm)
        original = SimpleNamespace(
            configuration_settings={"subscriber.workspaceId": WORKSPACE_ID}
        )

        with self.assertRaisesRegex(
            InvalidArgumentValueError, "Changing 'chaos-workspace-id'"
        ):
            _update(
                instance,
                original_extension=original,
                configuration_settings={
                    ChaosStudio.WORKSPACE_ID_KEY: WORKSPACE_ID + "-other"
                },
            )

        self.assertEqual(arm.writes, [])

    def test_update_rejects_release_namespace_change_before_writes(self):
        arm = ControlledArmClient(_base_resources())
        original = SimpleNamespace(
            scope=SimpleNamespace(
                cluster=SimpleNamespace(
                    release_namespace="original-release"
                )
            ),
            configuration_settings={
                "namespace": "original-release",
                "subscriber.workspaceId": WORKSPACE_ID,
            },
        )

        with self.assertRaisesRegex(
            InvalidArgumentValueError, "Changing the release namespace"
        ):
            _update(
                _instance(arm),
                original_extension=original,
                configuration_settings={"namespace": "other-release"},
            )

        self.assertEqual(arm.writes, [])

    def test_signature_matches_partner_extension_model(self):
        for method in ("Create", "Update", "Delete"):
            expected = list(
                inspect.signature(getattr(PartnerExtensionModel, method)).parameters
            )
            actual = list(inspect.signature(getattr(ChaosStudio, method)).parameters)
            self.assertEqual(expected, actual, "{} signature drifted".format(method))


if __name__ == "__main__":
    unittest.main()
