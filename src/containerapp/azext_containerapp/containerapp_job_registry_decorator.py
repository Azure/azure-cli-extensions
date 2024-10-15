# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-branches, too-many-boolean-expressions, no-else-return, logging-fstring-interpolation

from copy import deepcopy
from urllib.parse import urlparse

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError)

from azure.cli.command_modules.containerapp.containerapp_job_registry_decorator import ContainerAppJobRegistrySetDecorator
from azure.cli.command_modules.containerapp._utils import safe_get, _get_acr_cred, store_as_secret_and_return_secret_ref, safe_set, \
    is_registry_msi_system, set_managed_identity

from azure.mgmt.core.tools import parse_resource_id, is_valid_resource_id
from knack.log import get_logger

from ._constants import ACR_IMAGE_SUFFIX
from ._models import (RegistryCredentials as RegistryCredentialsModel)
from ._utils import env_has_managed_identity
from ._validators import validate_create

logger = get_logger(__name__)


class ContainerAppJobRegistryPreviewSetDecorator(ContainerAppJobRegistrySetDecorator):
    def validate_arguments(self):
        super().validate_arguments()
        validate_create(registry_identity=self.get_argument_identity(), registry_pass=self.get_argument_password(), registry_user=self.get_argument_username(), registry_server=self.get_argument_server(), no_wait=self.get_argument_no_wait())

    # copy from parent
    def parent_construct_payload(self):
        self.set_up_get_existing_secrets()

        registries_def = safe_get(self.containerappjob_def, "properties", "configuration", "registries", default=[])
        safe_set(self.new_containerappjob, "properties", "configuration", "registries", value=registries_def)

        if (not self.get_argument_username() or not self.get_argument_password()) and not self.get_argument_identity():
            # If registry is Azure Container Registry, we can try inferring credentials
            if ACR_IMAGE_SUFFIX not in self.get_argument_server():
                raise RequiredArgumentMissingError(
                    'Registry username and password are required if you are not using Azure Container Registry.')
            if not self.get_argument_disable_warnings():
                logger.warning('No credential was provided to access Azure Container Registry. Trying to look up...')
            parsed = urlparse(self.get_argument_server())
            registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

            try:
                username, password, _ = _get_acr_cred(self.cmd.cli_ctx, registry_name)
                self.set_argument_username(username)
                self.set_argument_password(password)
            except Exception as ex:
                raise RequiredArgumentMissingError(
                    'Failed to retrieve credentials for container registry. Please provide the registry username and password') from ex

        # Check if updating existing registry
        updating_existing_registry = False
        for r in registries_def:
            if r['server'].lower() == self.get_argument_server().lower():
                if not self.get_argument_disable_warnings():
                    logger.warning("Updating existing registry.")
                updating_existing_registry = True
                if self.get_argument_username():
                    r["username"] = self.get_argument_username()
                    r["identity"] = None
                if self.get_argument_password():
                    r["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                        self.new_containerappjob["properties"]["configuration"]["secrets"],
                        r["username"],
                        r["server"],
                        self.get_argument_password(),
                        update_existing_secret=True)
                    r["identity"] = None
                if self.get_argument_identity():
                    r["identity"] = self.get_argument_identity()
                    r["username"] = None
                    r["passwordSecretRef"] = None

        # If not updating existing registry, add as new registry
        if not updating_existing_registry:
            registry = deepcopy(RegistryCredentialsModel)
            registry["server"] = self.get_argument_server()
            if not self.get_argument_identity():
                registry["username"] = self.get_argument_username()
                registry["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                    self.new_containerappjob["properties"]["configuration"]["secrets"],
                    self.get_argument_username(),
                    self.get_argument_server(),
                    self.get_argument_password(),
                    update_existing_secret=True)
            else:
                registry["identity"] = self.get_argument_identity()

            registries_def.append(registry)

        # preview logic
        self.set_up_registry_identity()

    def set_up_registry_identity(self):
        identity = self.get_argument_identity()
        if identity:
            identity_def = safe_get(self.containerappjob_def, "identity", default={})
            safe_set(self.new_containerappjob, "identity", value=identity_def)

            if is_registry_msi_system(identity):
                set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerappjob, system_assigned=True)

            if is_valid_resource_id(identity):
                env_id = safe_get(self.containerappjob_def, "properties", "environmentId", default="")
                parsed_managed_env = parse_resource_id(env_id)
                managed_env_name = parsed_managed_env['name']
                managed_env_rg = parsed_managed_env['resource_group']
                if not env_has_managed_identity(self.cmd, managed_env_rg, managed_env_name, identity):
                    set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.new_containerappjob, user_assigned=[identity])

    def construct_payload(self):
        self.parent_construct_payload()
