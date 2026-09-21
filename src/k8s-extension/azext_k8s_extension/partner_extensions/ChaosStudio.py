# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import hashlib
import json
import time
import uuid
from urllib.parse import urlsplit

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.core.pipeline.policies import RetryPolicy
from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request, sdk_no_wait
from knack.log import get_logger
from knack.util import CLIError
from ..vendored_sdks.models import Extension, PatchExtension, Scope, ScopeCluster
from .._client_factory import cf_k8s_extension_types
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
    DEFAULT_VERSION = "0.1.6"
    WORKSPACE_ID_KEY = "chaos-workspace-id"
    EXISTING_ROLE_KEY = "chaos-existing-role-definition-id"

    AKS_API_VERSION = "2024-10-01"
    WORKSPACE_API_VERSION = "2026-08-01-preview"
    CONNECTION_API_VERSION = "2026-08-01-preview"
    AUTHORIZATION_API_VERSION = "2022-04-01"
    CONNECTION_KIND = "AksExtension"
    SERVER_ENDPOINT_KEY = "subscriber.serverEndpoint"
    ENABLED_KEY = "subscriber.enabled"
    PENDING_STATES = ("creating", "updating", "accepted", "running", "inprogress")
    MANAGED_KEYS = (
        "subscriber.enabled", "subscriber.serverEndpoint",
        "subscriber.workspaceId", "subscriber.clusterResourceId",
        "workspaceManagedIdentity.objectId",
        "workloadIdentity.enabled", "workloadIdentity.clientId", "workloadIdentity.tenantId",
        "IsWorkloadIdentityEnabled", "IdentityClientId", "IdentityTenantId",
    )

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
        self._reject_managed_overrides(configuration_settings, configuration_protected_settings)
        workspace_id = self._take_workspace_id(
            configuration_settings, configuration_protected_settings
        )
        if not workspace_id:
            raise InvalidArgumentValueError("'chaos-workspace-id' is required.")
        self._validate_version(version or self.DEFAULT_VERSION)
        release_namespace = self._resolve_release_namespace(
            release_namespace
        )
        configuration_settings["subscriber.workspaceId"] = self._validate_workspace_id(workspace_id)
        configuration_settings[self.ENABLED_KEY] = "false"

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

    @classmethod
    def _validate_version(cls, version):
        # Only the coordinated bootstrap contract is known compatible. Availability
        # remains an extension-RP registration check, not a version-number inference.
        if version != cls.DEFAULT_VERSION:
            raise InvalidArgumentValueError(
                "Microsoft.ChaosStudio staged installation requires chart {}. "
                "It must be published and registered before installation.".format(cls.DEFAULT_VERSION)
            )

    @classmethod
    def _reject_managed_overrides(cls, *settings):
        for values in settings:
            conflicts = set(values).intersection(cls.MANAGED_KEYS)
            if conflicts:
                raise InvalidArgumentValueError(
                    "These settings are managed by Microsoft.ChaosStudio: {}.".format(
                        ", ".join(sorted(conflicts))
                    )
                )

    @staticmethod
    def _platform_identity(extension):
        identity = getattr(extension, "aks_assigned_identity", None)
        values = []
        for field in ("principal_id", "tenant_id"):
            value = getattr(identity, field, None)
            try:
                parsed = uuid.UUID(value) if isinstance(value, str) else None
            except ValueError:
                parsed = None
            if not parsed or parsed.int == 0:
                raise AzureResponseError(
                    "Completed extension did not expose a valid aksAssignedIdentity.{}.".format(field)
                )
            values.append(str(parsed))
        return tuple(values)

    @classmethod
    def _stage(cls, extension):
        settings = dict(extension.configuration_settings or {})
        value = settings.get(cls.ENABLED_KEY)
        if value not in ("true", "false") or any(
            key in settings for key in ("workloadIdentity.clientId", "workloadIdentity.tenantId")
        ):
            raise InvalidArgumentValueError(
                "The existing extension is not a staged platform-identity installation. "
                "Automatic migration of older manual identities is not supported."
            )
        cls._validate_version(extension.version)
        return value

    def Install(self, cmd, client, resource_group_name, cluster_rp, cluster_type,
                cluster_name, name, extension, no_wait=False):
        """Bootstrap and activate one extension; persisted ARM state is the resume record."""
        args = (resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        arm = self._arm_client_factory(cmd)
        cluster_id = self._cluster_resource_id(arm.subscription_id, resource_group_name, cluster_name)
        extension_id = "{}/providers/Microsoft.KubernetesConfiguration/extensions/{}".format(cluster_id, name)
        workspace_id = extension.configuration_settings["subscriber.workspaceId"]
        connection_id = "{}/connections/{}".format(
            workspace_id, self._recommended_connection_name(workspace_id, cluster_id)
        )
        phase = "inspection"
        try:
            versions = cf_k8s_extension_types(cmd.cli_ctx).cluster_list_versions(
                resource_group_name, cluster_rp, cluster_type, cluster_name,
                "Microsoft.ChaosStudio", release_train=extension.release_train,
            )
            if not any(item.properties.version == extension.version for item in versions):
                raise InvalidArgumentValueError(
                    "Bootstrap chart {} is not registered for this cluster/train.".format(extension.version)
                )
            try:
                existing = client.get(*args)
            except ResourceNotFoundError:
                existing = None
            connection = arm.get(connection_id, self.CONNECTION_API_VERSION,
                                 "Chaos Studio workspace connection", allow_not_found=True)
            if existing is not None:
                self._validate_existing(existing, extension, cluster_id)
                stage = self._stage(existing)
                if stage == "true":
                    self._check_active_connection(existing, connection, workspace_id, cluster_id)
                    if self._state(existing) == "succeeded":
                        return existing
                    if self._state(existing) not in ("failed", "canceled", "cancelled"):
                        if no_wait:
                            return existing
                        final = self._wait_existing(cmd, client, args)
                        self._check_active_connection(final, connection, workspace_id, cluster_id)
                        return final
                elif self._state(existing) not in ("succeeded", "failed", "canceled", "cancelled"):
                    existing = self._wait_existing(cmd, client, args)
                if connection is not None:
                    principal, tenant = self._platform_identity(existing)
                    self._connection_endpoint(connection, cluster_id, principal, tenant)
                # Creation on rerun is not a settings-update interface.
                extension = existing
            elif connection is not None:
                raise InvalidArgumentValueError(
                    "A connection already exists without its extension; refusing to adopt its identity."
                )

            phase = "workspace permissions"
            settings = dict(extension.configuration_settings or {})
            settings.update(self._reconcile_prerequisites(
                cmd, resource_group_name, cluster_name, workspace_id,
                self._existing_release_namespace(extension, settings),
                settings.get(self.EXISTING_ROLE_KEY),
            ))
            phase = "bootstrap"
            if existing is None or (
                self._stage(existing) == "false" and self._state(existing) != "succeeded"
            ):
                settings[self.ENABLED_KEY] = "false"
                settings.pop(self.SERVER_ENDPOINT_KEY, None)
                extension.configuration_settings = settings
                LongRunningOperation(cmd.cli_ctx)(client.begin_create(*args, extension))
                existing = client.get(*args)
                self._require_success(existing)

            phase = "connection"
            principal, tenant = self._platform_identity(existing)
            endpoint = self._reconcile_workspace_connection(
                arm, workspace_id, cluster_id, principal, tenant
            )
            if self._stage(existing) == "true" and (
                existing.configuration_settings.get(self.SERVER_ENDPOINT_KEY) != endpoint
            ):
                raise InvalidArgumentValueError("The active endpoint conflicts with its workspace connection.")
            phase = "activation"
            settings[self.ENABLED_KEY] = "true"
            settings[self.SERVER_ENDPOINT_KEY] = endpoint
            update = PatchExtension(configuration_settings=settings)
            # Protected settings are deliberately omitted: GET cannot reconstruct secrets.
            result = sdk_no_wait(no_wait, client.begin_update, *args, update)
            if no_wait:
                logger.warning("Chaos bootstrap is complete; subscriber activation is still in progress.")
                return result
            LongRunningOperation(cmd.cli_ctx)(result)
            final = client.get(*args)
            self._require_success(final)
            if self._platform_identity(final) != (principal, tenant):
                raise AzureResponseError("Platform identity changed during activation; connection was retained.")
            if self._stage(final) != "true" or final.configuration_settings.get(self.SERVER_ENDPOINT_KEY) != endpoint:
                raise AzureResponseError("Completed activation does not match the requested subscriber settings.")
            return final
        except (CLIError, AzureError, ValueError) as error:
            raise AzureResponseError(
                "Chaos {} failed. Extension '{}', connection '{}' and workspace permissions "
                "were retained; rerun after correcting the error. {}".format(
                    phase, extension_id, connection_id, error
                )
            ) from error

    @staticmethod
    def _state(extension):
        state = getattr(extension, "provisioning_state", "") or ""
        return str(getattr(state, "value", state)).lower()

    @classmethod
    def _require_success(cls, extension):
        if cls._state(extension) != "succeeded":
            raise AzureResponseError(
                "Extension operation ended in state '{}'.".format(cls._state(extension))
            )

    def _wait_existing(self, cmd, client, args):
        # Resume has no LRO continuation token. Poll the existing resource with
        # the SDK's cadence and retry policy, never submitting another mutation.
        while True:
            delays = []

            def read_response(response, value, _):
                delays.append(RetryPolicy().get_retry_after(response))
                return value

            existing = client.get(*args, cls=read_response)
            state = self._state(existing)
            if state in ("succeeded", "failed", "canceled", "cancelled"):
                self._require_success(existing)
                return existing
            if state not in self.PENDING_STATES:
                raise AzureResponseError("Cannot resume extension state '{}'.".format(state))
            retry_after = delays[0]
            delay = retry_after if retry_after is not None else client._config.polling_interval  # pylint: disable=protected-access
            time.sleep(delay)

    def _validate_existing(self, existing, requested, cluster_id):
        settings = dict(existing.configuration_settings or {})
        if (str(existing.extension_type).lower() != "microsoft.chaosstudio"
                or self._state(existing) not in self.PENDING_STATES + ("succeeded", "failed", "canceled", "cancelled")
                or not self._same_resource_id(settings.get("subscriber.workspaceId"),
                                              requested.configuration_settings["subscriber.workspaceId"])
                or not self._same_resource_id(settings.get("subscriber.clusterResourceId"), cluster_id)
                or self._existing_release_namespace(existing, settings)
                != self._existing_release_namespace(requested, requested.configuration_settings)
                or existing.version != requested.version
                or existing.release_train != requested.release_train):
            raise InvalidArgumentValueError("Existing extension ownership, namespace, version or state conflicts.")
        for key, value in requested.configuration_settings.items():
            if key not in self.MANAGED_KEYS and settings.get(key) != value:
                raise InvalidArgumentValueError("Resume cannot change setting '{}'; use update after completion.".format(key))
        if requested.configuration_protected_settings:
            raise InvalidArgumentValueError("Resume cannot replace protected settings; use update after completion.")

    def _check_active_connection(self, extension, connection, workspace_id, cluster_id):
        principal, tenant = self._platform_identity(extension)
        endpoint = self._connection_endpoint(connection, cluster_id, principal, tenant)
        if extension.configuration_settings.get(self.SERVER_ENDPOINT_KEY) != endpoint:
            raise InvalidArgumentValueError("Installed endpoint conflicts with the workspace connection.")

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
        """Update only an already active platform-identity installation."""
        self._warn_ignored_auto_upgrade(
            auto_upgrade_minor_version, auto_upgrade_mode
        )
        supplied_settings = dict(configuration_settings or {})
        configuration_protected_settings = dict(
            configuration_protected_settings or {}
        )
        self._reject_managed_overrides(supplied_settings, configuration_protected_settings)
        self._validate_version(version or original_extension.version)
        if self._stage(original_extension) != "true":
            raise InvalidArgumentValueError("Resume bootstrap with create before updating settings.")
        self._require_success(original_extension)
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
            arm = self._arm_client_factory(cmd)
            cluster_id = self._cluster_resource_id(arm.subscription_id, resource_group_name, cluster_name)
            connection = arm.get(
                "{}/connections/{}".format(workspace_id, self._recommended_connection_name(workspace_id, cluster_id)),
                self.CONNECTION_API_VERSION, "Chaos Studio workspace connection"
            )
            self._check_active_connection(original_extension, connection, workspace_id, cluster_id)
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
        self._validate_cluster(cluster)
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

        return {
            "workspaceManagedIdentity.objectId": workspace_principal_id,
            "subscriber.workspaceId": workspace_id,
            "subscriber.clusterResourceId": cluster_id,
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
        return cls._connection_endpoint(connection, cluster_id, principal_id, tenant_id)

    @classmethod
    def _connection_endpoint(cls, connection, cluster_id, principal_id, tenant_id):
        if not isinstance(connection, dict):
            raise AzureResponseError(
                "The Chaos Studio workspace connection returned an "
                "invalid response."
            )
        properties = connection.get("properties") or {}
        if not (
            properties.get("kind") == cls.CONNECTION_KIND
            and cls._same_resource_id(
                properties.get("targetResourceId"),
                cluster_id,
            )
            and cls._same_identifier(
                properties.get("principalId"), principal_id
            )
            and cls._same_identifier(
                properties.get("tenantId"), tenant_id
            )
        ):
            raise AzureResponseError(
                "The Chaos Studio workspace connection response did not "
                "match the requested immutable trust keys."
            )

        endpoint = properties.get("dataPlaneEndpoint")
        uri = urlsplit(endpoint) if isinstance(endpoint, str) else None
        if (not uri or uri.scheme != "https" or not uri.hostname
                or uri.username or uri.password or uri.fragment):
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
        self._stage(extension)
        if self._state(extension) not in ("succeeded", "failed", "canceled", "cancelled"):
            raise InvalidArgumentValueError("Wait for the extension operation before deleting workspace resources.")
        workspace_id = settings.get("subscriber.workspaceId")
        managed_keys = (
            "subscriber.workspaceId",
            "subscriber.clusterResourceId",
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

        principal_id, tenant_id = self._platform_identity(extension)

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
                principal_id,
            )
            and self._same_identifier(
                properties.get("tenantId"),
                tenant_id,
            )
        ):
            raise InvalidArgumentValueError(
                "The Chaos Studio workspace connection does not match the "
                "installed extension and its platform subscriber identity. It "
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
