# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-branches, too-many-boolean-expressions, no-else-return, logging-fstring-interpolation, too-many-locals, expression-not-assigned, too-many-public-methods

from copy import deepcopy
from typing import Dict, Any
from urllib.parse import urlparse

from azure.cli.command_modules.containerapp._validators import validate_revision_suffix
from azure.cli.core.commands import AzCliCommand

import time

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ValidationError,
    ArgumentUsageError,
    ResourceNotFoundError,
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError)
from azure.cli.command_modules.containerapp.containerapp_decorator import BaseContainerAppDecorator, ContainerAppCreateDecorator
from azure.cli.command_modules.containerapp._github_oauth import cache_github_token
from azure.cli.command_modules.containerapp._utils import (store_as_secret_and_return_secret_ref, parse_env_var_flags,
                                                           _convert_object_from_snake_to_camel_case,
                                                           _object_to_dict, _remove_additional_attributes,
                                                           _remove_readonly_attributes,
                                                           is_registry_msi_system, validate_container_app_name, AppType,
                                                           safe_set, parse_metadata_flags, parse_auth_flags,
                                                           ensure_workload_profile_supported, _generate_secret_volume_name,
                                                           safe_get, _update_revision_env_secretrefs, _add_or_update_tags, _populate_secret_values,
                                                           clean_null_values, _add_or_update_env_vars, _remove_env_vars, _get_acr_cred, _ensure_identity_resource_id,
                                                           create_acrpull_role_assignment, _ensure_location_allowed, get_default_workload_profile_name_from_env,
                                                           set_managed_identity, parse_secret_flags, _infer_acr_credentials, _remove_registry_secret)
from azure.cli.command_modules.containerapp._constants import (CONTAINER_APPS_RP)
from azure.cli.command_modules.containerapp._models import (
    Ingress as IngressModel,
    Configuration as ConfigurationModel,
    Template as TemplateModel,
    Dapr as DaprModel,
    ManagedServiceIdentity as ManagedServiceIdentityModel,
)

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.mgmt.core.tools import parse_resource_id, is_valid_resource_id

from knack.log import get_logger
from knack.util import CLIError

from msrest.exceptions import DeserializationError

from ._clients import ManagedEnvironmentClient, ConnectedEnvironmentClient, ManagedEnvironmentPreviewClient
from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception, get_linker_client
from ._models import (
    RegistryCredentials as RegistryCredentialsModel,
    ContainerResources as ContainerResourcesModel,
    Scale as ScaleModel,
    Container as ContainerModel,
    ScaleRule as ScaleRuleModel,
    Service as ServiceModel,
    Volume as VolumeModel,
    VolumeMount as VolumeMountModel,
    RuntimeJava as RuntimeJavaModel)

from ._decorator_utils import (create_deserializer,
                               process_loaded_yaml,
                               load_yaml_file,
                               infer_runtime_option
                               )
from ._utils import parse_service_bindings, check_unique_bindings, is_registry_msi_system_environment, \
    env_has_managed_identity, create_acrpull_role_assignment_if_needed, is_cloud_supported_by_service_connector
from ._validators import validate_create, validate_runtime
from ._constants import (HELLO_WORLD_IMAGE,
                         CONNECTED_ENVIRONMENT_TYPE,
                         CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                         MANAGED_ENVIRONMENT_TYPE,
                         MANAGED_ENVIRONMENT_RESOURCE_TYPE, ACR_IMAGE_SUFFIX,
                         RUNTIME_JAVA)


logger = get_logger(__name__)


