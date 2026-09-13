# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import hashlib
import json
import uuid

from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from knack.log import get_logger
from knack.util import CLIError

from ..vendored_sdks.models import Extension, PatchExtension, Scope, ScopeCluster
from .DefaultExtension import DefaultExtension

logger = get_logger(__name__)


class _ArmClient:
    """Small ARM transport kept injectable for partner-model unit tests."""

    def __init__(self, cmd):
        self.cli_ctx = cmd.cli_ctx
        self.subscription_id = get_subscription_id(self.cli_ctx)
        self.endpoint = self.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")

    def get(self, resource_id, api_version, description, allow_not_found=False):
        return self._request(
            "GET",
            resource_id,
            api_version,
            description,
            allow_not_found=allow_not_found,
        )

    def put(self, resource_id, api_version, description, body):
        return self._request(
            "PUT", resource_id, api_version, description, body=body
        )

    def delete(self, resource_id, api_version, description):
        return self._request("DELETE", resource_id, api_version, description)

    def _request(
        self,
        method,
        resource_id,
        api_version,
        description,
        body=None,
        allow_not_found=False,
    ):
        url = "{}{}?api-version={}".format(
            self.endpoint, resource_id, api_version
        )
        headers = [
            "User-Agent=chaos-studio-aks-extension",
            "Content-Type=application/json",
        ]
        try:
            response = send_raw_request(
                self.cli_ctx,
                method,
                url,
                body=json.dumps(body) if body is not None else None,
                headers=headers,
            )
        except CLIError as error:
            status_code = getattr(
                getattr(error, "response", None), "status_code", None
            )
            if allow_not_found and status_code == 404:
                return None
            raise AzureResponseError(
                "Failed to {} {} '{}': {}".format(
                    method, description, resource_id, error
                )
            ) from error

        if method == "DELETE":
            return None
        try:
            return response.json()
        except ValueError as error:
            raise AzureResponseError(
                "ARM returned an invalid response while attempting to {} {} "
                "'{}'.".format(method, description, resource_id)
            ) from error


