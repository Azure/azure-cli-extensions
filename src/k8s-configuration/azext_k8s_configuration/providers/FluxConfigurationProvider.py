# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import os

from azure.cli.core.azclierror import DeploymentError, ResourceNotFoundError, ValidationError
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.commands.client_factory import get_subscription_id

from azure.core.exceptions import HttpResponseError
from knack.log import get_logger

from ..confirm import user_confirmation_factory
from .._client_factory import (
    cf_resources,
    k8s_configuration_fluxconfig_client,
    k8s_configuration_extension_client
)
from ..utils import (
    get_parent_api_version,
    get_cluster_rp,
    get_data_from_key_or_file,
    parse_dependencies,
    parse_duration,
    has_prune_enabled,
    to_base64,
    is_dogfood_cluster
)
from ..validators import (
    validate_cc_registration,
    validate_known_hosts,
    validate_repository_ref,
    validate_duration,
    validate_git_repository,
    validate_private_key,
    validate_url_with_params
)
from .. import consts
from ..vendored_sdks.v2021_11_01_preview.models import (
    FluxConfiguration,
    FluxConfigurationPatch,
    GitRepositoryDefinition,
    RepositoryRefDefinition,
    KustomizationDefinition,
    DependsOnDefinition
)
from ..vendored_sdks.v2021_05_01_preview.models import (
    Extension,
    Identity
)
from .SourceControlConfigurationProvider import SourceControlConfigurationProvider

logger = get_logger(__name__)