class ContainerAppUpdateDecorator(BaseContainerAppDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerapp_def = {}
        self.new_containerapp = {}

    # move list_secrets to BaseContainerAppDecorator when move ContainerAppUpdateDecorator to Core CLI
    def list_secrets(self, show_values=False):
        containerapp_def = None
        try:
            containerapp_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not containerapp_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(self.get_argument_name()))

        if not show_values:
            return safe_get(containerapp_def, "properties", "configuration", "secrets", default=[])

        try:
            return self.client.list_secrets(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())["value"]
        except Exception as e:
            handle_non_404_status_code_exception(e)

    def set_argument_container_name(self, container_name):
        self.set_param("container_name", container_name)

    def get_argument_show_values(self):
        return self.get_param("show_values")

    def get_argument_set_env_vars(self):
        return self.get_param("set_env_vars")

    def get_argument_remove_env_vars(self):
        return self.get_param("remove_env_vars")

    def get_argument_replace_env_vars(self):
        return self.get_param("replace_env_vars")

    def get_argument_remove_all_env_vars(self):
        return self.get_param("remove_all_env_vars")

    def get_argument_from_revision(self):
        return self.get_param("from_revision")

    def get_argument_target_label(self):
        return self.get_param("target_label")

    def validate_arguments(self):
        self.containerapp_def = None
        try:
            self.containerapp_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not self.containerapp_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(self.get_argument_name()))

        validate_revision_suffix(self.get_argument_revision_suffix())
        # Validate that max_replicas is set to 0-1000
        if self.get_argument_max_replicas() is not None:
            if self.get_argument_max_replicas() < 1 or self.get_argument_max_replicas() > 1000:
                raise ArgumentUsageError('--max-replicas must be in the range [1,1000]')

    def update(self):
        try:
            r = self.client.update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name(), container_app_envelope=self.new_containerapp,
                no_wait=self.get_argument_no_wait())
            if not self.get_argument_no_wait() and "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting":
                logger.warning('Containerapp update in progress. Please monitor the update using `az containerapp show -n {} -g {}`'.format(self.get_argument_name(), self.get_argument_resource_group_name()))
            return r
        except Exception as e:
            handle_raw_exception(e)

    def set_up_from_revision(self):
        if self.get_argument_from_revision():
            r = None
            try:
                r = self.client.show_revision(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), container_app_name=self.get_argument_name(), name=self.get_argument_from_revision())
            except CLIError as e:
                handle_non_404_status_code_exception(e)

            _update_revision_env_secretrefs(r["properties"]["template"]["containers"], self.get_argument_name())
            safe_set(self.new_containerapp, "properties", "template", value=r["properties"]["template"])

    def _need_update_container(self):
        return self.get_argument_image() or self.get_argument_container_name() or self.get_argument_set_env_vars() is not None or self.get_argument_remove_env_vars() is not None or self.get_argument_replace_env_vars() is not None or self.get_argument_remove_all_env_vars() or self.get_argument_cpu() or self.get_argument_memory() or self.get_argument_startup_command() is not None or self.get_argument_args() is not None or self.get_argument_secret_volume_mount() is not None

    def construct_payload(self):
        # construct from yaml
        if self.get_argument_yaml():
            return self.set_up_update_containerapp_yaml(name=self.get_argument_name(), file_name=self.get_argument_yaml())

        self.new_containerapp["properties"] = {}

        self.set_up_from_revision()

        # Doing this while API has bug. If env var is an empty string, API doesn't return "value" even though the "value" should be an empty string
        for container in safe_get(self.containerapp_def, "properties", "template", "containers", default=[]):
            if "env" in container:
                for e in container["env"]:
                    if "value" not in e:
                        e["value"] = ""

        update_map = {}
        update_map['scale'] = self.get_argument_min_replicas() is not None or self.get_argument_max_replicas() is not None or self.get_argument_scale_rule_name()
        update_map['container'] = self._need_update_container()
        update_map['ingress'] = self.get_argument_ingress() or self.get_argument_target_port()
        update_map['registry'] = self.get_argument_registry_server() or self.get_argument_registry_user() or self.get_argument_registry_pass() or self.get_argument_registry_identity()

        if self.get_argument_tags():
            _add_or_update_tags(self.new_containerapp, self.get_argument_tags())

        if self.get_argument_revision_suffix() is not None:
            self.new_containerapp["properties"]["template"] = {} if "template" not in self.new_containerapp["properties"] else self.new_containerapp["properties"]["template"]
            self.new_containerapp["properties"]["template"]["revisionSuffix"] = self.get_argument_revision_suffix()

        if self.get_argument_termination_grace_period() is not None:
            safe_set(self.new_containerapp, "properties", "template", "terminationGracePeriodSeconds",
                     value=self.get_argument_termination_grace_period())

        if self.get_argument_workload_profile_name():
            self.new_containerapp["properties"]["workloadProfileName"] = self.get_argument_workload_profile_name()

            parsed_managed_env = parse_resource_id(self.containerapp_def["properties"]["environmentId"])
            managed_env_name = parsed_managed_env['name']
            managed_env_rg = parsed_managed_env['resource_group']
            managed_env_info = None
            try:
                managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)
            except Exception as e:
                handle_non_404_status_code_exception(e)

            if not managed_env_info:
                raise ValidationError(
                    "Error parsing the managed environment '{}' from the specified containerapp".format(
                        managed_env_name))

            ensure_workload_profile_supported(self.cmd, managed_env_name, managed_env_rg, self.get_argument_workload_profile_name(),
                                              managed_env_info)

        # Containers
        if update_map["container"]:
            self.new_containerapp["properties"]["template"] = {} if "template" not in self.new_containerapp["properties"] else self.new_containerapp["properties"]["template"]
            self.new_containerapp["properties"]["template"]["containers"] = self.containerapp_def["properties"]["template"]["containers"]
            if not self.get_argument_container_name():
                if len(self.new_containerapp["properties"]["template"]["containers"]) == 1:
                    container_name = self.new_containerapp["properties"]["template"]["containers"][0]["name"]
                    self.set_argument_container_name(container_name)
                else:
                    raise ValidationError(
                        "Usage error: --container-name is required when adding or updating a container")

            # Check if updating existing container
            updating_existing_container = self.set_up_existing_container_update()
            # If not updating existing container, add as new container
            if not updating_existing_container:
                if self.get_argument_image() is None:
                    raise ValidationError("Usage error: --image is required when adding a new container")

                resources_def = None
                if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
                    resources_def = ContainerResourcesModel
                    resources_def["cpu"] = self.get_argument_cpu()
                    resources_def["memory"] = self.get_argument_memory()

                container_def = ContainerModel
                container_def["name"] = self.get_argument_container_name()
                container_def["image"] = self.get_argument_image()
                container_def["env"] = []

                if self.get_argument_set_env_vars() is not None:
                    # env vars
                    _add_or_update_env_vars(container_def["env"], parse_env_var_flags(self.get_argument_set_env_vars()))

                if self.get_argument_replace_env_vars() is not None:
                    # env vars
                    _add_or_update_env_vars(container_def["env"], parse_env_var_flags(self.get_argument_replace_env_vars()))

                if self.get_argument_remove_env_vars() is not None:
                    # env vars
                    _remove_env_vars(container_def["env"], self.get_argument_remove_env_vars())

                if self.get_argument_remove_all_env_vars():
                    container_def["env"] = []

                if self.get_argument_startup_command() is not None:
                    if isinstance(self.get_argument_startup_command(), list) and not self.get_argument_startup_command():
                        container_def["command"] = None
                    else:
                        container_def["command"] = self.get_argument_startup_command()
                if self.get_argument_args() is not None:
                    if isinstance(self.get_argument_args(), list) and not self.get_argument_args():
                        container_def["args"] = None
                    else:
                        container_def["args"] = self.get_argument_args()
                if resources_def is not None:
                    container_def["resources"] = resources_def
                if self.get_argument_secret_volume_mount() is not None:
                    self.new_containerapp["properties"]["template"]["volumes"] = self.containerapp_def["properties"]["template"]["volumes"]
                    # generate a new volume name
                    volume_def = VolumeModel
                    volume_mount_def = VolumeMountModel
                    volume_def["name"] = _generate_secret_volume_name()
                    volume_def["storageType"] = "Secret"

                    # mount the volume to the container
                    volume_mount_def["volumeName"] = volume_def["name"]
                    volume_mount_def["mountPath"] = self.get_argument_secret_volume_mount()
                    container_def["volumeMounts"] = [volume_mount_def]
                    if "volumes" not in self.new_containerapp["properties"]["template"]:
                        self.new_containerapp["properties"]["template"]["volumes"] = [volume_def]
                    else:
                        self.new_containerapp["properties"]["template"]["volumes"].append(volume_def)

                self.new_containerapp["properties"]["template"]["containers"].append(container_def)
        # Scale
        if update_map["scale"]:
            self.new_containerapp["properties"]["template"] = {} if "template" not in self.new_containerapp["properties"] else self.new_containerapp["properties"]["template"]
            if "scale" not in self.new_containerapp["properties"]["template"]:
                self.new_containerapp["properties"]["template"]["scale"] = {}
            if self.get_argument_min_replicas() is not None:
                self.new_containerapp["properties"]["template"]["scale"]["minReplicas"] = self.get_argument_min_replicas()
            if self.get_argument_max_replicas() is not None:
                self.new_containerapp["properties"]["template"]["scale"]["maxReplicas"] = self.get_argument_max_replicas()

        scale_def = None
        if self.get_argument_min_replicas() is not None or self.get_argument_max_replicas() is not None:
            scale_def = ScaleModel
            scale_def["minReplicas"] = self.get_argument_min_replicas()
            scale_def["maxReplicas"] = self.get_argument_max_replicas()
        # so we don't overwrite rules
        if safe_get(self.new_containerapp, "properties", "template", "scale", "rules"):
            self.new_containerapp["properties"]["template"]["scale"].pop(["rules"])
        scale_rule_type = self.get_argument_scale_rule_type()
        if self.get_argument_scale_rule_name():
            if not scale_rule_type:
                scale_rule_type = "http"
            scale_rule_type = scale_rule_type.lower()
            scale_rule_def = deepcopy(ScaleRuleModel)
            curr_metadata = {}
            if self.get_argument_scale_rule_http_concurrency():
                if scale_rule_type == 'http':
                    curr_metadata["concurrentRequests"] = str(self.get_argument_scale_rule_http_concurrency())
                elif scale_rule_type == 'tcp':
                    curr_metadata["concurrentConnections"] = str(self.get_argument_scale_rule_http_concurrency())
            metadata_def = parse_metadata_flags(self.get_argument_scale_rule_metadata(), curr_metadata)
            auth_def = parse_auth_flags(self.get_argument_scale_rule_auth())
            if scale_rule_type == "http":
                scale_rule_def["name"] = self.get_argument_scale_rule_name()
                scale_rule_def["custom"] = None
                scale_rule_def["tcp"] = None
                scale_rule_def["http"] = {}
                scale_rule_def["http"]["metadata"] = metadata_def
                scale_rule_def["http"]["auth"] = auth_def
            elif scale_rule_type == "tcp":
                scale_rule_def["name"] = self.get_argument_scale_rule_name()
                scale_rule_def["custom"] = None
                scale_rule_def["http"] = None
                scale_rule_def["tcp"] = {}
                scale_rule_def["tcp"]["metadata"] = metadata_def
                scale_rule_def["tcp"]["auth"] = auth_def
            else:
                scale_rule_def["name"] = self.get_argument_scale_rule_name()
                scale_rule_def["http"] = None
                scale_rule_def["tcp"] = None
                scale_rule_def["custom"] = {}
                scale_rule_def["custom"]["type"] = scale_rule_type
                scale_rule_def["custom"]["metadata"] = metadata_def
                scale_rule_def["custom"]["auth"] = auth_def
            if not scale_def:
                scale_def = ScaleModel
            scale_def["rules"] = [scale_rule_def]
            self.new_containerapp["properties"]["template"]["scale"]["rules"] = scale_def["rules"]
        # Ingress
        if update_map["ingress"]:
            self.new_containerapp["properties"]["configuration"] = {} if "configuration" not in self.new_containerapp[
                "properties"] else self.new_containerapp["properties"]["configuration"]
            if self.get_argument_target_port() is not None or self.get_argument_ingress() is not None:
                self.new_containerapp["properties"]["configuration"]["ingress"] = {}
                if self.get_argument_ingress():
                    self.new_containerapp["properties"]["configuration"]["ingress"][
                        "external"] = self.get_argument_ingress().lower() == "external"
                if self.get_argument_target_port():
                    self.new_containerapp["properties"]["configuration"]["ingress"]["targetPort"] = self.get_argument_target_port()

        # Registry
        if update_map["registry"]:  # pylint: disable=too-many-nested-blocks
            self.new_containerapp["properties"]["configuration"] = {} if "configuration" not in self.new_containerapp[
                "properties"] else self.new_containerapp["properties"]["configuration"]
            if "registries" in self.containerapp_def["properties"]["configuration"]:
                self.new_containerapp["properties"]["configuration"]["registries"] = self.containerapp_def["properties"]["configuration"]["registries"]
            if "registries" not in self.containerapp_def["properties"]["configuration"] or \
                    self.containerapp_def["properties"]["configuration"]["registries"] is None:
                self.new_containerapp["properties"]["configuration"]["registries"] = []

            registries_def = self.new_containerapp["properties"]["configuration"]["registries"]

            self.set_up_get_existing_secrets(self.containerapp_def)
            if "secrets" in self.containerapp_def["properties"]["configuration"] and self.containerapp_def["properties"]["configuration"]["secrets"]:
                self.new_containerapp["properties"]["configuration"]["secrets"] = self.containerapp_def["properties"]["configuration"]["secrets"]
            else:
                self.new_containerapp["properties"]["configuration"]["secrets"] = []

            if self.get_argument_registry_server():
                if (not self.get_argument_registry_pass() or not self.get_argument_registry_user()) and not self.get_argument_registry_identity():
                    if ACR_IMAGE_SUFFIX not in self.get_argument_registry_server():
                        raise RequiredArgumentMissingError(
                            'Registry url is required if using Azure Container Registry, otherwise Registry username and password are required if using Dockerhub')
                    logger.warning(
                        'No credential was provided to access Azure Container Registry. Trying to look up...')
                    parsed = urlparse(self.get_argument_registry_server())
                    registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]
                    registry_user, registry_pass, _ = _get_acr_cred(self.cmd.cli_ctx, registry_name)
                    self.set_argument_registry_user(registry_user)
                    self.set_argument_registry_pass(registry_pass)

                # Check if updating existing registry
                updating_existing_registry = False
                for r in registries_def:
                    if r['server'].lower() == self.get_argument_registry_server().lower():
                        updating_existing_registry = True
                        # registry (username and password) and identity are mutually exclusive, set identity to None when setting username or password
                        if (self.get_argument_registry_user() or self.get_argument_registry_pass()) and self.get_argument_registry_identity() is None:
                            r["identity"] = None
                        if self.get_argument_registry_user():
                            r["username"] = self.get_argument_registry_user()
                        if self.get_argument_registry_pass():
                            r["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                                self.new_containerapp["properties"]["configuration"]["secrets"],
                                r["username"],
                                r["server"],
                                self.get_argument_registry_pass(),
                                update_existing_secret=True,
                                disable_warnings=True)
                        if self.get_argument_registry_identity():
                            r["identity"] = self.get_argument_registry_identity()
                            if r["username"]:
                                _remove_registry_secret(containerapp_def=self.new_containerapp, server=r["server"], username=r["username"])
                            r["username"] = None
                            r["passwordSecretRef"] = None

                # If not updating existing registry, add as new registry
                if not updating_existing_registry:
                    registry = RegistryCredentialsModel
                    registry["server"] = self.get_argument_registry_server()
                    registry["username"] = self.get_argument_registry_user()
                    registry["identity"] = self.get_argument_registry_identity()
                    if self.get_argument_registry_pass():
                        registry["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                            self.new_containerapp["properties"]["configuration"]["secrets"],
                            self.get_argument_registry_user(),
                            self.get_argument_registry_server(),
                            self.get_argument_registry_pass(),
                            update_existing_secret=True,
                            disable_warnings=True)

                    registries_def.append(registry)

        if not self.get_argument_revision_suffix():
            safe_set(self.new_containerapp, "properties", "template", "revisionSuffix", value=None)

        if self.get_argument_revisions_mode():
            safe_set(self.new_containerapp, "properties", "configuration", "activeRevisionsMode", value=self.get_argument_revisions_mode())

        if self.get_argument_target_label():
            safe_set(self.new_containerapp, "properties", "configuration", "targetLabel", value=self.get_argument_target_label())

    def set_up_update_containerapp_yaml(self, name, file_name):
        if self.get_argument_image() or self.get_argument_min_replicas() or self.get_argument_max_replicas() or \
                self.get_argument_set_env_vars() or self.get_argument_remove_env_vars() or self.get_argument_replace_env_vars() or self.get_argument_remove_all_env_vars() or self.get_argument_cpu() or self.get_argument_memory() or \
                self.get_argument_startup_command() or self.get_argument_args() or self.get_argument_tags() or self.get_argument_revisions_mode() or self.get_argument_target_label():
            logger.warning(
                'Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')
        yaml_containerapp = process_loaded_yaml(load_yaml_file(file_name))
        if not isinstance(yaml_containerapp, dict):  # pylint: disable=unidiomatic-typecheck
            raise ValidationError(
                'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')

        if not yaml_containerapp.get('name'):
            yaml_containerapp['name'] = name
        elif yaml_containerapp.get('name').lower() != name.lower():
            logger.warning(
                'The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
                    yaml_containerapp.get('name'), name))
        name = yaml_containerapp.get('name')

        if not yaml_containerapp.get('type'):
            yaml_containerapp['type'] = 'Microsoft.App/containerApps'
        elif yaml_containerapp.get('type').lower() != "microsoft.app/containerapps":
            raise ValidationError('Containerapp type must be \"Microsoft.App/ContainerApps\"')

        # Check if containerapp exists
        try:
            self.new_containerapp = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not self.new_containerapp:
            raise ValidationError("The containerapp '{}' does not exist".format(name))
        existed_environment_id = self.new_containerapp['properties']['environmentId']
        self.new_containerapp = None

        # Deserialize the yaml into a ContainerApp object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)
            self.new_containerapp = deserializer('ContainerApp', yaml_containerapp)
        except DeserializationError as ex:
            raise ValidationError(
                'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.') from ex

        # Remove tags before converting from snake case to camel case, then re-add tags. We don't want to change the case of the tags. Need this since we're not using SDK
        tags = None
        if yaml_containerapp.get('tags'):
            tags = yaml_containerapp.get('tags')
            del yaml_containerapp['tags']

        # Save customizedKeys before converting from snake case to camel case, then re-add customizedKeys. We don't want to change the case of the customizedKeys.
        service_binds = safe_get(yaml_containerapp, "properties", "template", "serviceBinds", default=[])
        customized_keys_dict = {}
        for bind in service_binds:
            if bind.get("name") and bind.get("customizedKeys"):
                customized_keys_dict[bind["name"]] = bind["customizedKeys"]

        self.new_containerapp = _convert_object_from_snake_to_camel_case(_object_to_dict(self.new_containerapp))
        self.new_containerapp['tags'] = tags

        # Containerapp object is deserialized from 'ContainerApp' model, "Properties" level is lost after deserialization
        # We try to get serviceBinds from 'properties.template.serviceBinds' first, if not exists, try 'template.serviceBinds'
        service_binds = safe_get(self.new_containerapp, "properties", "template", "serviceBinds") or safe_get(self.new_containerapp, "template", "serviceBinds")
        if service_binds:
            for bind in service_binds:
                bind["customizedKeys"] = customized_keys_dict.get(bind["name"])

        # After deserializing, some properties may need to be moved under the "properties" attribute. Need this since we're not using SDK
        self.new_containerapp = process_loaded_yaml(self.new_containerapp)

        # Change which revision we update from
        if self.get_argument_from_revision():
            r = self.client.show_revision(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), container_app_name=name, name=self.get_argument_from_revision())
            _update_revision_env_secretrefs(r["properties"]["template"]["containers"], name)
            self.new_containerapp["properties"]["template"] = r["properties"]["template"]

        # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
        _remove_additional_attributes(self.new_containerapp)
        _remove_readonly_attributes(self.new_containerapp)

        secret_values = self.list_secrets(show_values=True)
        _populate_secret_values(self.new_containerapp, secret_values)

        # Clean null values since this is an update
        self.new_containerapp = clean_null_values(self.new_containerapp)

        # Fix bug with revisionSuffix when containers are added
        if not safe_get(self.new_containerapp, "properties", "template", "revisionSuffix"):
            if "properties" not in self.new_containerapp:
                self.new_containerapp["properties"] = {}
            if "template" not in self.new_containerapp["properties"]:
                self.new_containerapp["properties"]["template"] = {}
            self.new_containerapp["properties"]["template"]["revisionSuffix"] = None

        # Remove the environmentId in the PATCH payload if it has not been changed
        if safe_get(self.new_containerapp, "properties", "environmentId") and safe_get(self.new_containerapp, "properties", "environmentId").lower() == existed_environment_id.lower():
            del self.new_containerapp["properties"]['environmentId']

    def set_up_existing_container_update(self):
        updating_existing_container = False
        for c in self.new_containerapp["properties"]["template"]["containers"]:  # pylint: disable=too-many-nested-blocks
            # Update existing container if container name matches the argument container name
            if self.should_update_existing_container(c):
                updating_existing_container = True

                if self.get_argument_image() is not None:
                    c["image"] = self.get_argument_image()

                if self.get_argument_set_env_vars() is not None:
                    if "env" not in c or not c["env"]:
                        c["env"] = []
                    # env vars
                    _add_or_update_env_vars(c["env"], parse_env_var_flags(self.get_argument_set_env_vars()))

                if self.get_argument_replace_env_vars() is not None:
                    # Remove other existing env_vars, then add them
                    c["env"] = []
                    _add_or_update_env_vars(c["env"], parse_env_var_flags(self.get_argument_replace_env_vars()))

                if self.get_argument_remove_env_vars() is not None:
                    if "env" not in c or not c["env"]:
                        c["env"] = []
                    # env vars
                    _remove_env_vars(c["env"], self.get_argument_remove_env_vars())

                if self.get_argument_remove_all_env_vars():
                    c["env"] = []

                if self.get_argument_startup_command() is not None:
                    if isinstance(self.get_argument_startup_command(), list) and not self.get_argument_startup_command():
                        c["command"] = None
                    else:
                        c["command"] = self.get_argument_startup_command()
                if self.get_argument_args() is not None:
                    if isinstance(self.get_argument_args(), list) and not self.get_argument_args():
                        c["args"] = None
                    else:
                        c["args"] = self.get_argument_args()
                if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
                    if "resources" in c and c["resources"]:
                        if self.get_argument_cpu() is not None:
                            c["resources"]["cpu"] = self.get_argument_cpu()
                        if self.get_argument_memory() is not None:
                            c["resources"]["memory"] = self.get_argument_memory()
                    else:
                        c["resources"] = {
                            "cpu": self.get_argument_cpu(),
                            "memory": self.get_argument_memory()
                        }
                if self.get_argument_secret_volume_mount() is not None:
                    self.new_containerapp["properties"]["template"]["volumes"] = self.containerapp_def["properties"]["template"]["volumes"]
                    if "volumeMounts" not in c or not c["volumeMounts"]:
                        # if no volume mount exists, create a new volume and then mount
                        volume_def = VolumeModel
                        volume_mount_def = VolumeMountModel
                        volume_def["name"] = _generate_secret_volume_name()
                        volume_def["storageType"] = "Secret"

                        volume_mount_def["volumeName"] = volume_def["name"]
                        volume_mount_def["mountPath"] = self.get_argument_secret_volume_mount()

                        if "volumes" not in self.new_containerapp["properties"]["template"] or self.new_containerapp["properties"]["template"]["volumes"] is None:
                            self.new_containerapp["properties"]["template"]["volumes"] = [volume_def]
                        else:
                            self.new_containerapp["properties"]["template"]["volumes"].append(volume_def)
                        c["volumeMounts"] = [volume_mount_def]
                    else:
                        if len(c["volumeMounts"]) > 1:  # pylint: disable=no-else-raise
                            raise ValidationError(
                                "Usage error: --secret-volume-mount can only be used with a container that has a single volume mount, to define multiple volumes and mounts please use --yaml")
                        else:
                            # check that the only volume is of type secret
                            volume_name = c["volumeMounts"][0]["volumeName"]
                            for v in self.new_containerapp["properties"]["template"]["volumes"]:
                                if v["name"].lower() == volume_name.lower():
                                    if v["storageType"] != "Secret":
                                        raise ValidationError(
                                            "Usage error: --secret-volume-mount can only be used to update volume mounts with volumes of type secret. To update other types of volumes please use --yaml")
                                    break
                            c["volumeMounts"][0]["mountPath"] = self.get_argument_secret_volume_mount()
        return updating_existing_container

    def should_update_existing_container(self, c):
        return c["name"].lower() == self.get_argument_container_name().lower()