class ChaosStudio(DefaultExtension):
    """Microsoft.ChaosStudio validations, defaults, and prerequisites."""

    DEFAULT_CLUSTER_TYPE = "managedclusters"
    DEFAULT_RELEASE_NAMESPACE = "chaos-infrastructure"
    DEFAULT_RELEASE_TRAIN = "dev"
    DEFAULT_VERSION = "0.1.0"
    WORKSPACE_ID_KEY = "chaos-workspace-id"
    EXISTING_ROLE_KEY = "chaos-existing-role-definition-id"

    AKS_API_VERSION = "2024-10-01"
    WORKSPACE_API_VERSION = "2026-08-01-preview"
    CONNECTION_API_VERSION = "2026-08-01-preview"
    IDENTITY_API_VERSION = "2023-01-31"
    AUTHORIZATION_API_VERSION = "2022-04-01"
    CONNECTION_KIND = "AksExtension"
    SERVER_ENDPOINT_KEY = "subscriber.serverEndpoint"

    FEDERATED_CREDENTIAL_NAME = "chaos-subscriber"
    FEDERATED_CREDENTIAL_AUDIENCE = "api://AzureADTokenExchange"

    ROLE_NAME = "Chaos Studio Kubernetes Operator"
    ROLE_DESCRIPTION = (
        "Allows a Chaos Studio workspace managed identity to operate through "
        "the chaos-subscriber ServiceAccount on AKS."
    )
    ROLE_ACTIONS = ["Microsoft.ContainerService/managedClusters/read"]
    ROLE_DATA_ACTIONS = [
        "Microsoft.ContainerService/managedClusters/serviceaccounts/"
        "impersonate/action",
        "Microsoft.ContainerService/managedClusters/pods/read",
    ]
    ROLE_DEFINITION_GUID = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            "microsoft-chaosstudio-kubernetes-operator",
        )
    )

    OWNER_TAG = "ChaosStudioAksExtension"
    OWNER_TAG_VALUE = "true"
    CLUSTER_TAG = "ChaosStudioClusterResourceId"
    ROLE_ASSIGNMENT_DESCRIPTION = (
        "Owned by the Microsoft.ChaosStudio AKS extension."
    )

    def __init__(self):
        self._arm_client_factory = _ArmClient

    def Create(
        self,
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        cluster_rp,
        extension_type,
        scope,
        auto_upgrade_minor_version,
        auto_upgrade_mode,
        release_train,
        version,
        target_namespace,
        release_namespace,
        configuration_settings,
        configuration_protected_settings,
        configuration_settings_file,
        configuration_protected_settings_file,
        plan_name,
        plan_publisher,
        plan_product,
    ):
        """Apply Microsoft.ChaosStudio create defaults and prerequisites."""
        self._validate_cluster_type(cluster_type)
        self._validate_scope(scope)
        self._warn_ignored_auto_upgrade(
            auto_upgrade_minor_version, auto_upgrade_mode
        )

        configuration_settings = dict(configuration_settings or {})
        configuration_protected_settings = dict(
            configuration_protected_settings or {}
        )
        workspace_id = self._take_workspace_id(
            configuration_settings, configuration_protected_settings
        )
        release_namespace = self._resolve_release_namespace(
            release_namespace
        )
        if workspace_id is not None:
            configuration_protected_settings.pop(
                self.SERVER_ENDPOINT_KEY, None
            )
            configuration_settings.update(
                self._reconcile_prerequisites(
                    cmd,
                    resource_group_name,
                    cluster_name,
                    workspace_id,
                    release_namespace,
                    configuration_settings.get(self.EXISTING_ROLE_KEY),
                )
            )

        configuration_settings["namespace"] = release_namespace
        extension_scope = Scope(
            cluster=ScopeCluster(release_namespace=release_namespace),
            namespace=None,
        )
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=False,
            auto_upgrade_mode=None,
            release_train=release_train or self.DEFAULT_RELEASE_TRAIN,
            version=version or self.DEFAULT_VERSION,
            scope=extension_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )
        return extension, name, False

    def Update(
        self,
        cmd,
        resource_group_name,
        cluster_name,
        auto_upgrade_minor_version,
        auto_upgrade_mode,
        release_train,
        version,
        configuration_settings,
        configuration_protected_settings,
        original_extension,
        yes=False,
    ):
        """Reconcile prerequisites while retaining deterministic identities."""
        self._warn_ignored_auto_upgrade(
            auto_upgrade_minor_version, auto_upgrade_mode
        )
        supplied_settings = dict(configuration_settings or {})
        configuration_protected_settings = dict(
            configuration_protected_settings or {}
        )
        original_settings = dict(
            getattr(original_extension, "configuration_settings", None) or {}
        )
        configuration_settings = dict(original_settings)
        configuration_settings.update(supplied_settings)
        release_namespace = self._existing_release_namespace(
            original_extension, original_settings
        )
        requested_namespace = supplied_settings.get("namespace")
        if (
            requested_namespace is not None
            and requested_namespace != release_namespace
        ):
            raise InvalidArgumentValueError(
                "Changing the release namespace requires deleting and "
                "recreating the extension."
            )
        workspace_id = self._take_workspace_id(
            configuration_settings,
            configuration_protected_settings,
            original_settings,
        )
        if workspace_id is not None:
            configuration_protected_settings.pop(
                self.SERVER_ENDPOINT_KEY, None
            )
            configuration_settings.update(
                self._reconcile_prerequisites(
                    cmd,
                    resource_group_name,
                    cluster_name,
                    workspace_id,
                    release_namespace,
                    configuration_settings.get(self.EXISTING_ROLE_KEY),
                )
            )

        return PatchExtension(
            auto_upgrade_minor_version=False,
            auto_upgrade_mode=None,
            release_train=(
                release_train
                or getattr(original_extension, "release_train", None)
                or self.DEFAULT_RELEASE_TRAIN
            ),
            version=(
                version
                or getattr(original_extension, "version", None)
                or self.DEFAULT_VERSION
            ),
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )

    def Delete(
        self,
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        cluster_rp,
        yes,
    ):
        """Confirm normally, then remove only extension-owned resources."""
        super().Delete(
            cmd,
            client,
            resource_group_name,
            cluster_name,
            name,
            cluster_type,
            cluster_rp,
            yes,
        )
        existing_role_id = self._delete_owned_workspace_connection(
            cmd,
            client,
            resource_group_name,
            cluster_name,
            name,
            cluster_type,
            cluster_rp,
        )
        self._delete_owned_prerequisites(
            cmd, resource_group_name, cluster_name, existing_role_id
        )

    def _reconcile_prerequisites(
        self,
        cmd,
        resource_group_name,
        cluster_name,
        workspace_id,
        release_namespace,
        existing_role_id=None,
    ):
        arm = self._arm_client_factory(cmd)
        cluster_id = self._cluster_resource_id(
            arm.subscription_id, resource_group_name, cluster_name
        )
        workspace_id = self._validate_workspace_id(workspace_id)

        cluster = arm.get(
            cluster_id,
            self.AKS_API_VERSION,
            "AKS cluster",
        )
        issuer, location = self._validate_cluster(cluster)
        workspace = arm.get(
            workspace_id,
            self.WORKSPACE_API_VERSION,
            "Chaos Studio workspace",
        )
        workspace_principal_id = self._workspace_principal_id(workspace)

        resource_ids = self._prerequisite_resource_ids(
            arm.subscription_id,
            resource_group_name,
            cluster_name,
            cluster_id,
        )
        role_definition = arm.get(
            self._select_role_id(resource_ids, existing_role_id, arm.subscription_id),
            self.AUTHORIZATION_API_VERSION,
            "Chaos Studio Kubernetes Operator role definition",
            allow_not_found=existing_role_id is None,
        )
        identity = arm.get(
            resource_ids["identity"],
            self.IDENTITY_API_VERSION,
            "subscriber managed identity",
            allow_not_found=True,
        )
        federated_credential = None
        if identity is not None:
            federated_credential = arm.get(
                resource_ids["federated_credential"],
                self.IDENTITY_API_VERSION,
                "subscriber federated credential",
                allow_not_found=True,
            )
        role_assignment = arm.get(
            resource_ids["role_assignment"],
            self.AUTHORIZATION_API_VERSION,
            "workspace managed identity role assignment",
            allow_not_found=True,
        )

        if role_definition is not None:
            self._validate_role_definition(
                role_definition, arm.subscription_id, existing_role_id is not None
            )
        if identity is not None:
            self._validate_identity(identity, cluster_id, location)
        if federated_credential is not None:
            self._validate_federated_credential(
                federated_credential, issuer, release_namespace
            )
        if role_assignment is not None:
            self._validate_role_assignment(
                role_assignment,
                resource_ids["role_definition"],
                workspace_principal_id,
            )

        if role_definition is None:
            arm.put(
                resource_ids["role_definition"],
                self.AUTHORIZATION_API_VERSION,
                "Chaos Studio Kubernetes Operator role definition",
                self._role_definition_body(arm.subscription_id),
            )
        if identity is None:
            arm.put(
                resource_ids["identity"],
                self.IDENTITY_API_VERSION,
                "subscriber managed identity",
                self._identity_body(cluster_id, location),
            )
            identity = arm.get(
                resource_ids["identity"],
                self.IDENTITY_API_VERSION,
                "subscriber managed identity",
            )
            self._validate_identity(identity, cluster_id, location)
        if federated_credential is None:
            arm.put(
                resource_ids["federated_credential"],
                self.IDENTITY_API_VERSION,
                "subscriber federated credential",
                self._federated_credential_body(
                    issuer, release_namespace
                ),
            )
        if role_assignment is None:
            arm.put(
                resource_ids["role_assignment"],
                self.AUTHORIZATION_API_VERSION,
                "workspace managed identity role assignment",
                self._role_assignment_body(
                    resource_ids["role_definition"],
                    workspace_principal_id,
                ),
            )

        identity_properties = identity.get("properties") or {}
        data_plane_endpoint = self._reconcile_workspace_connection(
            arm,
            workspace_id,
            cluster_id,
            identity_properties["principalId"],
            identity_properties["tenantId"],
        )
        return {
            "workloadIdentity.clientId": identity_properties["clientId"],
            "workloadIdentity.tenantId": identity_properties["tenantId"],
            "workspaceManagedIdentity.objectId": workspace_principal_id,
            "subscriber.workspaceId": workspace_id,
            "subscriber.clusterResourceId": cluster_id,
            self.SERVER_ENDPOINT_KEY: data_plane_endpoint,
        }

    @classmethod
    def _reconcile_workspace_connection(
        cls,
        arm,
        workspace_id,
        cluster_id,
        principal_id,
        tenant_id,
    ):
        connection_name = cls._recommended_connection_name(
            workspace_id, cluster_id
        )
        connection_id = "{}/connections/{}".format(
            workspace_id, connection_name
        )
        expected = {
            "kind": cls.CONNECTION_KIND,
            "targetResourceId": cluster_id,
            "principalId": principal_id,
            "tenantId": tenant_id,
        }
        connection = arm.put(
            connection_id,
            cls.CONNECTION_API_VERSION,
            "Chaos Studio workspace connection",
            {"properties": expected},
        )

        if not isinstance(connection, dict):
            raise AzureResponseError(
                "The Chaos Studio workspace connection PUT returned an "
                "invalid response."
            )
        properties = connection.get("properties") or {}
        if not (
            properties.get("kind") == expected["kind"]
            and cls._same_resource_id(
                properties.get("targetResourceId"),
                expected["targetResourceId"],
            )
            and cls._same_identifier(
                properties.get("principalId"), expected["principalId"]
            )
            and cls._same_identifier(
                properties.get("tenantId"), expected["tenantId"]
            )
        ):
            raise AzureResponseError(
                "The Chaos Studio workspace connection response did not "
                "match the requested immutable trust keys."
            )

        endpoint = properties.get("dataPlaneEndpoint")
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise AzureResponseError(
                "The Chaos Studio workspace connection response did not "
                "include 'properties.dataPlaneEndpoint'."
            )
        return endpoint

    @classmethod
    def _recommended_connection_name(cls, workspace_id, target_resource_id):
        fields = (
            cls._canonicalize_arm_id(workspace_id),
            cls._canonicalize_arm_id(target_resource_id),
            cls.CONNECTION_KIND,
        )
        payload = b"".join(
            len(encoded).to_bytes(4, byteorder="big") + encoded
            for encoded in (
                field.encode("utf-8") for field in fields
            )
        )
        return "chaos-" + hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _canonicalize_arm_id(resource_id):
        normalized = "/" + resource_id.strip().strip("/")
        return "/" + "/".join(
            segment.lower() for segment in normalized.strip("/").split("/")
        )

    @staticmethod
    def _same_identifier(left, right):
        return (
            isinstance(left, str)
            and isinstance(right, str)
            and left.lower() == right.lower()
        )

    def _delete_owned_workspace_connection(
        self,
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        cluster_rp,
    ):
        extension = client.get(
            resource_group_name,
            cluster_rp,
            cluster_type,
            cluster_name,
            name,
        )
        settings = dict(
            getattr(extension, "configuration_settings", None) or {}
        )
        workspace_id = settings.get("subscriber.workspaceId")
        managed_keys = (
            "subscriber.workspaceId",
            "subscriber.clusterResourceId",
            "workloadIdentity.clientId",
            "workloadIdentity.tenantId",
        )
        if workspace_id is None:
            if any(key in settings for key in managed_keys[1:]):
                raise InvalidArgumentValueError(
                    "The installed Microsoft.ChaosStudio extension has "
                    "incomplete managed workspace settings. Its workspace "
                    "connection was not deleted."
                )
            return

        missing = [key for key in managed_keys if not settings.get(key)]
        if missing:
            raise InvalidArgumentValueError(
                "The installed Microsoft.ChaosStudio extension is missing "
                "managed workspace setting(s): {}. Its workspace connection "
                "was not deleted.".format(", ".join(missing))
            )

        arm = self._arm_client_factory(cmd)
        cluster_id = self._cluster_resource_id(
            arm.subscription_id, resource_group_name, cluster_name
        )
        workspace_id = self._validate_workspace_id(workspace_id)
        if not self._same_resource_id(
            settings["subscriber.clusterResourceId"], cluster_id
        ):
            raise InvalidArgumentValueError(
                "The installed Microsoft.ChaosStudio extension's managed "
                "cluster setting does not match this cluster. Its workspace "
                "connection was not deleted."
            )

        connection_id = "{}/connections/{}".format(
            workspace_id,
            self._recommended_connection_name(workspace_id, cluster_id),
        )
        connection = arm.get(
            connection_id,
            self.CONNECTION_API_VERSION,
            "Chaos Studio workspace connection",
            allow_not_found=True,
        )
        if connection is None:
            return settings.get(self.EXISTING_ROLE_KEY)

        resource_ids = self._prerequisite_resource_ids(
            arm.subscription_id,
            resource_group_name,
            cluster_name,
            cluster_id,
        )
        cluster = arm.get(
            cluster_id,
            self.AKS_API_VERSION,
            "AKS cluster",
        )
        location = cluster.get("location")
        if not location:
            raise InvalidArgumentValueError(
                "The AKS cluster response did not include a location."
            )
        identity = arm.get(
            resource_ids["identity"],
            self.IDENTITY_API_VERSION,
            "subscriber managed identity",
            allow_not_found=True,
        )
        if identity is None:
            raise InvalidArgumentValueError(
                "The extension-owned subscriber managed identity could not "
                "be found. The workspace connection was not deleted."
            )
        self._validate_identity(identity, cluster_id, location)
        identity_properties = identity.get("properties") or {}
        if not (
            self._same_identifier(
                identity_properties.get("clientId"),
                settings["workloadIdentity.clientId"],
            )
            and self._same_identifier(
                identity_properties.get("tenantId"),
                settings["workloadIdentity.tenantId"],
            )
        ):
            raise InvalidArgumentValueError(
                "The installed Microsoft.ChaosStudio extension settings do "
                "not match the extension-owned subscriber managed identity. "
                "The workspace connection was not deleted."
            )

        if not isinstance(connection, dict):
            raise AzureResponseError(
                "The Chaos Studio workspace connection GET returned an "
                "invalid response."
            )
        properties = connection.get("properties") or {}
        if not (
            properties.get("kind") == self.CONNECTION_KIND
            and self._same_resource_id(
                properties.get("targetResourceId"), cluster_id
            )
            and self._same_identifier(
                properties.get("principalId"),
                identity_properties.get("principalId"),
            )
            and self._same_identifier(
                properties.get("tenantId"),
                identity_properties.get("tenantId"),
            )
        ):
            raise InvalidArgumentValueError(
                "The Chaos Studio workspace connection does not match the "
                "installed extension and its owned subscriber identity. It "
                "was not deleted."
            )

        arm.delete(
            connection_id,
            self.CONNECTION_API_VERSION,
            "Chaos Studio workspace connection",
        )
        return settings.get(self.EXISTING_ROLE_KEY)

    def _delete_owned_prerequisites(
        self, cmd, resource_group_name, cluster_name, existing_role_id=None
    ):
        arm = self._arm_client_factory(cmd)
        cluster_id = self._cluster_resource_id(
            arm.subscription_id, resource_group_name, cluster_name
        )
        resource_ids = self._prerequisite_resource_ids(
            arm.subscription_id,
            resource_group_name,
            cluster_name,
            cluster_id,
        )
        self._select_role_id(resource_ids, existing_role_id, arm.subscription_id)
        role_assignment = arm.get(
            resource_ids["role_assignment"],
            self.AUTHORIZATION_API_VERSION,
            "workspace managed identity role assignment",
            allow_not_found=True,
        )
        identity = arm.get(
            resource_ids["identity"],
            self.IDENTITY_API_VERSION,
            "subscriber managed identity",
            allow_not_found=True,
        )

        if role_assignment is not None:
            properties = role_assignment.get("properties") or {}
            if (
                self._same_resource_id(
                    properties.get("roleDefinitionId"),
                    resource_ids["role_definition"],
                )
                and properties.get("description")
                == self.ROLE_ASSIGNMENT_DESCRIPTION
            ):
                arm.delete(
                    resource_ids["role_assignment"],
                    self.AUTHORIZATION_API_VERSION,
                    "workspace managed identity role assignment",
                )
            else:
                logger.warning(
                    "Preserving role assignment '%s' because it is not owned "
                    "by the Microsoft.ChaosStudio extension.",
                    resource_ids["role_assignment"],
                )

        if identity is not None:
            if self._identity_is_owned(identity, cluster_id):
                arm.delete(
                    resource_ids["identity"],
                    self.IDENTITY_API_VERSION,
                    "subscriber managed identity",
                )
            else:
                logger.warning(
                    "Preserving managed identity '%s' because it is not owned "
                    "by the Microsoft.ChaosStudio extension.",
                    resource_ids["identity"],
                )

    @classmethod
    def _take_workspace_id(
        cls, settings, protected_settings, original_settings=None
    ):
        supplied = []
        for source in (settings, protected_settings):
            if cls.WORKSPACE_ID_KEY in source:
                supplied.append(source.pop(cls.WORKSPACE_ID_KEY))
        if len(set(supplied)) > 1:
            raise InvalidArgumentValueError(
                "'chaos-workspace-id' must have one consistent value."
            )

        original_workspace_id = (original_settings or {}).get(
            "subscriber.workspaceId"
        )
        workspace_id = supplied[0] if supplied else original_workspace_id
        if (
            supplied
            and original_workspace_id
            and not cls._same_resource_id(
                workspace_id, original_workspace_id
            )
        ):
            raise InvalidArgumentValueError(
                "Changing 'chaos-workspace-id' on an installed extension is "
                "not supported. Delete and recreate the extension instead."
            )
        return workspace_id

    @staticmethod
    def _validate_workspace_id(workspace_id):
        if not isinstance(workspace_id, str):
            raise InvalidArgumentValueError(
                "'chaos-workspace-id' must be a Chaos Studio workspace "
                "resource ID."
            )
        normalized = "/" + workspace_id.strip().strip("/")
        parts = normalized.strip("/").split("/")
        if (
            len(parts) != 8
            or parts[0].lower() != "subscriptions"
            or parts[2].lower() != "resourcegroups"
            or parts[4].lower() != "providers"
            or parts[5].lower() != "microsoft.chaos"
            or parts[6].lower() != "workspaces"
            or not all(parts[index] for index in (1, 3, 7))
        ):
            raise InvalidArgumentValueError(
                "'chaos-workspace-id' must use "
                "'/subscriptions/{subscription}/resourceGroups/{group}/"
                "providers/Microsoft.Chaos/workspaces/{workspace}'."
            )
        return normalized

    @staticmethod
    def _validate_cluster(cluster):
        properties = cluster.get("properties") or {}
        workload_identity = (
            (properties.get("securityProfile") or {}).get(
                "workloadIdentity"
            )
            or {}
        )
        if workload_identity.get("enabled") is not True:
            raise InvalidArgumentValueError(
                "AKS Workload Identity must be enabled before installing "
                "Microsoft.ChaosStudio."
            )

        oidc_profile = properties.get("oidcIssuerProfile") or {}
        issuer = oidc_profile.get("issuerURL") or oidc_profile.get("issuerUrl")
        if oidc_profile.get("enabled") is not True or not issuer:
            raise InvalidArgumentValueError(
                "The AKS OIDC issuer must be enabled and expose an issuer URL "
                "before installing Microsoft.ChaosStudio."
            )

        aad_profile = properties.get("aadProfile") or {}
        if aad_profile.get("enableAzureRBAC") is not True:
            raise InvalidArgumentValueError(
                "Azure RBAC for Kubernetes must be enabled before installing "
                "Microsoft.ChaosStudio."
            )

        location = cluster.get("location")
        if not location:
            raise InvalidArgumentValueError(
                "The AKS cluster response did not include a location."
            )
        return issuer, location

    @staticmethod
    def _workspace_principal_id(workspace):
        identity = workspace.get("identity") or {}
        identity_type = identity.get("type") or ""
        user_assigned = identity.get("userAssignedIdentities") or {}
        if identity_type.lower() == "systemassigned" and not user_assigned:
            principal_id = identity.get("principalId")
            if principal_id:
                return principal_id
        principal_ids = [
            value.get("principalId")
            for value in user_assigned.values()
            if value.get("principalId")
        ]
        if (identity_type.lower() != "userassigned"
                or len(user_assigned) != 1 or len(principal_ids) != 1):
            raise InvalidArgumentValueError(
                "The Chaos Studio workspace must expose a system-assigned "
                "identity or exactly one user-assigned managed identity "
                "with a principal ID; combined identities are ambiguous."
            )
        return principal_ids[0]

    @classmethod
    def _select_role_id(cls, resource_ids, existing_role_id, subscription_id):
        if existing_role_id is not None:
            prefix = "/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/".format(
                subscription_id
            )
            if (not isinstance(existing_role_id, str)
                    or not existing_role_id.lower().startswith(prefix.lower())):
                raise InvalidArgumentValueError(
                    "The existing role definition must be an ARM ID in the cluster subscription."
                )
            try:
                uuid.UUID(existing_role_id[len(prefix):])
            except ValueError as error:
                raise InvalidArgumentValueError(
                    "The existing role definition ID must end in a UUID."
                ) from error
            resource_ids["role_definition"] = existing_role_id
        return resource_ids["role_definition"]

    @classmethod
    def _validate_role_definition(cls, role_definition, subscription_id, explicit=False):
        properties = role_definition.get("properties") or {}
        permissions = properties.get("permissions") or []
        expected_scope = "/subscriptions/{}".format(subscription_id)
        compatible = (
            properties.get("roleName") == cls.ROLE_NAME
            and (explicit or properties.get("description") == cls.ROLE_DESCRIPTION)
            and properties.get("type") == "CustomRole"
            and properties.get("assignableScopes") == [expected_scope]
            and len(permissions) == 1
            and permissions[0].get("actions") == cls.ROLE_ACTIONS
            and permissions[0].get("notActions") == []
            and (
                permissions[0].get("dataActions") == cls.ROLE_DATA_ACTIONS
                or (explicit and set(permissions[0].get("dataActions") or []) == set(
                    cls.ROLE_DATA_ACTIONS
                    + ["Microsoft.ContainerService/managedClusters/namespaces/read"]
                ))
            )
            and permissions[0].get("notDataActions") == []
            and not permissions[0].get("condition")
        )
        if not compatible:
            raise InvalidArgumentValueError(
                "The existing '{}' role definition is incompatible. Remove "
                "or repair it before retrying; it was not overwritten.".format(
                    cls.ROLE_NAME
                )
            )

    @classmethod
    def _validate_identity(cls, identity, cluster_id, location):
        properties = identity.get("properties") or {}
        if (
            not cls._identity_is_owned(identity, cluster_id)
            or (identity.get("location") or "").lower() != location.lower()
            or not properties.get("clientId")
            or not properties.get("principalId")
            or not properties.get("tenantId")
        ):
            raise InvalidArgumentValueError(
                "The deterministic subscriber managed identity already "
                "exists but is incompatible. It was not overwritten."
            )

    @classmethod
    def _validate_federated_credential(
        cls, federated_credential, issuer, release_namespace
    ):
        properties = federated_credential.get("properties") or {}
        if not (
            properties.get("issuer") == issuer
            and properties.get("subject")
            == cls._federated_credential_subject(release_namespace)
            and properties.get("audiences")
            == [cls.FEDERATED_CREDENTIAL_AUDIENCE]
        ):
            raise InvalidArgumentValueError(
                "The existing subscriber federated credential is "
                "incompatible. It was not overwritten."
            )

    @classmethod
    def _validate_role_assignment(
        cls, role_assignment, role_definition_id, workspace_principal_id
    ):
        properties = role_assignment.get("properties") or {}
        if not (
            cls._same_resource_id(
                properties.get("roleDefinitionId"), role_definition_id
            )
            and properties.get("principalId") == workspace_principal_id
            and properties.get("principalType") == "ServicePrincipal"
            and properties.get("description")
            == cls.ROLE_ASSIGNMENT_DESCRIPTION
        ):
            raise InvalidArgumentValueError(
                "The deterministic AKS role assignment already exists but is "
                "incompatible. It was not overwritten."
            )

    @classmethod
    def _identity_is_owned(cls, identity, cluster_id):
        tags = identity.get("tags") or {}
        return (
            str(tags.get(cls.OWNER_TAG, "")).lower()
            == cls.OWNER_TAG_VALUE
            and cls._same_resource_id(tags.get(cls.CLUSTER_TAG), cluster_id)
        )

    @classmethod
    def _role_definition_body(cls, subscription_id):
        return {
            "properties": {
                "roleName": cls.ROLE_NAME,
                "description": cls.ROLE_DESCRIPTION,
                "type": "CustomRole",
                "permissions": [
                    {
                        "actions": cls.ROLE_ACTIONS,
                        "notActions": [],
                        "dataActions": cls.ROLE_DATA_ACTIONS,
                        "notDataActions": [],
                    }
                ],
                "assignableScopes": [
                    "/subscriptions/{}".format(subscription_id)
                ],
            }
        }

    @classmethod
    def _identity_body(cls, cluster_id, location):
        return {
            "location": location,
            "tags": {
                cls.OWNER_TAG: cls.OWNER_TAG_VALUE,
                cls.CLUSTER_TAG: cluster_id,
            },
        }

    @classmethod
    def _federated_credential_body(cls, issuer, release_namespace):
        return {
            "properties": {
                "issuer": issuer,
                "subject": cls._federated_credential_subject(
                    release_namespace
                ),
                "audiences": [cls.FEDERATED_CREDENTIAL_AUDIENCE],
            }
        }

    @classmethod
    def _federated_credential_subject(cls, release_namespace):
        return "system:serviceaccount:{}:chaos-subscriber".format(
            release_namespace
        )

    @classmethod
    def _resolve_release_namespace(cls, release_namespace):
        return release_namespace or cls.DEFAULT_RELEASE_NAMESPACE

    @classmethod
    def _existing_release_namespace(
        cls, original_extension, original_settings
    ):
        scope = getattr(original_extension, "scope", None)
        cluster_scope = getattr(scope, "cluster", None)
        return cls._resolve_release_namespace(
            getattr(cluster_scope, "release_namespace", None)
            or original_settings.get("namespace")
        )

    @classmethod
    def _role_assignment_body(
        cls, role_definition_id, workspace_principal_id
    ):
        return {
            "properties": {
                "roleDefinitionId": role_definition_id,
                "principalId": workspace_principal_id,
                "principalType": "ServicePrincipal",
                "description": cls.ROLE_ASSIGNMENT_DESCRIPTION,
            }
        }

    @classmethod
    def _prerequisite_resource_ids(
        cls,
        subscription_id,
        resource_group_name,
        cluster_name,
        cluster_id,
    ):
        identity_name = "chaos-subscriber-{}".format(
            hashlib.sha256(cluster_id.lower().encode("utf-8")).hexdigest()
        )
        identity_id = (
            "/subscriptions/{}/resourceGroups/{}/providers/"
            "Microsoft.ManagedIdentity/userAssignedIdentities/{}"
        ).format(subscription_id, resource_group_name, identity_name)
        role_definition_id = (
            "/subscriptions/{}/providers/Microsoft.Authorization/"
            "roleDefinitions/{}"
        ).format(subscription_id, cls.ROLE_DEFINITION_GUID)
        role_assignment_guid = str(
            uuid.uuid5(
                uuid.UUID(cls.ROLE_DEFINITION_GUID),
                cluster_id.lower(),
            )
        )
        return {
            "identity": identity_id,
            "federated_credential": (
                "{}/federatedIdentityCredentials/{}"
            ).format(identity_id, cls.FEDERATED_CREDENTIAL_NAME),
            "role_definition": role_definition_id,
            "role_assignment": (
                "{}/providers/Microsoft.Authorization/roleAssignments/{}"
            ).format(cluster_id, role_assignment_guid),
        }

    @staticmethod
    def _cluster_resource_id(
        subscription_id, resource_group_name, cluster_name
    ):
        return (
            "/subscriptions/{}/resourceGroups/{}/providers/"
            "Microsoft.ContainerService/managedClusters/{}"
        ).format(subscription_id, resource_group_name, cluster_name)

    @staticmethod
    def _same_resource_id(left, right):
        return bool(
            left
            and right
            and left.rstrip("/").lower() == right.rstrip("/").lower()
        )

    @classmethod
    def _validate_cluster_type(cls, cluster_type):
        if cluster_type.lower() != cls.DEFAULT_CLUSTER_TYPE:
            raise InvalidArgumentValueError(
                "Microsoft.ChaosStudio supports only AKS clusters "
                "('--cluster-type managedClusters')."
            )

    @staticmethod
    def _validate_scope(scope):
        if scope is not None and scope.lower() != "cluster":
            raise InvalidArgumentValueError(
                "Microsoft.ChaosStudio supports only cluster scope."
            )

    @staticmethod
    def _warn_ignored_auto_upgrade(
        auto_upgrade_minor_version, auto_upgrade_mode
    ):
        if auto_upgrade_minor_version or auto_upgrade_mode is not None:
            logger.warning(
                "Ignoring auto-upgrade settings because Microsoft.ChaosStudio "
                "requires auto-upgrade-minor-version=false."
            )