class FluxConfigurationProvider:
    def __init__(self, cmd):
        self.extension_client = k8s_configuration_extension_client(cmd.cli_ctx)
        self.source_control_configuration_provider = SourceControlConfigurationProvider(cmd)
        self.cmd = cmd
        self.client = k8s_configuration_fluxconfig_client(cmd.cli_ctx)

    def show(self, resource_group_name, cluster_type, cluster_name, name):
        """Get an existing Kubernetes Source Control Configuration.

        """
        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        try:
            config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
            return config
        except HttpResponseError as ex:
            # Customize the error message for resources not found
            if ex.response.status_code == 404:
                # If Cluster not found
                if ex.message.__contains__("(ResourceNotFound)"):
                    message = ex.message
                    recommendation = 'Verify that the --cluster-type is correct and the Resource ' \
                                     '{0}/{1}/{2} exists'.format(cluster_rp, cluster_type, cluster_name)
                # If Configuration not found
                elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                    message = '(FluxConfigurationNotFound) The Resource {0}/{1}/{2}/' \
                              'Microsoft.KubernetesConfiguration/fluxConfigurations/{3} ' \
                              'could not be found!' \
                              .format(cluster_rp, cluster_type, cluster_name, name)
                    recommendation = 'Verify that the Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration' \
                                     '/fluxConfigurations/{3} exists'.format(cluster_rp, cluster_type,
                                                                             cluster_name, name)
                else:
                    message = ex.message
                    recommendation = ''
                raise ResourceNotFoundError(message, recommendation) from ex
            raise ex

    def list(self, resource_group_name, cluster_type, cluster_name):
        cluster_rp = get_cluster_rp(cluster_type)
        return self.client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)

    # pylint: disable=too-many-locals
    def create(self, resource_group_name, cluster_type, cluster_name, name, url=None, scope='cluster',
               namespace='default', kind=consts.GIT, timeout=None, sync_interval=None, branch=None,
               tag=None, semver=None, commit=None, local_auth_ref=None, ssh_private_key=None,
               ssh_private_key_file=None, https_user=None, https_key=None, https_ca_cert=None,
               https_ca_cert_file=None, known_hosts=None, known_hosts_file=None, suspend=False,
               kustomization=None, no_wait=False):

        # Determine the cluster RP
        cluster_rp = get_cluster_rp(cluster_type)
        dp_source_kind = ""
        git_repository = None

        # Validate and Create the Data before checking the cluster compataibility
        if kind == consts.GIT:
            dp_source_kind = consts.GIT_REPOSITORY
            git_repository = self._validate_and_get_gitrepository(url, branch, tag, semver, commit, timeout,
                                                                  sync_interval, ssh_private_key,
                                                                  ssh_private_key_file, https_user,
                                                                  https_key, https_ca_cert, https_ca_cert_file,
                                                                  known_hosts, known_hosts_file, local_auth_ref, True)

        if kustomization:
            # Convert the Internal List Representation of Kustomization to Dictionary
            kustomization = {k.name: k.to_KustomizationDefinition() for k in kustomization}
        else:
            logger.warning(consts.NO_KUSTOMIZATIONS_WARNING)
            kustomization = {
                consts.DEFAULT_KUSTOMIZATION_NAME: KustomizationDefinition()
            }

        # Get the protected settings and validate the private key value
        protected_settings = get_protected_settings(
            ssh_private_key, ssh_private_key_file, https_user, https_key
        )
        if protected_settings and consts.SSH_PRIVATE_KEY_KEY in protected_settings:
            validate_private_key(protected_settings['sshPrivateKey'])

        flux_configuration = FluxConfiguration(
            scope=scope,
            namespace=namespace,
            source_kind=dp_source_kind,
            git_repository=git_repository,
            suspend=suspend,
            kustomizations=kustomization,
            configuration_protected_settings=protected_settings,
        )

        self._validate_source_control_config_not_installed(resource_group_name, cluster_type, cluster_name)
        self._validate_extension_install(resource_group_name, cluster_rp, cluster_type, cluster_name, no_wait)

        logger.warning("Creating the flux configuration '%s' in the cluster. This may take a few minutes...", name)

        return sdk_no_wait(no_wait, self.client.begin_create_or_update, resource_group_name, cluster_rp,
                           cluster_type, cluster_name, name, flux_configuration)

    def update(self, resource_group_name, cluster_type, cluster_name, name, url=None,
               timeout=None, sync_interval=None, branch=None, tag=None, semver=None,
               commit=None, local_auth_ref=None, ssh_private_key=None, ssh_private_key_file=None,
               https_user=None, https_key=None, https_ca_cert=None, https_ca_cert_file=None, known_hosts=None,
               known_hosts_file=None, suspend=None, kustomization=None, no_wait=False):
        # Determine the cluster RP
        cluster_rp = get_cluster_rp(cluster_type)

        git_repository = None
        if any([url, branch, tag, semver, commit,
                timeout, sync_interval,
                ssh_private_key, ssh_private_key_file,
                https_user, https_key, https_ca_cert,
                https_ca_cert_file, known_hosts,
                known_hosts_file, local_auth_ref]):
            git_repository = self._validate_and_get_gitrepository(url, branch, tag, semver, commit,
                                                                  timeout, sync_interval,
                                                                  ssh_private_key, ssh_private_key_file,
                                                                  https_user, https_key, https_ca_cert,
                                                                  https_ca_cert_file, known_hosts,
                                                                  known_hosts_file, local_auth_ref, False)

        if kustomization:
            # Convert the Internal List Representation of Kustomization to Dictionary
            kustomization = {k.name: k.to_KustomizationDefinition() for k in kustomization}

        # Get the protected settings and validate the private key value
        protected_settings = get_protected_settings(
            ssh_private_key, ssh_private_key_file, https_user, https_key
        )
        if protected_settings and consts.SSH_PRIVATE_KEY_KEY in protected_settings:
            validate_private_key(protected_settings['sshPrivateKey'])

        flux_configuration = FluxConfigurationPatch(
            git_repository=git_repository,
            suspend=suspend,
            kustomizations=kustomization,
            configuration_protected_settings=protected_settings,
        )

        return sdk_no_wait(no_wait, self.client.begin_update, resource_group_name, cluster_rp,
                           cluster_type, cluster_name, name, flux_configuration)

    def create_kustomization(self, resource_group_name, cluster_type, cluster_name, name,
                             kustomization_name, dependencies=None, timeout=None, sync_interval=None,
                             retry_interval=None, path='', prune=False, force=False, no_wait=False):
        # Pre-Validation
        validate_duration("--timeout", timeout)
        validate_duration("--sync-interval", sync_interval)
        validate_duration("--retry-interval", retry_interval)

        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        if kustomization_name in current_config.kustomizations:
            raise ValidationError(
                consts.CREATE_KUSTOMIZATION_EXIST_ERROR.format(kustomization_name, name),
                consts.CREATE_KUSTOMIZATION_EXIST_HELP
            )

        # Add the dependencies in their model to the kustomization
        model_dependencies = None
        if dependencies:
            model_dependencies = []
            for dep in parse_dependencies(dependencies):
                model_dependencies.append(
                    DependsOnDefinition(
                        kustomization_name=dep
                    )
                )

        kustomization = {
            kustomization_name: KustomizationDefinition(
                path=path,
                depends_on=model_dependencies,
                timeout_in_seconds=parse_duration(timeout),
                sync_interval_in_seconds=parse_duration(sync_interval),
                retry_interval_in_seconds=parse_duration(retry_interval),
                prune=prune,
                force=force
            )
        }
        flux_configuration_patch = FluxConfigurationPatch(
            kustomizations=kustomization
        )
        return sdk_no_wait(no_wait, self.client.begin_update, resource_group_name, cluster_rp,
                           cluster_type, cluster_name, name, flux_configuration_patch)

    def update_kustomization(self, resource_group_name, cluster_type, cluster_name, name,
                             kustomization_name, dependencies=None, timeout=None, sync_interval=None,
                             retry_interval=None, path=None, prune=False, force=False, no_wait=False):
        # Pre-Validation
        validate_duration("--timeout", timeout)
        validate_duration("--sync-interval", sync_interval)
        validate_duration("--retry-interval", retry_interval)

        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        if kustomization_name not in current_config.kustomizations:
            raise ValidationError(
                consts.UPDATE_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name, name),
                consts.UPDATE_KUSTOMIZATION_NO_EXIST_HELP
            )

        # Add the dependencies in their model to the kustomization
        model_dependencies = None
        if dependencies:
            model_dependencies = []
            for dep in parse_dependencies(dependencies):
                model_dependencies.append(
                    DependsOnDefinition(
                        kustomization_name=dep
                    )
                )

        kustomization = {
            kustomization_name: KustomizationDefinition(
                path=path,
                depends_on=model_dependencies,
                timeout_in_seconds=parse_duration(timeout),
                sync_interval_in_seconds=parse_duration(sync_interval),
                retry_interval_in_seconds=parse_duration(retry_interval),
                prune=prune,
                force=force
            )
        }
        flux_configuration_patch = FluxConfigurationPatch(
            kustomizations=kustomization
        )
        return sdk_no_wait(no_wait, self.client.begin_update, resource_group_name, cluster_rp,
                           cluster_type, cluster_name, name, flux_configuration_patch)

    def delete_kustomization(self, resource_group_name, cluster_type, cluster_name, name,
                             kustomization_name, no_wait=False, yes=False):
        # Confirmation message for deletes
        user_confirmation_factory(self.cmd, yes)

        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)

        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        if kustomization_name not in current_config.kustomizations:
            raise ValidationError(
                consts.DELETE_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name, name),
                consts.DELETE_KUSTOMIZATION_NO_EXIST_HELP
            )

        if current_config.kustomizations[kustomization_name].prune:
            logger.warning("Prune is enabled on this kustomization. Deleting a kustomization "
                           "with prune enabled will also delete the Kubernetes objects "
                           "deployed by the kustomization.")
            user_confirmation_factory(self.cmd, yes, "Do you want to continue?")

        kustomization = {
            kustomization_name: None
        }
        flux_configuration_patch = FluxConfigurationPatch(
            kustomizations=kustomization
        )
        return sdk_no_wait(no_wait, self.client.begin_update, resource_group_name, cluster_rp,
                           cluster_type, cluster_name, name, flux_configuration_patch)

    def list_kustomization(self, resource_group_name, cluster_type, cluster_name, name):
        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        return current_config.kustomizations

    def show_kustomization(self, resource_group_name, cluster_type, cluster_name, name, kustomization_name):
        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        if kustomization_name not in current_config.kustomizations:
            raise ValidationError(
                consts.SHOW_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name, name),
                consts.SHOW_KUSTOMIZATION_NO_EXIST_HELP
            )
        return {kustomization_name: current_config.kustomizations[kustomization_name]}

    def list_deployed_object(self, resource_group_name, cluster_type, cluster_name, name):
        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        return current_config.statuses

    def show_deployed_object(self, resource_group_name, cluster_type, cluster_name, name,
                             object_name, object_namespace, object_kind):
        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)
        current_config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)

        for status in current_config.statuses:
            if status.name == object_name and status.namespace == object_namespace and status.kind == object_kind:
                return status
        raise ValidationError(
            consts.SHOW_DEPLOYED_OBJECT_NO_EXIST_ERROR.format(object_name, object_namespace, object_kind, name),
            consts.SHOW_DEPLOYED_OBJECT_NO_EXIST_HELP
        )

    def delete(self, resource_group_name, cluster_type, cluster_name, name, force, no_wait, yes):
        # Confirmation message for deletes
        user_confirmation_factory(self.cmd, yes)

        # Determine ClusterRP
        cluster_rp = get_cluster_rp(cluster_type)

        config = None
        try:
            config = self.client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        except HttpResponseError:
            logger.warning("No flux configuration with name '%s' found on cluster '%s', so nothing to delete",
                           name, cluster_name)
            return None

        if has_prune_enabled(config):
            logger.warning("Prune is enabled on one or more of your kustomizations. Deleting a Flux "
                           "configuration with prune enabled will also delete the Kubernetes objects "
                           "deployed by the kustomization(s).")
            user_confirmation_factory(self.cmd, yes, "Do you want to continue?")

        if not force:
            logger.info("Deleting the flux configuration from the cluster. This may take a few minutes...")
        return sdk_no_wait(no_wait, self.client.begin_delete, resource_group_name, cluster_rp, cluster_type,
                           cluster_name, name, force_delete=force)

    def _is_deferred(self):
        if '--defer' in self.cmd.cli_ctx.data.get('safe_params'):
            return True
        return False

    def _validate_source_control_config_not_installed(self, resource_group_name, cluster_type, cluster_name):
        # Validate if we are able to install the flux configuration
        configs = self.source_control_configuration_provider.list(resource_group_name, cluster_type, cluster_name)
        # configs is an iterable, no len() so we have to iterate to check for configs
        for _ in configs:
            raise DeploymentError(
                consts.SCC_EXISTS_ON_CLUSTER_ERROR,
                consts.SCC_EXISTS_ON_CLUSTER_HELP)

    def _validate_extension_install(self, resource_group_name, cluster_rp, cluster_type, cluster_name, no_wait):
        # Validate if the extension is installed, if not, install it
        extensions = self.extension_client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)
        flux_extension = None
        for extension in extensions:
            if extension.extension_type.lower() == consts.FLUX_EXTENSION_TYPE:
                flux_extension = extension
                break
        if not flux_extension:
            logger.warning("'Microsoft.Flux' extension not found on the cluster, installing it now."
                           " This may take a few minutes...")

            extension = Extension(
                extension_type="microsoft.flux",
                auto_upgrade_minor_version=True,
                release_train=os.getenv(consts.FLUX_EXTENSION_RELEASETRAIN),
                version=os.getenv(consts.FLUX_EXTENSION_VERSION)
            )
            if not is_dogfood_cluster(self.cmd):
                extension = self.__add_identity(extension,
                                                resource_group_name,
                                                cluster_rp,
                                                cluster_type,
                                                cluster_name)

            logger.info("Starting extension creation on the cluster. This might take a few minutes...")
            sdk_no_wait(no_wait, self.extension_client.begin_create, resource_group_name, cluster_rp, cluster_type,
                        cluster_name, "flux", extension).result()
            # Only show that we have received a success when we have --no-wait
            if not no_wait:
                logger.warning("'Microsoft.Flux' extension was successfully installed on the cluster")
        elif flux_extension.provisioning_state == consts.CREATING:
            raise DeploymentError(
                consts.FLUX_EXTENSION_CREATING_ERROR,
                consts.FLUX_EXTENSION_CREATING_HELP
            )
        elif flux_extension.provisioning_state != consts.SUCCEEDED:
            # Print the error detail so the user know how to fix it
            if flux_extension.error_detail:
                logger.error('%s %s', flux_extension.error_detail.code, flux_extension.error_detail.message)
            raise DeploymentError(
                consts.FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_ERROR,
                consts.FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_HELP
            )

    def _validate_and_get_gitrepository(self, url, branch, tag, semver, commit, timeout, sync_interval,
                                        ssh_private_key, ssh_private_key_file, https_user, https_key,
                                        https_ca_cert, https_ca_cert_file, known_hosts, known_hosts_file,
                                        local_auth_ref, is_create):
        # Pre-Validation
        validate_duration("--timeout", timeout)
        validate_duration("--sync-interval", sync_interval)

        # Get the known hosts data and validate it
        knownhost_data = get_data_from_key_or_file(known_hosts, known_hosts_file, strip_newline=True)
        if knownhost_data:
            validate_known_hosts(knownhost_data)

        https_ca_data = get_data_from_key_or_file(https_ca_cert, https_ca_cert_file, strip_newline=True)

        # Validate registration with the RP endpoint
        validate_cc_registration(self.cmd)

        if is_create:
            validate_git_repository(url)
            validate_url_with_params(url, ssh_private_key, ssh_private_key_file,
                                     known_hosts, known_hosts_file, https_user, https_key)
            validate_repository_ref(branch, tag, semver, commit)

        repository_ref = None
        if any([branch, tag, semver, commit]):
            repository_ref = RepositoryRefDefinition(
                branch=branch,
                tag=tag,
                semver=semver,
                commit=commit
            )

        # Encode the https username to base64
        if https_user:
            https_user = to_base64(https_user)

        return GitRepositoryDefinition(
            url=url,
            timeout_in_seconds=parse_duration(timeout),
            sync_interval_in_seconds=parse_duration(sync_interval),
            repository_ref=repository_ref,
            ssh_known_hosts=knownhost_data,
            https_user=https_user,
            local_auth_ref=local_auth_ref,
            https_ca_file=https_ca_data
        )

    def __add_identity(self, extension_instance, resource_group_name, cluster_rp, cluster_type, cluster_name):
        subscription_id = get_subscription_id(self.cmd.cli_ctx)
        resources = cf_resources(self.cmd.cli_ctx, subscription_id)

        cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(subscription_id,
                                                                                                   resource_group_name,
                                                                                                   cluster_rp,
                                                                                                   cluster_type,
                                                                                                   cluster_name)

        if cluster_rp == consts.MANAGED_RP_NAMESPACE:
            return extension_instance
        parent_api_version = get_parent_api_version(cluster_rp)
        try:
            resource = resources.get_by_id(cluster_resource_id, parent_api_version)
            location = str(resource.location.lower())
        except HttpResponseError as ex:
            raise ex
        identity_type = "SystemAssigned"

        extension_instance.identity = Identity(type=identity_type)
        extension_instance.location = location
        return extension_instance


def get_protected_settings(ssh_private_key, ssh_private_key_file, https_user, https_key):
    protected_settings = {}
    ssh_private_key_data = get_data_from_key_or_file(ssh_private_key, ssh_private_key_file)

    # Add gitops private key data to protected settings if exists
    # Dry-run all key types to determine if the private key is in a valid format
    if ssh_private_key_data:
        protected_settings[consts.SSH_PRIVATE_KEY_KEY] = ssh_private_key_data

    # Check if both httpsUser and httpsKey exist, then add to protected settings
    if https_user and https_key:
        protected_settings[consts.HTTPS_KEY_KEY] = to_base64(https_key)

    # Return the protected settings dict if there are any values there
    return protected_settings if len(protected_settings) > 0 else None