# decorator for preview create
class ContainerAppPreviewCreateDecorator(ContainerAppCreateDecorator):
    # pylint: disable=useless-super-delegation
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_service_type(self):
        return self.get_param("service_type")

    def get_argument_service_bindings(self):
        return self.get_param("service_bindings")

    def get_argument_customized_keys(self):
        return self.get_param("customized_keys")

    def get_argument_service_connectors_def_list(self):
        return self.get_param("service_connectors_def_list")

    def get_argument_kind(self):
        return self.get_param("kind")

    def set_argument_service_connectors_def_list(self, service_connectors_def_list):
        self.set_param("service_connectors_def_list", service_connectors_def_list)

    def set_argument_registry_identity(self, registry_identity):
        self.set_param("registry_identity", registry_identity)

    def set_argument_registry_server(self, registry_server):
        self.set_param("registry_server", registry_server)

    def set_argument_no_wait(self, no_wait):
        self.set_param("no_wait", no_wait)

    def get_argument_target_label(self):
        return self.get_param("target_label")

    # not craete role assignment if it's env system msi
    def check_create_acrpull_role_assignment(self):
        identity = self.get_argument_registry_identity()
        if identity and not is_registry_msi_system(identity) and not is_registry_msi_system_environment(identity):
            logger.info("Creating an acrpull role assignment for the registry identity")
            create_acrpull_role_assignment(self.cmd, self.get_argument_registry_server(), identity, skip_error=True)

    # not set up msi for current containerapp if it's env msi
    def set_up_registry_identity(self):
        identity = self.get_argument_registry_identity()
        if identity:
            if is_registry_msi_system(identity):
                set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.containerapp_def, system_assigned=True)
            elif is_valid_resource_id(identity):
                parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
                managed_env_name = parsed_managed_env['name']
                managed_env_rg = parsed_managed_env['resource_group']
                if not env_has_managed_identity(self.cmd, managed_env_rg, managed_env_name, identity):
                    set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.containerapp_def, user_assigned=[identity])

    def set_up_managed_identity(self):
        if self.get_argument_user_assigned() or self.get_argument_system_assigned():
            identity_def = deepcopy(ManagedServiceIdentityModel)
            identity_def["type"] = "None"

            assign_system_identity = self.get_argument_system_assigned()
            if self.get_argument_user_assigned():
                assign_user_identities = [x.lower() for x in self.get_argument_user_assigned()]
            else:
                assign_user_identities = []

            if assign_system_identity and assign_user_identities:
                identity_def["type"] = "SystemAssigned, UserAssigned"
            elif assign_system_identity:
                identity_def["type"] = "SystemAssigned"
            elif assign_user_identities:
                identity_def["type"] = "UserAssigned"

            if assign_user_identities:
                identity_def["userAssignedIdentities"] = {}
                subscription_id = get_subscription_id(self.cmd.cli_ctx)

                for r in assign_user_identities:
                    r = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), r)
                    identity_def["userAssignedIdentities"][r] = {}  # pylint: disable=unsupported-assignment-operation

            self.containerapp_def["identity"] = identity_def

    # If --registry-server is ACR, use system-assigned managed identity for image pull by default
    def set_up_system_assigned_identity_as_default_if_using_acr(self):
        registry_server = self.get_argument_registry_server()
        if registry_server is not None:
            if ACR_IMAGE_SUFFIX not in registry_server:
                return

            if self.get_argument_registry_identity() is None and self.get_argument_registry_user() is None and self.get_argument_registry_pass() is None:
                # Connected ContainerApp Not Support Identity
                parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
                if "resource_type" in parsed_managed_env:
                    if parsed_managed_env["resource_type"].lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
                        return
                self.set_argument_registry_identity('system')

    def parent_construct_payload(self):
        # preview logic
        self.check_create_acrpull_role_assignment()
        # end preview logic

        if self.get_argument_yaml():
            return self.set_up_create_containerapp_yaml(name=self.get_argument_name(), file_name=self.get_argument_yaml())

        if not self.get_argument_image():
            self.set_argument_image(HELLO_WORLD_IMAGE)

        if self.get_argument_managed_env() is None:
            raise RequiredArgumentMissingError('Usage error: --environment is required if not using --yaml')

        # Validate managed environment
        parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
        managed_env_name = parsed_managed_env['name']
        managed_env_rg = parsed_managed_env['resource_group']
        managed_env_info = None

        try:
            managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not managed_env_info:
            raise ValidationError("The environment '{}' does not exist. Specify a valid environment".format(self.get_argument_managed_env()))

        while not self.get_argument_no_wait() and safe_get(managed_env_info, "properties", "provisioningState", default="").lower() in ["inprogress", "updating"]:
            logger.info("Waiting for environment provisioning to finish before creating container app")
            time.sleep(5)
            managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)

        location = managed_env_info["location"]
        _ensure_location_allowed(self.cmd, location, CONTAINER_APPS_RP, "containerApps")

        if not self.get_argument_workload_profile_name() and "workloadProfiles" in managed_env_info:
            workload_profile_name = get_default_workload_profile_name_from_env(self.cmd, managed_env_info, managed_env_rg)
            self.set_argument_workload_profile_name(workload_profile_name)

        external_ingress = None
        if self.get_argument_ingress() is not None:
            if self.get_argument_ingress().lower() == "internal":
                external_ingress = False
            elif self.get_argument_ingress().lower() == "external":
                external_ingress = True

        ingress_def = None
        if self.get_argument_target_port() is not None and self.get_argument_ingress() is not None:
            ingress_def = deepcopy(IngressModel)
            ingress_def["external"] = external_ingress
            ingress_def["targetPort"] = self.get_argument_target_port()
            ingress_def["transport"] = self.get_argument_transport()
            ingress_def["exposedPort"] = self.get_argument_exposed_port() if self.get_argument_transport() == "tcp" else None
            ingress_def["allowInsecure"] = self.get_argument_allow_insecure()

        secrets_def = None
        if self.get_argument_secrets() is not None:
            secrets_def = parse_secret_flags(self.get_argument_secrets())

        registries_def = None
        if self.get_argument_registry_server() is not None and not is_registry_msi_system(self.get_argument_registry_identity()):
            registries_def = deepcopy(RegistryCredentialsModel)
            registries_def["server"] = self.get_argument_registry_server()

            # Infer credentials if not supplied and its azurecr
            if (self.get_argument_registry_user() is None or self.get_argument_registry_pass() is None) and self.get_argument_registry_identity() is None:
                registry_user, registry_pass = _infer_acr_credentials(self.cmd, self.get_argument_registry_server(), self.get_argument_disable_warnings())
                self.set_argument_registry_user(registry_user)
                self.set_argument_registry_pass(registry_pass)

            if not self.get_argument_registry_identity():
                registries_def["username"] = self.get_argument_registry_user()

                if secrets_def is None:
                    secrets_def = []
                registries_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def, self.get_argument_registry_user(),
                                                                                            self.get_argument_registry_server(),
                                                                                            self.get_argument_registry_pass(),
                                                                                            disable_warnings=self.get_argument_disable_warnings())
            else:
                registries_def["identity"] = self.get_argument_registry_identity()

        dapr_def = None
        if self.get_argument_dapr_enabled():
            dapr_def = deepcopy(DaprModel)
            dapr_def["enabled"] = True
            dapr_def["appId"] = self.get_argument_dapr_app_id()
            dapr_def["appPort"] = self.get_argument_dapr_app_port()
            dapr_def["appProtocol"] = self.get_argument_dapr_app_protocol()
            dapr_def["httpReadBufferSize"] = self.get_argument_dapr_http_read_buffer_size()
            dapr_def["httpMaxRequestSize"] = self.get_argument_dapr_http_max_request_size()
            dapr_def["logLevel"] = self.get_argument_dapr_log_level()
            dapr_def["enableApiLogging"] = self.get_argument_dapr_enable_api_logging()

        config_def = deepcopy(ConfigurationModel)
        config_def["secrets"] = secrets_def
        config_def["activeRevisionsMode"] = self.get_argument_revisions_mode()
        config_def["targetLabel"] = self.get_argument_target_label()
        config_def["ingress"] = ingress_def
        config_def["registries"] = [registries_def] if registries_def is not None else None
        config_def["dapr"] = dapr_def

        # Identity actions
        self.set_up_managed_identity()

        scale_def = self.set_up_scale_rule()

        resources_def = None
        if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
            resources_def = deepcopy(ContainerResourcesModel)
            resources_def["cpu"] = self.get_argument_cpu()
            resources_def["memory"] = self.get_argument_memory()

        container_def = deepcopy(ContainerModel)
        container_def["name"] = self.get_argument_container_name() if self.get_argument_container_name() else self.get_argument_name()
        container_def["image"] = self.get_argument_image() if not is_registry_msi_system(self.get_argument_registry_identity()) else HELLO_WORLD_IMAGE
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
        if resources_def is not None:
            container_def["resources"] = resources_def

        template_def = deepcopy(TemplateModel)

        template_def["containers"] = [container_def]
        template_def["scale"] = scale_def

        if self.get_argument_secret_volume_mount() is not None:
            volume_def = deepcopy(VolumeModel)
            volume_mount_def = deepcopy(VolumeMountModel)
            # generate a volume name
            volume_def["name"] = _generate_secret_volume_name()
            volume_def["storageType"] = "Secret"

            # mount the volume to the container
            volume_mount_def["volumeName"] = volume_def["name"]
            volume_mount_def["mountPath"] = self.get_argument_secret_volume_mount()
            container_def["volumeMounts"] = [volume_mount_def]
            template_def["volumes"] = [volume_def]

        if self.get_argument_revision_suffix() is not None and not is_registry_msi_system(self.get_argument_registry_identity()):
            template_def["revisionSuffix"] = self.get_argument_revision_suffix()

        if self.get_argument_termination_grace_period() is not None:
            template_def["terminationGracePeriodSeconds"] = self.get_argument_termination_grace_period()

        self.containerapp_def["location"] = location
        self.containerapp_def["properties"]["environmentId"] = self.get_argument_managed_env()
        self.containerapp_def["properties"]["configuration"] = config_def
        self.containerapp_def["properties"]["template"] = template_def
        self.containerapp_def["tags"] = self.get_argument_tags()

        if self.get_argument_workload_profile_name():
            self.containerapp_def["properties"]["workloadProfileName"] = self.get_argument_workload_profile_name()
            ensure_workload_profile_supported(self.cmd, managed_env_name, managed_env_rg, self.get_argument_workload_profile_name(),
                                              managed_env_info)

        # preview logic
        self.set_up_registry_identity()

    def construct_payload(self):
        self.set_up_system_assigned_identity_as_default_if_using_acr()
        self.parent_construct_payload()
        self.set_up_service_type()
        self.set_up_service_binds()
        self.set_up_extended_location()
        self.set_up_source()
        self.set_up_repo()
        if self.get_argument_max_inactive_revisions() is not None:
            safe_set(self.containerapp_def, "properties", "configuration", "maxInactiveRevisions", value=self.get_argument_max_inactive_revisions())
        if self.get_argument_kind() is not None:
            safe_set(self.containerapp_def, "kind", value=self.get_argument_kind())
        self.set_up_runtime()

    # copy from parent
    def parent_validate_arguments(self):
        validate_container_app_name(self.get_argument_name(), AppType.ContainerApp.name)
        validate_revision_suffix(self.get_argument_revision_suffix())
        # preview logic
        self.validate_create()
        # end preview logic

    def validate_create(self):
        validate_create(self.get_argument_registry_identity(), self.get_argument_registry_pass(), self.get_argument_registry_user(), self.get_argument_registry_server(),
                        self.get_argument_no_wait(), self.get_argument_revisions_mode(), self.get_argument_target_label(), self.get_argument_source(), self.get_argument_artifact(),
                        self.get_argument_repo(), self.get_argument_yaml(), self.get_argument_environment_type())

    def validate_arguments(self):
        self.parent_validate_arguments()
        if self.get_argument_service_bindings() and len(self.get_argument_service_bindings()) > 1 and self.get_argument_customized_keys():
            raise InvalidArgumentValueError("--bind have multiple values, but --customized-keys only can be set when --bind is single.")
        validate_runtime(self.get_argument_runtime(), self.get_argument_enable_java_metrics(), self.get_argument_enable_java_agent())
        if self.get_argument_scale_rule_type() and self.get_argument_scale_rule_identity():
            scale_rule_type = self.get_argument_scale_rule_type().lower()
            if scale_rule_type == "http" or scale_rule_type == "tcp":
                raise InvalidArgumentValueError("--scale-rule-identity cannot be set when --scale-rule-type is 'http' or 'tcp'")

        if self.get_argument_registry_server() is not None and \
                ACR_IMAGE_SUFFIX in self.get_argument_registry_server() and \
                self.get_argument_registry_user() is None and \
                self.get_argument_registry_pass() is None and \
                self.get_argument_no_wait():
            logger.warning(
                "--registry-server use system assigned managed identity for image pull by default. --no-wait will not take effect when using system-assigned registry identity.\n"
                "You can either remove --no-wait, use --registry-username, or use a user-assigned registry identity.")
            self.set_argument_no_wait(False)

    def set_up_source(self):
        from ._up_utils import (_validate_source_artifact_args)

        source = self.get_argument_source()
        artifact = self.get_argument_artifact()
        _validate_source_artifact_args(source, artifact)
        if artifact:
            # Artifact is mostly a convenience argument provided to use --source specifically with a single artifact file.
            # At this point we know for sure that source isn't set (else _validate_up_args would have failed), so we can build with this value.
            source = artifact
            self.set_argument_source(source)

        if source:
            app, _ = self._construct_app_and_env_for_source_or_repo()
            build_env_vars = self.get_argument_build_env_vars()
            dockerfile = "Dockerfile"
            # Uses local buildpacks, the Cloud Build or an ACR Task to generate image if Dockerfile was not provided by the user
            app.run_source_to_cloud_flow(source, dockerfile, build_env_vars, can_create_acr_if_needed=False, registry_server=self.get_argument_registry_server())
            # Validate containers exist
            containers = safe_get(self.containerapp_def, "properties", "template", "containers", default=[])
            if containers is None or len(containers) == 0:
                raise ValidationError(
                    "The container app '{}' does not have any containers. Please use --image to set the image for the container app".format(
                        self.get_argument_name()))
            # Update image
            # If is system registry identity, we will create containerapp with SystemAssigned first, then update the image
            containers[0]["image"] = HELLO_WORLD_IMAGE if (app.image is None or is_registry_msi_system(self.get_argument_registry_identity())) else app.image
            self.set_argument_image(app.image)

    def set_up_repo(self):
        if self.get_argument_repo():
            # Check if container app exists and if it does, set the image to the image of the existing container app
            existing_container_app = self._get_containerapp_if_exists()
            if existing_container_app:
                # Executing the create command with --repo makes two ARM calls. The container app is created first
                # and the source control is set only after the container app is created. This means, when the container app is
                # first created, the image would be defaulted to mcr.microsoft.com/k8se/quickstart:latest (if --image was not provided)
                # and the image name would change to `registry-server/containerapp-name:{github-sha}` only
                # after the source control completes successfully
                # and the new image is deployed.
                # If the create command is executed multiple times however, we need to make sure that the image is not defaulted
                # to mcr.microsoft.com/k8se/quickstart:latest if source control fails the subsequent times by setting the image
                # to the previously deployed image.
                containers_from_existing_container_app = safe_get(existing_container_app, "properties", "template", "containers", default=[])
                if containers_from_existing_container_app is None or len(containers_from_existing_container_app) == 0:
                    raise ValidationError(
                        "The container app '{}' does not have any containers. Please use --image to set the image for the container app".format(
                            self.get_argument_name()))
                if containers_from_existing_container_app[0]["image"] is None:
                    raise ValidationError(
                        "The container app '{}' does not have an image. Please use --image to set the image for the container app while creating the container app.".format(
                            self.get_argument_name()))
                containers = safe_get(self.containerapp_def, "properties", "template", "containers", default=[])
                if containers is None or len(containers) == 0:
                    raise ValidationError(
                        "The container app '{}' does not have any containers. Please use --image to set the image for the container app".format(
                            self.get_argument_name()))
                containers[0]["image"] = containers_from_existing_container_app[0]["image"]

    def _get_containerapp_if_exists(self):
        try:
            return self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)
            return None

    def _post_process_for_repo(self):
        from ._up_utils import (get_token, _create_github_action)
        app, env = self._construct_app_and_env_for_source_or_repo()
        # Get GitHub access token
        token = get_token(self.cmd, self.get_argument_repo(), self.get_argument_token())
        _create_github_action(app, env, self.get_argument_service_principal_client_id(), self.get_argument_service_principal_client_secret(),
                              self.get_argument_service_principal_tenant_id(), self.get_argument_branch(), token, self.get_argument_repo(), self.get_argument_context_path(), self.get_argument_build_env_vars())
        cache_github_token(self.cmd, token, self.get_argument_repo())
        return self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())

    def _construct_app_and_env_for_source_or_repo(self):
        from ._up_utils import (ContainerApp, ResourceGroup, ContainerAppEnvironment, _reformat_image, get_token, _has_dockerfile, _get_dockerfile_content, _get_ingress_and_target_port, _get_registry_details, _get_registry_details_without_get_creds)
        ingress = self.get_argument_ingress()
        target_port = self.get_argument_target_port()
        dockerfile = "Dockerfile"
        token = get_token(self.cmd, self.get_argument_repo(), self.get_argument_token())

        # Parse resource group name and managed env name
        env_id = safe_get(self.containerapp_def, "properties", "environmentId")
        parsed_env = parse_resource_id(env_id)
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            raise ValidationError(
                "Usage error: --source or --repo cannot be used with a connected environment. Please provide a managed environment instead.")
        env_name = parsed_env['name']
        env_rg = parsed_env['resource_group']

        # Parse location
        env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
        location = self.containerapp_def["location"] if "location" in self.containerapp_def else env_info['location']

        # Set image to None if it was previously set to the default image (case where image was not provided by the user) else reformat it
        image = None if self.get_argument_image().__eq__(HELLO_WORLD_IMAGE) else _reformat_image(self.get_argument_source(), self.get_argument_repo(), self.get_argument_image())

        has_dockerfile = _has_dockerfile(self.get_argument_source(), dockerfile)
        if has_dockerfile:
            dockerfile_content = _get_dockerfile_content(self.get_argument_repo(), self.get_argument_branch(), token, self.get_argument_source(), self.get_argument_context_path(), dockerfile)
            ingress, target_port = _get_ingress_and_target_port(self.get_argument_ingress(), self.get_argument_target_port(), dockerfile_content)

        # Construct ContainerApp
        resource_group = ResourceGroup(self.cmd, self.get_argument_resource_group_name(), location=location)
        env_resource_group = ResourceGroup(self.cmd, env_rg, location=location)
        env = ContainerAppEnvironment(self.cmd, env_name, env_resource_group, location=location)
        app = ContainerApp(self.cmd, self.get_argument_name(), resource_group, None, image, env, target_port, self.get_argument_registry_server(), self.get_argument_registry_user(), self.get_argument_registry_pass(), self.get_argument_env_vars(), self.get_argument_workload_profile_name(), ingress)

        if self.get_argument_source():
            _get_registry_details_without_get_creds(self.cmd, app, self.get_argument_source())
        if self.get_argument_repo():
            _get_registry_details(self.cmd, app, self.get_argument_source())  # fetch ACR creds from arguments registry arguments, --repo will create Github Actions, which requires ACR registry's creds

        # When the ACR not exists, it will not create acr, it will use local buildpacks or the Cloud Build
        # So we should only backfill registry_server, registry_identity when the ACR existing
        if app.should_create_acr is False:
            self.set_argument_registry_server(app.registry_server)
            self.set_up_system_assigned_identity_as_default_if_using_acr()
            self.set_up_registry_identity()
        return app, env

    def post_process(self, r):
        if is_registry_msi_system(self.get_argument_registry_identity()):
            r = self.create()

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not self.get_argument_no_wait():
            not self.get_argument_disable_warnings() and logger.warning('Containerapp creation in progress. Please monitor the creation using `az containerapp show -n {} -g {}`'.format(self.get_argument_name(), self.get_argument_resource_group_name()))

        if "configuration" in r["properties"] and "ingress" in r["properties"]["configuration"] and \
                r["properties"]["configuration"]["ingress"] and "fqdn" in r["properties"]["configuration"]["ingress"]:
            not self.get_argument_disable_warnings() and logger.warning("\nContainer app created. Access your app at https://{}/\n".format(r["properties"]["configuration"]["ingress"]["fqdn"]))
        else:
            target_port = self.get_argument_target_port() or "<port>"
            not self.get_argument_disable_warnings() and logger.warning(
                "\nContainer app created. To access it over HTTPS, enable ingress: "
                "az containerapp ingress enable -n %s -g %s --type external --target-port %s"
                " --transport auto\n", self.get_argument_name(), self.get_argument_resource_group_name(), target_port)

        if self.get_argument_service_connectors_def_list() is not None:
            linker_client = get_linker_client(self.cmd)

            for item in self.get_argument_service_connectors_def_list():
                while r is not None and r["properties"]["provisioningState"].lower() == "inprogress":
                    r = self.client.show(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                    time.sleep(1)
                linker_client.linker.begin_create_or_update(resource_uri=r["id"],
                                                            parameters=item["parameters"],
                                                            linker_name=item["linker_name"]).result()
        if self.get_argument_repo():
            r = self._post_process_for_repo()

        return r

    def set_up_extended_location(self):
        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            if not self.containerapp_def.get('extendedLocation'):
                env_id = safe_get(self.containerapp_def, "properties", 'environmentId') or self.get_argument_managed_env()
                parsed_env = parse_resource_id(env_id)
                env_name = parsed_env['name']
                env_rg = parsed_env['resource_group']
                env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
                self.containerapp_def["extendedLocation"] = env_info["extendedLocation"]

    def set_up_service_type(self):
        service_def = None
        if self.get_argument_service_type():
            service_def = ServiceModel
            service_def["type"] = self.get_argument_service_type()
        safe_set(self.containerapp_def, "properties", "configuration", "service", value=service_def)

    def set_up_service_binds(self):
        if self.get_argument_service_bindings() is not None:
            service_connectors_def_list, service_bindings_def_list = parse_service_bindings(self.cmd,
                                                                                            self.get_argument_service_bindings(),
                                                                                            self.get_argument_resource_group_name(),
                                                                                            self.get_argument_name(),
                                                                                            safe_get(self.containerapp_def, "properties", "environmentId"),
                                                                                            self.get_argument_customized_keys())
            self.set_argument_service_connectors_def_list(service_connectors_def_list)
            unique_bindings = check_unique_bindings(self.cmd, service_connectors_def_list, service_bindings_def_list,
                                                    self.get_argument_resource_group_name(), self.get_argument_name())
            if not unique_bindings:
                raise ValidationError("Binding names across managed and dev services should be unique.")
            safe_set(self.containerapp_def, "properties", "template", "serviceBinds", value=service_bindings_def_list)

    def set_up_create_containerapp_yaml(self, name, file_name):
        # This list can not include anything that has a default value: transport, revisions_mode, environment_type
        if self.get_argument_image() or self.get_argument_min_replicas() or self.get_argument_max_replicas() or self.get_argument_target_port() or self.get_argument_ingress() or \
                self.get_argument_secrets() or self.get_argument_env_vars() or self.get_argument_cpu() or self.get_argument_memory() or self.get_argument_registry_server() or \
                self.get_argument_registry_user() or self.get_argument_registry_pass() or self.get_argument_dapr_enabled() or self.get_argument_dapr_app_port() or self.get_argument_dapr_app_id() or \
                self.get_argument_startup_command() or self.get_argument_args() or self.get_argument_tags() or self.get_argument_target_label():
            not self.get_argument_disable_warnings() and logger.warning(
                'Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')

        yaml_containerapp = process_loaded_yaml(load_yaml_file(file_name))

        if not yaml_containerapp.get('name'):
            yaml_containerapp['name'] = name
        elif yaml_containerapp.get('name').lower() != name.lower():
            logger.warning(
                'The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
                    yaml_containerapp.get('name'), name))
        name = yaml_containerapp.get('name')

        if not yaml_containerapp.get('type'):
            yaml_containerapp['type'] = 'Microsoft.App/containerApps'
        elif yaml_containerapp.get('type').lower() != "microsoft.app/containerapps":
            raise ValidationError('Containerapp type must be \"Microsoft.App/ContainerApps\"')

        # Deserialize the yaml into a ContainerApp object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)

            self.containerapp_def = deserializer('ContainerApp', yaml_containerapp)
        except DeserializationError as ex:
            raise ValidationError(
                'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.') from ex

        # Remove tags before converting from snake case to camel case, then re-add tags. We don't want to change the case of the tags. Need this since we're not using SDK
        tags = None
        if yaml_containerapp.get('tags'):
            tags = yaml_containerapp.get('tags')
            del yaml_containerapp['tags']

        # Save customizedKeys before converting from snake case to camel case, then re-add customizedKeys. We don't want to change the case of the customizedKeys.
        service_binds = safe_get(yaml_containerapp, "properties", "template", "serviceBinds", default=[])
        customized_keys_dict = {}
        for bind in service_binds:
            if bind.get("name") and bind.get("customizedKeys"):
                customized_keys_dict[bind["name"]] = bind["customizedKeys"]

        self.containerapp_def = _convert_object_from_snake_to_camel_case(_object_to_dict(self.containerapp_def))
        self.containerapp_def['tags'] = tags

        # Containerapp object is deserialized from 'ContainerApp' model, "Properties" level is lost after deserialization
        # We try to get serviceBinds from 'properties.template.serviceBinds' first, if not exists, try 'template.serviceBinds'
        service_binds = safe_get(self.containerapp_def, "properties", "template", "serviceBinds") or safe_get(self.containerapp_def, "template", "serviceBinds")
        if service_binds:
            for bind in service_binds:
                if bind.get("name") and bind.get("customizedKeys"):
                    bind["customizedKeys"] = customized_keys_dict.get(bind["name"])

        # After deserializing, some properties may need to be moved under the "properties" attribute. Need this since we're not using SDK
        self.containerapp_def = process_loaded_yaml(self.containerapp_def)

        # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
        _remove_additional_attributes(self.containerapp_def)
        _remove_readonly_attributes(self.containerapp_def)

        # Remove extra workloadProfileName introduced in deserialization
        if "workloadProfileName" in self.containerapp_def:
            del self.containerapp_def["workloadProfileName"]

        # Validate managed environment
        env_id = self.containerapp_def["properties"]['environmentId']
        env_info = None
        if self.get_argument_managed_env():
            if not self.get_argument_disable_warnings() and env_id is not None and env_id != self.get_argument_managed_env():
                logger.warning('The environmentId was passed along with --yaml. The value entered with --environment will be ignored, and the configuration defined in the yaml will be used instead')
            if env_id is None:
                env_id = self.get_argument_managed_env()
                safe_set(self.containerapp_def, "properties", "environmentId", value=env_id)

        if not self.containerapp_def["properties"].get('environmentId'):
            raise RequiredArgumentMissingError(
                'environmentId is required. This can be retrieved using the `az containerapp env show -g MyResourceGroup -n MyContainerappEnvironment --query id` command. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')

        if is_valid_resource_id(env_id):
            parsed_managed_env = parse_resource_id(env_id)
            env_name = parsed_managed_env['name']
            env_rg = parsed_managed_env['resource_group']
        else:
            raise ValidationError('Invalid environmentId specified. Environment not found')

        try:
            env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not env_info:
            raise ValidationError("The environment '{}' in resource group '{}' was not found".format(env_name, env_rg))

        # Validate location
        if not self.containerapp_def.get('location'):
            self.containerapp_def['location'] = env_info['location']

    def get_environment_client(self):
        if self.get_argument_yaml():
            env = safe_get(self.containerapp_def, "properties", "environmentId")
        else:
            env = self.get_argument_managed_env()

        environment_type = self.get_argument_environment_type()
        if not env and not environment_type:
            return ManagedEnvironmentClient

        parsed_env = parse_resource_id(env)

        # Validate environment type
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            if environment_type == MANAGED_ENVIRONMENT_TYPE:
                logger.warning("User passed a connectedEnvironment resource id but did not specify --environment-type connected. Using environment type connected.")
            environment_type = CONNECTED_ENVIRONMENT_TYPE
        else:
            if environment_type == CONNECTED_ENVIRONMENT_TYPE:
                logger.warning("User passed a managedEnvironment resource id but specified --environment-type connected. Using environment type managed.")
            environment_type = MANAGED_ENVIRONMENT_TYPE

        self.set_argument_environment_type(environment_type)
        self.set_argument_managed_env(env)

        if environment_type == CONNECTED_ENVIRONMENT_TYPE:
            return ConnectedEnvironmentClient
        else:
            return ManagedEnvironmentPreviewClient

    def set_up_runtime(self):
        if self.should_set_up_runtime():
            runtime_option = infer_runtime_option(self.get_argument_runtime(), self.get_argument_enable_java_metrics(), self.get_argument_enable_java_agent())
            runtime_def = None  # default value for runtime_option == RUNTIME_GENERIC, set None to erase runtime info
            if runtime_option == RUNTIME_JAVA:
                if self.get_argument_enable_java_metrics() is None and self.get_argument_enable_java_agent() is None:
                    runtime_def = {
                        "java": {
                            "enableMetrics": True
                        }
                    }
                else:
                    runtime_java_def = RuntimeJavaModel
                    if self.get_argument_enable_java_metrics() is not None:
                        runtime_java_def["enableMetrics"] = self.get_argument_enable_java_metrics()
                    if self.get_argument_enable_java_agent() is not None:
                        runtime_java_def["javaAgent"]["enabled"] = self.get_argument_enable_java_agent()
                    runtime_def = {
                        "java": runtime_java_def
                    }
            safe_set(self.containerapp_def, "properties", "configuration", "runtime", value=runtime_def)

    # pylint: disable=unsupported-assignment-operation
    def set_up_scale_rule(self):
        scale_def = super().set_up_scale_rule()
        if scale_def and scale_def["rules"] and scale_def["rules"][0] and scale_def["rules"][0]["custom"] and self.get_argument_scale_rule_identity():
            identity = self.get_argument_scale_rule_identity().lower()
            if identity != "system":
                subscription_id = get_subscription_id(self.cmd.cli_ctx)
                identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
            scale_def["rules"][0]["custom"]["identity"] = identity
        return scale_def

    def should_set_up_runtime(self):
        if self.get_argument_runtime() is not None:
            return True
        if self.get_argument_enable_java_metrics() is not None:
            return True
        if self.get_argument_enable_java_agent() is not None:
            return True
        return False

    def get_argument_environment_type(self):
        return self.get_param("environment_type")

    def set_argument_environment_type(self, environment_type):
        self.set_param("environment_type", environment_type)

    def get_argument_source(self):
        return self.get_param("source")

    def set_argument_source(self, source):
        self.set_param("source", source)

    def get_argument_artifact(self):
        return self.get_param("artifact")

    def get_argument_build_env_vars(self):
        return self.get_param("build_env_vars")

    def get_argument_repo(self):
        return self.get_param("repo")

    def get_argument_branch(self):
        return self.get_param("branch")

    def get_argument_token(self):
        return self.get_param("token")

    def get_argument_context_path(self):
        return self.get_param("context_path")

    def get_argument_service_principal_client_id(self):
        return self.get_param("service_principal_client_id")

    def get_argument_service_principal_client_secret(self):
        return self.get_param("service_principal_client_secret")

    def get_argument_service_principal_tenant_id(self):
        return self.get_param("service_principal_tenant_id")

    def get_argument_max_inactive_revisions(self):
        return self.get_param("max_inactive_revisions")

    def get_argument_runtime(self):
        return self.get_param("runtime")

    def get_argument_enable_java_metrics(self):
        return self.get_param("enable_java_metrics")

    def get_argument_enable_java_agent(self):
        return self.get_param("enable_java_agent")

    def get_argument_scale_rule_identity(self):
        return self.get_param("scale_rule_identity")


# decorator for preview update
class ContainerAppPreviewUpdateDecorator(ContainerAppUpdateDecorator):
    def get_argument_service_bindings(self):
        return self.get_param("service_bindings")

    def get_argument_customized_keys(self):
        return self.get_param("customized_keys")

    def get_argument_service_connectors_def_list(self):
        return self.get_param("service_connectors_def_list")

    def set_argument_service_connectors_def_list(self, service_connectors_def_list):
        self.set_param("service_connectors_def_list", service_connectors_def_list)

    def get_argument_unbind_service_bindings(self):
        return self.get_param("unbind_service_bindings")

    def get_argument_source(self):
        return self.get_param("source")

    def set_argument_source(self, source):
        self.set_param("source", source)

    def get_argument_artifact(self):
        return self.get_param("artifact")

    def get_argument_build_env_vars(self):
        return self.get_param("build_env_vars")

    def get_argument_runtime(self):
        return self.get_param("runtime")

    def get_argument_enable_java_metrics(self):
        return self.get_param("enable_java_metrics")

    def get_argument_enable_java_agent(self):
        return self.get_param("enable_java_agent")

    # This argument is set when cloud build is used to build the image and this argument ensures that only one container with the new cloud build image is
    def get_argument_force_single_container_updates(self):
        return self.get_param("force_single_container_updates")

    def get_argument_scale_rule_identity(self):
        return self.get_param("scale_rule_identity")

    def set_argument_registry_identity(self, registry_identity):
        self.set_param("registry_identity", registry_identity)

    def validate_arguments(self):
        super().validate_arguments()
        if self.get_argument_service_bindings() and len(self.get_argument_service_bindings()) > 1 and self.get_argument_customized_keys():
            raise InvalidArgumentValueError(
                "--bind have multiple values, but --customized-keys only can be set when --bind is single.")
        validate_runtime(self.get_argument_runtime(), self.get_argument_enable_java_metrics(), self.get_argument_enable_java_agent())
        if self.get_argument_scale_rule_type() and self.get_argument_scale_rule_identity():
            scale_rule_type = self.get_argument_scale_rule_type().lower()
            if scale_rule_type == "http" or scale_rule_type == "tcp":
                raise InvalidArgumentValueError("--scale-rule-identity cannot be set when --scale-rule-type is 'http' or 'tcp'")

    def check_assign_system_identity(self):
        identity = self.get_argument_registry_identity()
        system_sp = safe_get(self.containerapp_def, "identity", "principalId")

        # create system service principalId
        if system_sp is None and is_registry_msi_system(identity):
            logger.warning("Assign system identity to containerapp.")
            patch_identity_def = {}
            safe_set(patch_identity_def, "identity", value=safe_get(self.new_containerapp, "identity"))
            try:
                self.client.update(
                    cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                    name=self.get_argument_name(), container_app_envelope=patch_identity_def,
                    no_wait=False)
            except Exception as e:
                handle_raw_exception(e)
            self.containerapp_def = self.show()

    def check_acrpull_role_assignment(self):
        identity = self.get_argument_registry_identity()
        system_sp = safe_get(self.containerapp_def, "identity", "principalId")

        # not create role assignment if it's env system msi or system msi
        if identity and not is_registry_msi_system(identity) and not is_registry_msi_system_environment(identity):
            create_acrpull_role_assignment_if_needed(self.cmd, self.get_argument_registry_server(), identity, skip_error=True)
        # create acrpull role assignment if the containerapp already has principalId
        if identity and is_registry_msi_system(identity):
            create_acrpull_role_assignment_if_needed(self.cmd, self.get_argument_registry_server(), registry_identity=None, service_principal=system_sp)

    # not set up msi for current containerapp if it's env msi
    def set_up_managed_identity(self):
        identity = self.get_argument_registry_identity()
        user_assigned_identity = self.get_argument_user_assigned()
        system_assigned_identity = self.get_argument_system_assigned()

        if identity:
            safe_set(self.new_containerapp, "identity", value=deepcopy(self.containerapp_def["identity"]))
            if safe_get(self.new_containerapp, "identity", "principalId"):
                self.new_containerapp["identity"].pop("principalId")
            if safe_get(self.new_containerapp, "identity", "tenantId"):
                self.new_containerapp["identity"].pop("tenantId")

            if is_registry_msi_system(identity):
                set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerapp,
                                     system_assigned=True)
            elif is_valid_resource_id(identity):
                parsed_managed_env = parse_resource_id(safe_get(self.containerapp_def, "properties", "environmentId"))
                managed_env_name = parsed_managed_env['name']
                managed_env_rg = parsed_managed_env['resource_group']
                if not env_has_managed_identity(self.cmd, managed_env_rg, managed_env_name, identity):
                    set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerapp,
                                         user_assigned=[identity])

        if user_assigned_identity:
            set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerapp,
                                 user_assigned=user_assigned_identity)

        if system_assigned_identity is not None:
            set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerapp,
                                 system_assigned=system_assigned_identity)

    # If --registry-server is ACR, use system-assigned managed identity for image pull by default
    # Don't update registries unless the registry for the updated image is missing
    # If the existing registry identity is 'system', keep it consistent
    def set_up_system_assigned_identity_as_default_if_using_acr(self):
        registry_server = self.get_argument_registry_server()
        if registry_server is not None:
            if ACR_IMAGE_SUFFIX not in registry_server:
                return

            if self.get_argument_registry_identity() is None and self.get_argument_registry_user() is None and self.get_argument_registry_pass() is None:
                registries_def = safe_get(self.containerapp_def, "properties", "configuration", "registries")
                if registries_def is None:
                    self.set_argument_registry_identity('system')
                    return
                registry_exists = False
                for r in registries_def:
                    if r['server'].lower() == self.get_argument_registry_server().lower():
                        registry_exists = True
                        registry_identity = safe_get(r, "identity")
                        if registry_identity:
                            self.set_argument_registry_identity(registry_identity)

                if not registry_exists:
                    self.set_argument_registry_identity('system')

    def construct_for_pre_process(self):
        self.set_up_system_assigned_identity_as_default_if_using_acr()
        self.set_up_managed_identity()

    def pre_process(self):
        self.check_assign_system_identity()
        self.check_acrpull_role_assignment()

    def construct_payload(self):
        super().construct_payload()
        self.set_up_service_bindings()
        self.set_up_unbind_service_bindings()
        self.set_up_source()
        if self.get_argument_max_inactive_revisions() is not None:
            safe_set(self.new_containerapp, "properties", "configuration", "maxInactiveRevisions", value=self.get_argument_max_inactive_revisions())
        self.set_up_runtime()

        if self.get_argument_scale_rule_name() and self.get_argument_scale_rule_identity():
            custom_scale_rule = safe_get(self.new_containerapp, "properties", "template", "scale", "rules", default=[])
            if custom_scale_rule and len(custom_scale_rule) > 0 and custom_scale_rule[0]["custom"]:
                identity = self.get_argument_scale_rule_identity().lower()
                if identity != "system":
                    subscription_id = get_subscription_id(self.cmd.cli_ctx)
                    identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
                self.new_containerapp["properties"]["template"]["scale"]["rules"][0]["custom"]["identity"] = identity

    def set_up_source(self):
        from ._up_utils import (_validate_source_artifact_args)

        source = self.get_argument_source()
        artifact = self.get_argument_artifact()
        build_env_vars = self.get_argument_build_env_vars()
        _validate_source_artifact_args(source, artifact)
        if artifact:
            # Artifact is mostly a convenience argument provided to use --source specifically with a single artifact file.
            # At this point we know for sure that source isn't set (else _validate_up_args would have failed), so we can build with this value.
            source = artifact
            self.set_argument_source(source)

        if source:
            if self.get_argument_yaml():
                raise MutuallyExclusiveArgumentError("Cannot use --source with --yaml together. Can either deploy from a local directory or provide a yaml file")
            # Check if an ACR registry is associated with the container app
            existing_registries = safe_get(self.containerapp_def, "properties", "configuration", "registries", default=[])
            existing_registries = [r for r in existing_registries if ACR_IMAGE_SUFFIX in r["server"]]
            if existing_registries and len(existing_registries) > 0:
                registry_server = existing_registries[0]["server"]
                self._update_container_app_source(cmd=self.cmd, source=source, build_env_vars=build_env_vars, registry_server=registry_server)
            else:
                self._update_container_app_source(cmd=self.cmd, source=source, build_env_vars=build_env_vars, registry_server=None)

    def _update_container_app_source(self, cmd, source, build_env_vars, registry_server):
        from ._up_utils import (ContainerApp, ResourceGroup, ContainerAppEnvironment, _reformat_image, _has_dockerfile, _get_dockerfile_content, _get_ingress_and_target_port, _get_registry_details_without_get_creds)

        ingress = self.get_argument_ingress()
        target_port = self.get_argument_target_port()
        dockerfile = "Dockerfile"

        # Parse resource group name and managed env name
        env_id = safe_get(self.containerapp_def, "properties", "environmentId")
        parsed_env = parse_resource_id(env_id)
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            raise ValidationError(
                "Usage error: --source cannot be used with a connected environment. Please provide a managed environment instead.")
        env_name = parsed_env['name']
        env_rg = parsed_env['resource_group']

        # Set image to None if it was previously set to the default image (case where image was not provided by the user) else reformat it
        image = None if self.get_argument_image() is None else _reformat_image(source=source, image=self.get_argument_image(), repo=None)

        # Parse location
        env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
        location = self.containerapp_def["location"] if "location" in self.containerapp_def else env_info['location']

        # Check if source contains a Dockerfile
        # and ignore checking if Dockerfile exists in repo since GitHub action inherently checks for it.
        if _has_dockerfile(source, dockerfile):
            dockerfile_content = _get_dockerfile_content(repo=None, branch=None, token=None, source=source, context_path=None, dockerfile=dockerfile)
            ingress, target_port = _get_ingress_and_target_port(self.get_argument_ingress(), self.get_argument_target_port(), dockerfile_content)

        # Construct ContainerApp
        resource_group = ResourceGroup(cmd, self.get_argument_resource_group_name(), location=location)
        env_resource_group = ResourceGroup(cmd, env_rg, location=location)
        env = ContainerAppEnvironment(cmd, env_name, env_resource_group, location=location)
        app = ContainerApp(cmd=cmd, name=self.get_argument_name(), resource_group=resource_group, image=image, env=env, target_port=target_port, workload_profile_name=self.get_argument_workload_profile_name(), ingress=ingress, registry_server=registry_server)

        # Fetch registry credentials
        _get_registry_details_without_get_creds(cmd, app, source)  # fetch ACR creds from arguments registry arguments
        # Uses local buildpacks, the Cloud Build or an ACR Task to generate image if Dockerfile was not provided by the user
        app.run_source_to_cloud_flow(source, dockerfile, build_env_vars, can_create_acr_if_needed=False, registry_server=app.registry_server)

        # Validate an image associated with the container app exists
        containers = safe_get(self.containerapp_def, "properties", "template", "containers", default=[])
        if containers is None or len(containers) == 0:
            raise ValidationError(
                "The container app '{}' does not have any containers. Please use --image to set the image for the container app".format(
                    self.get_argument_name()))
        self.new_containerapp["properties"]["template"] = {} if "template" not in self.new_containerapp["properties"] else self.new_containerapp["properties"]["template"]
        self.new_containerapp["properties"]["template"]["containers"] = containers
        # Update image in the container app
        self.new_containerapp["properties"]["template"]["containers"][0]["image"] = HELLO_WORLD_IMAGE if app.image is None else app.image
        self.new_containerapp["properties"]["template"]["containers"][0]["name"] = app.name

    def post_process(self, r):
        # Delete managed bindings
        if is_cloud_supported_by_service_connector(self.cmd.cli_ctx):
            linker_client = None
            if self.get_argument_unbind_service_bindings():
                linker_client = get_linker_client(self.cmd)
                for item in self.get_argument_unbind_service_bindings():
                    while r["properties"]["provisioningState"].lower() == "inprogress":
                        r = self.client.show(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                        time.sleep(1)
                    linker_client.linker.begin_delete(resource_uri=r["id"], linker_name=item).result()

            # Update managed bindings
            if self.get_argument_service_connectors_def_list() is not None:
                linker_client = get_linker_client(self.cmd) if linker_client is None else linker_client
                for item in self.get_argument_service_connectors_def_list():
                    while r["properties"]["provisioningState"].lower() == "inprogress":
                        r = self.client.show(self.cmd, self.get_argument_resource_group_name(), self.get_argument_name())
                        time.sleep(1)
                    linker_client.linker.begin_create_or_update(resource_uri=r["id"],
                                                                parameters=item["parameters"],
                                                                linker_name=item["linker_name"]).result()
        return r

    def set_up_service_bindings(self):
        if self.get_argument_service_bindings() is None:
            return

        linker_client = get_linker_client(self.cmd)

        service_connectors_def_list, service_bindings_def_list = parse_service_bindings(self.cmd,
                                                                                        self.get_argument_service_bindings(),
                                                                                        self.get_argument_resource_group_name(),
                                                                                        self.get_argument_name(),
                                                                                        safe_get(self.containerapp_def, "properties", "environmentId"),
                                                                                        self.get_argument_customized_keys())
        self.set_argument_service_connectors_def_list(service_connectors_def_list)
        service_bindings_used_map = {update_item["name"]: False for update_item in service_bindings_def_list}

        safe_set(self.new_containerapp, "properties", "template", "serviceBinds", value=self.containerapp_def["properties"]["template"]["serviceBinds"])

        if self.new_containerapp["properties"]["template"]["serviceBinds"] is None:
            self.new_containerapp["properties"]["template"]["serviceBinds"] = []

        for item in self.new_containerapp["properties"]["template"]["serviceBinds"]:
            for update_item in service_bindings_def_list:
                if update_item["name"] in item.values():
                    item["serviceId"] = update_item["serviceId"]
                    if update_item.get("clientType"):
                        item["clientType"] = update_item.get("clientType")
                    if update_item.get("customizedKeys"):
                        item["customizedKeys"] = update_item.get("customizedKeys")
                    service_bindings_used_map[update_item["name"]] = True

        for update_item in service_bindings_def_list:
            if service_bindings_used_map[update_item["name"]] is False:
                # Check if it doesn't exist in existing service linkers
                if is_cloud_supported_by_service_connector(self.cmd.cli_ctx):
                    managed_bindings = linker_client.linker.list(resource_uri=self.containerapp_def["id"])
                    if managed_bindings:
                        managed_bindings_list = [item.name for item in managed_bindings]
                        if update_item["name"] in managed_bindings_list:
                            raise ValidationError("Binding names across managed and dev services should be unique.")

                self.new_containerapp["properties"]["template"]["serviceBinds"].append(update_item)

        if service_connectors_def_list is not None:
            for item in service_connectors_def_list:
                # Check if it doesn't exist in existing service bindings
                service_bindings_list = []
                for binds in self.new_containerapp["properties"]["template"]["serviceBinds"]:
                    service_bindings_list.append(binds["name"])
                    if item["linker_name"] in service_bindings_list:
                        raise ValidationError("Binding names across managed and dev services should be unique.")

    def set_up_unbind_service_bindings(self):
        if self.get_argument_unbind_service_bindings():
            new_template = self.new_containerapp.setdefault("properties", {}).setdefault("template", {})
            existing_template = self.containerapp_def["properties"]["template"]

            if not self.get_argument_service_bindings():
                new_template["serviceBinds"] = existing_template.get("serviceBinds", [])

            service_bindings_dict = {}
            if new_template["serviceBinds"]:
                service_bindings_dict = {service_binding["name"]: index for index, service_binding in
                                         enumerate(new_template.get("serviceBinds", []))}

            for item in self.get_argument_unbind_service_bindings():
                if item in service_bindings_dict:
                    new_template["serviceBinds"] = [binding for binding in new_template["serviceBinds"] if
                                                    binding["name"] != item]

    def get_argument_max_inactive_revisions(self):
        return self.get_param("max_inactive_revisions")

    def _need_update_container(self):
        return self.get_argument_image() or self.get_argument_force_single_container_updates() or self.get_argument_container_name() or self.get_argument_set_env_vars() is not None or self.get_argument_remove_env_vars() is not None or self.get_argument_replace_env_vars() is not None or self.get_argument_remove_all_env_vars() or self.get_argument_cpu() or self.get_argument_memory() or self.get_argument_startup_command() is not None or self.get_argument_args() is not None or self.get_argument_secret_volume_mount() is not None

    def set_up_existing_container_update(self):
        if self.get_argument_force_single_container_updates():
            containers = safe_get(self.new_containerapp, "properties", "template", "containers", default=[])
            if len(containers) == 0:
                raise ValidationError(
                    "Cloud build image update failed. The container app '{}' does not have any containers.".format(self.get_argument_name()))
            # Remove n-1 containers where n is the number of containers in the containerapp and replace remaining container with the new container
            # Fails if all containers are removed
            while len(self.new_containerapp["properties"]["template"]["containers"]) > 1:
                self.new_containerapp["properties"]["template"]["containers"].pop()
            # Set the container name to the container app name if force_single_container_updates is set
            self.set_argument_container_name(self.get_argument_name())
            safe_set(self.new_containerapp, "properties", "template", "containers", 0, "name", value=self.get_argument_container_name())
        return super().set_up_existing_container_update()

    def should_update_existing_container(self, c):
        # Update existing container if container name matches the argument container name or if force_single_container_updates is set
        # force_single_container_updates argument is set when cloud build is used to build the image and this argument ensures that only one container with the new cloud build image is present in the containerapp
        return c["name"].lower() == self.get_argument_container_name().lower() or self.get_argument_force_single_container_updates()

    def set_up_runtime(self):
        if self.should_set_up_runtime():
            runtime_option = infer_runtime_option(self.get_argument_runtime(), self.get_argument_enable_java_metrics(), self.get_argument_enable_java_agent())
            runtime_def = None  # default value for runtime_option == RUNTIME_GENERIC, set None to erase runtime info
            if runtime_option == RUNTIME_JAVA:
                runtime_java_def = {}
                if self.get_argument_enable_java_metrics() is not None:
                    runtime_java_def["enableMetrics"] = self.get_argument_enable_java_metrics()
                else:
                    try:
                        runtime_java_def["enableMetrics"] = self.containerapp_def["properties"]["configuration"]["runtime"]["java"]["enableMetrics"]
                    except TypeError:
                        runtime_java_def["enableMetrics"] = True

                if self.get_argument_enable_java_agent() is not None:
                    safe_set(runtime_java_def, "javaAgent", "enabled", value=self.get_argument_enable_java_agent())
                    if self.get_argument_enable_java_agent() is False:
                        runtime_java_def["javaAgent"]["logging"] = {  # clear logger settings when disable java agent
                            "loggerSettings": []
                        }

                runtime_def = {
                    "java": runtime_java_def
                }
            safe_set(self.new_containerapp, "properties", "configuration", "runtime", value=runtime_def)

    def should_set_up_runtime(self):
        if self.get_argument_runtime() is not None or self.get_argument_enable_java_metrics() is not None or self.get_argument_enable_java_agent() is not None:
            return True
        return False


# decorator for preview list
class ContainerAppPreviewListDecorator(BaseContainerAppDecorator):
    # pylint: disable=useless-super-delegation
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)

    def list(self):
        containerapps = super().list()
        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            containerapps = [c for c in containerapps if CONNECTED_ENVIRONMENT_RESOURCE_TYPE in c["properties"]["environmentId"]]
        if self.get_argument_environment_type() == MANAGED_ENVIRONMENT_TYPE:
            containerapps = [c for c in containerapps if MANAGED_ENVIRONMENT_RESOURCE_TYPE in c["properties"]["environmentId"]]
        return containerapps

    def get_environment_client(self):
        env = self.get_argument_managed_env()

        if is_valid_resource_id(env):
            parsed_env = parse_resource_id(env)
            if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
                return ConnectedEnvironmentClient
            else:
                return ManagedEnvironmentPreviewClient

        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            return ConnectedEnvironmentClient
        else:
            return ManagedEnvironmentPreviewClient

    def get_argument_environment_type(self):
        return self.get_param("environment_type")
