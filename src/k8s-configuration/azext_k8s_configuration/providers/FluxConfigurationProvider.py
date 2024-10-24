# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import os

from azure.cli.core.azclierror import (
    DeploymentError,
    ResourceNotFoundError,
    ValidationError,
    UnrecognizedArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.commands.client_factory import get_subscription_id

from azure.core.exceptions import HttpResponseError
from knack.log import get_logger

from ..confirm import user_confirmation_factory
from .._client_factory import (
    cf_resources,
    k8s_configuration_extension_client,
    k8s_configuration_sourcecontrol_client,
)
from ..utils import (
    get_cluster_rp_api_version,
    get_data_from_key_or_file,
    parse_dependencies,
    parse_duration,
    has_prune_enabled,
    to_base64,
    is_dogfood_cluster,
)
from ..validators import (
    validate_bucket_url,
    validate_cc_registration,
    validate_git_url,
    validate_known_hosts,
    validate_repository_ref,
    validate_azure_blob_auth,
    validate_duration,
    validate_private_key,
    validate_url_with_params,
)
from .. import consts
from ..vendored_sdks.v2024_04_01_preview.models import (
    FluxConfiguration,
    FluxConfigurationPatch,
    GitRepositoryDefinition,
    GitRepositoryPatchDefinition,
    BucketDefinition,
    BucketPatchDefinition,
    AzureBlobDefinition,
    AzureBlobPatchDefinition,
    ServicePrincipalDefinition,
    ManagedIdentityDefinition,
    RepositoryRefDefinition,
    KustomizationDefinition,
    KustomizationPatchDefinition,
    SourceKindType,
)
from ..vendored_sdks.v2022_07_01.models import Extension, Identity

logger = get_logger(__name__)


def show_config(cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=None):
    """Get an existing Kubernetes Source Control Configuration."""

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)
    try:
        config = client.get(
            resource_group_name, cluster_rp, cluster_type, cluster_name, name
        )
        return config
    except HttpResponseError as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = ex.message
                recommendation = (
                    "Verify that the --cluster-type is correct and the Resource "
                    "{0}/{1}/{2} exists".format(cluster_rp, cluster_type, cluster_name)
                )
            # If Configuration not found
            elif ex.message.__contains__(
                "Operation returned an invalid status code 'Not Found'"
            ):
                message = (
                    "(FluxConfigurationNotFound) The Resource {0}/{1}/{2}/"
                    "Microsoft.KubernetesConfiguration/fluxConfigurations/{3} "
                    "could not be found!".format(
                        cluster_rp, cluster_type, cluster_name, name
                    )
                )
                recommendation = (
                    "Verify that the Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration"
                    "/fluxConfigurations/{3} exists".format(
                        cluster_rp, cluster_type, cluster_name, name
                    )
                )
            else:
                message = ex.message
                recommendation = ""
            raise ResourceNotFoundError(message, recommendation) from ex
        raise ex


def list_configs(cmd, client, resource_group_name, cluster_type, cluster_name, cluster_resource_provider=None):
    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


# pylint: disable=too-many-locals
def create_config(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    url,
    bucket_name=None,
    scope="cluster",
    namespace="default",
    kind=consts.GIT,
    timeout=None,
    sync_interval=None,
    branch=None,
    tag=None,
    semver=None,
    commit=None,
    local_auth_ref=None,
    ssh_private_key=None,
    ssh_private_key_file=None,
    https_user=None,
    https_key=None,
    https_ca_cert=None,
    https_ca_cert_file=None,
    known_hosts=None,
    known_hosts_file=None,
    bucket_access_key=None,
    bucket_secret_key=None,
    bucket_insecure=False,
    suspend=False,
    kustomization=None,
    no_wait=False,
    container_name=None,
    sp_tenant_id=None,
    sp_client_id=None,
    sp_client_cert=None,
    sp_client_cert_password=None,
    sp_client_secret=None,
    sp_client_cert_send_chain=False,
    account_key=None,
    sas_token=None,
    mi_client_id=None,
    cluster_resource_provider=None,
):

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    factory = source_kind_generator_factory(
        kind,
        url=url,
        bucket_name=bucket_name,
        timeout=timeout,
        sync_interval=sync_interval,
        branch=branch,
        tag=tag,
        semver=semver,
        commit=commit,
        local_auth_ref=local_auth_ref,
        ssh_private_key=ssh_private_key,
        ssh_private_key_file=ssh_private_key_file,
        https_user=https_user,
        https_key=https_key,
        https_ca_cert=https_ca_cert,
        https_ca_cert_file=https_ca_cert_file,
        known_hosts=known_hosts,
        known_hosts_file=known_hosts_file,
        bucket_access_key=bucket_access_key,
        bucket_secret_key=bucket_secret_key,
        bucket_insecure=bucket_insecure,
        container_name=container_name,
        account_key=account_key,
        sas_token=sas_token,
        sp_tenant_id=sp_tenant_id,
        sp_client_id=sp_client_id,
        sp_client_cert=sp_client_cert,
        sp_client_cert_password=sp_client_cert_password,
        sp_client_secret=sp_client_secret,
        sp_client_cert_send_chain=sp_client_cert_send_chain,
        mi_client_id=mi_client_id,
    )

    # This update func is a generated update function that modifies
    # the FluxConfiguration object with the appropriate source kind
    update_func = factory.generate_update_func()

    if kustomization:
        # Convert the Internal List Representation of Kustomization to Dictionary
        kustomization = {k.name: k.to_KustomizationDefinition() for k in kustomization}
    else:
        logger.warning(consts.NO_KUSTOMIZATIONS_WARNING)
        kustomization = {consts.DEFAULT_KUSTOMIZATION_NAME: KustomizationDefinition()}

    # Get the protected settings and validate the private key value
    protected_settings = get_protected_settings(
        ssh_private_key, ssh_private_key_file, https_key, bucket_secret_key
    )
    if protected_settings and consts.SSH_PRIVATE_KEY_KEY in protected_settings:
        validate_private_key(protected_settings["sshPrivateKey"])

    flux_configuration = FluxConfiguration(
        scope=scope,
        namespace=namespace,
        suspend=suspend,
        kustomizations=kustomization,
        configuration_protected_settings=protected_settings,
    )
    flux_configuration = update_func(flux_configuration)

    _validate_source_control_config_not_installed(
        cmd, resource_group_name, cluster_rp, cluster_type, cluster_name
    )
    _validate_extension_install(
        cmd, resource_group_name, cluster_rp, cluster_type, cluster_name, no_wait
    )

    logger.warning(
        "Creating the flux configuration '%s' in the cluster. This may take a few minutes...",
        name,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        flux_configuration,
    )


def update_config(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    kind=None,
    url=None,
    bucket_name=None,
    timeout=None,
    sync_interval=None,
    branch=None,
    tag=None,
    semver=None,
    commit=None,
    local_auth_ref=None,
    ssh_private_key=None,
    ssh_private_key_file=None,
    https_user=None,
    https_key=None,
    https_ca_cert=None,
    https_ca_cert_file=None,
    known_hosts=None,
    known_hosts_file=None,
    bucket_access_key=None,
    bucket_secret_key=None,
    bucket_insecure=None,
    suspend=None,
    kustomization=None,
    no_wait=False,
    yes=False,
    container_name=None,
    sp_tenant_id=None,
    sp_client_id=None,
    sp_client_cert=None,
    sp_client_cert_password=None,
    sp_client_secret=None,
    sp_client_cert_send_chain=False,
    account_key=None,
    sas_token=None,
    mi_client_id=None,
    cluster_resource_provider=None,
):

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    if not kind:
        kind = convert_to_cli_source_kind(config.source_kind)
    factory = source_kind_generator_factory(
        kind,
        url=url,
        bucket_name=bucket_name,
        timeout=timeout,
        sync_interval=sync_interval,
        branch=branch,
        tag=tag,
        semver=semver,
        commit=commit,
        local_auth_ref=local_auth_ref,
        ssh_private_key=ssh_private_key,
        ssh_private_key_file=ssh_private_key_file,
        https_user=https_user,
        https_key=https_key,
        https_ca_cert=https_ca_cert,
        https_ca_cert_file=https_ca_cert_file,
        known_hosts=known_hosts,
        known_hosts_file=known_hosts_file,
        bucket_access_key=bucket_access_key,
        bucket_secret_key=bucket_secret_key,
        bucket_insecure=bucket_insecure,
        container_name=container_name,
        account_key=account_key,
        sas_token=sas_token,
        sp_tenant_id=sp_tenant_id,
        sp_client_id=sp_client_id,
        sp_client_cert=sp_client_cert,
        sp_client_cert_password=sp_client_cert_password,
        sp_client_secret=sp_client_secret,
        sp_client_cert_send_chain=sp_client_cert_send_chain,
        mi_client_id=mi_client_id,
    )

    # This update func is a generated update function that modifies
    # the FluxConfiguration object with the appropriate source kind
    # If we update the source kind, we will also null out the other
    # kind type
    changed_source_kind = (
        kind.lower() != convert_to_cli_source_kind(config.source_kind).lower()
    )
    update_func = factory.generate_patch_update_func(changed_source_kind)

    if changed_source_kind:
        user_confirmation_factory(
            cmd,
            yes,
            f"You are choosing to migrate from source kind '{convert_to_cli_source_kind(config.source_kind).lower()}' "
            + f"to source kind '{kind.lower()}'. Changing your source repository may also require you to change your "
            + "kustomizations. Are you sure you want to change kinds?",
        )

    if kustomization:
        # Convert the Internal List Representation of Kustomization to Dictionary
        kustomization = {
            k.name: k.to_KustomizationPatchDefinition() for k in kustomization
        }

    # Get the protected settings and validate the private key value
    protected_settings = get_protected_settings(
        ssh_private_key, ssh_private_key_file, https_key, bucket_secret_key
    )
    if protected_settings and consts.SSH_PRIVATE_KEY_KEY in protected_settings:
        validate_private_key(protected_settings["sshPrivateKey"])

    flux_configuration = FluxConfigurationPatch(
        suspend=suspend,
        kustomizations=kustomization,
        configuration_protected_settings=protected_settings,
    )
    flux_configuration = update_func(flux_configuration)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        flux_configuration,
    )


def create_kustomization(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    kustomization_name,
    dependencies=None,
    timeout=None,
    sync_interval=None,
    retry_interval=None,
    path="",
    prune=None,
    force=None,
    disable_health_check=None,
    no_wait=False,
    cluster_resource_provider=None,
):

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    # Pre-Validation
    validate_duration("--timeout", timeout)
    validate_duration("--sync-interval", sync_interval)
    validate_duration("--retry-interval", retry_interval)

    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    if kustomization_name in current_config.kustomizations:
        raise ValidationError(
            consts.CREATE_KUSTOMIZATION_EXIST_ERROR.format(kustomization_name, name),
            consts.CREATE_KUSTOMIZATION_EXIST_HELP,
        )

    kustomization = {
        kustomization_name: KustomizationPatchDefinition(
            path=path,
            depends_on=parse_dependencies(dependencies),
            timeout_in_seconds=parse_duration(timeout),
            sync_interval_in_seconds=parse_duration(sync_interval),
            retry_interval_in_seconds=parse_duration(retry_interval),
            prune=prune,
            force=force,
            wait=disable_health_check!=True,
        )
    }
    flux_configuration_patch = FluxConfigurationPatch(kustomizations=kustomization)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        flux_configuration_patch,
    )


def update_kustomization(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    kustomization_name,
    dependencies=None,
    timeout=None,
    sync_interval=None,
    retry_interval=None,
    path=None,
    prune=None,
    force=None,
    disable_health_check=None,
    no_wait=False,
    cluster_resource_provider=None,
):

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    # Pre-Validation
    validate_duration("--timeout", timeout)
    validate_duration("--sync-interval", sync_interval)
    validate_duration("--retry-interval", retry_interval)

    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    if kustomization_name not in current_config.kustomizations:
        raise ValidationError(
            consts.UPDATE_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name, name),
            consts.UPDATE_KUSTOMIZATION_NO_EXIST_HELP,
        )

    kustomization = {
        kustomization_name: KustomizationPatchDefinition(
            path=path,
            depends_on=parse_dependencies(dependencies),
            timeout_in_seconds=parse_duration(timeout),
            sync_interval_in_seconds=parse_duration(sync_interval),
            retry_interval_in_seconds=parse_duration(retry_interval),
            prune=prune,
            force=force,
            wait=disable_health_check!=True,
        )
    }
    flux_configuration_patch = FluxConfigurationPatch(kustomizations=kustomization)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        flux_configuration_patch,
    )


def delete_kustomization(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    kustomization_name,
    no_wait=False,
    yes=False,
    cluster_resource_provider=None,
):

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    # Confirmation message for deletes
    user_confirmation_factory(cmd, yes)

    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    if kustomization_name not in current_config.kustomizations:
        raise ValidationError(
            consts.DELETE_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name, name),
            consts.DELETE_KUSTOMIZATION_NO_EXIST_HELP,
        )

    if current_config.kustomizations[kustomization_name].prune:
        logger.warning(
            "Prune is enabled on this kustomization. Deleting a kustomization "
            "with prune enabled will also delete the Kubernetes objects "
            "deployed by the kustomization."
        )
        user_confirmation_factory(cmd, yes, "Do you want to continue?")

    kustomization = {kustomization_name: None}
    flux_configuration_patch = FluxConfigurationPatch(kustomizations=kustomization)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        flux_configuration_patch,
    )


def list_kustomization(
    cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=None
):
    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    return current_config.kustomizations


def show_kustomization(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    kustomization_name,
    cluster_resource_provider=None,
):
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )
    if kustomization_name not in current_config.kustomizations:
        raise ValidationError(
            consts.SHOW_KUSTOMIZATION_NO_EXIST_ERROR.format(kustomization_name),
            consts.SHOW_KUSTOMIZATION_NO_EXIST_HELP,
        )
    return {kustomization_name: current_config.kustomizations[kustomization_name]}


def list_deployed_object(
    cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=None
):
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)
    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_rp
    )
    return current_config.statuses


def show_deployed_object(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    object_name,
    object_namespace,
    object_kind,
    cluster_resource_provider=None,
):
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)
    current_config = show_config(
        cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
    )

    for status in current_config.statuses:
        if (
            status.name == object_name
            and status.namespace == object_namespace
            and status.kind == object_kind
        ):
            return status
    raise ValidationError(
        consts.SHOW_DEPLOYED_OBJECT_NO_EXIST_ERROR.format(
            object_name, object_namespace, object_kind, name
        ),
        consts.SHOW_DEPLOYED_OBJECT_NO_EXIST_HELP,
    )


def delete_config(
    cmd,
    client,
    resource_group_name,
    cluster_type,
    cluster_name,
    name,
    force=False,
    no_wait=False,
    yes=False,
    cluster_resource_provider=None,
):

    # Confirmation message for deletes
    user_confirmation_factory(cmd, yes)

    # Get Resource Provider to call
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    validate_cc_registration(cmd)

    config = None
    try:
        config = show_config(
            cmd, client, resource_group_name, cluster_type, cluster_name, name, cluster_resource_provider=cluster_rp
        )
    except HttpResponseError:
        logger.warning(
            "No flux configuration with name '%s' found on cluster '%s', so nothing to delete",
            name,
            cluster_name,
        )
        return None

    if has_prune_enabled(config):
        logger.warning(
            "Prune is enabled on one or more of your kustomizations. Deleting a Flux "
            "configuration with prune enabled will also delete the Kubernetes objects "
            "deployed by the kustomization(s)."
        )
        user_confirmation_factory(cmd, yes, "Do you want to continue?")

    if not force:
        logger.info(
            "Deleting the flux configuration from the cluster. This may take a few minutes..."
        )
    return sdk_no_wait(
        no_wait,
        client.begin_delete,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        force_delete=force,
    )


def _validate_source_control_config_not_installed(
    cmd, resource_group_name, cluster_rp, cluster_type, cluster_name
):
    # Validate if we are able to install the flux configuration
    source_control_client = k8s_configuration_sourcecontrol_client(cmd.cli_ctx)
    configs = source_control_client.list(
        resource_group_name, cluster_rp, cluster_type, cluster_name
    )
    # configs is an iterable, no len() so we have to iterate to check for configs
    for _ in configs:
        raise DeploymentError(
            consts.SCC_EXISTS_ON_CLUSTER_ERROR, consts.SCC_EXISTS_ON_CLUSTER_HELP
        )


def _validate_extension_install(
    cmd, resource_group_name, cluster_rp, cluster_type, cluster_name, no_wait
):
    # Validate if the extension is installed, if not, install it
    extension_client = k8s_configuration_extension_client(cmd.cli_ctx)
    extensions = extension_client.list(
        resource_group_name, cluster_rp, cluster_type, cluster_name
    )
    flux_extension = None
    for extension in extensions:
        if extension.extension_type.lower() == consts.FLUX_EXTENSION_TYPE:
            flux_extension = extension
            break
    if not flux_extension:
        logger.warning(
            "'Microsoft.Flux' extension not found on the cluster, installing it now."
            " This may take a few minutes..."
        )

        extension = Extension(
            extension_type="microsoft.flux",
            auto_upgrade_minor_version=True,
            release_train=os.getenv(consts.FLUX_EXTENSION_RELEASETRAIN),
            version=os.getenv(consts.FLUX_EXTENSION_VERSION),
        )
        if not is_dogfood_cluster(cmd):
            extension = __add_identity(
                cmd,
                extension,
                resource_group_name,
                cluster_rp,
                cluster_type,
                cluster_name,
            )

        logger.info(
            "Starting extension creation on the cluster. This might take a few minutes..."
        )
        sdk_no_wait(
            no_wait,
            extension_client.begin_create,
            resource_group_name,
            cluster_rp,
            cluster_type,
            cluster_name,
            "flux",
            extension,
        ).result()
        # Only show that we have received a success when we have --no-wait
        if not no_wait:
            logger.warning(
                "'Microsoft.Flux' extension was successfully installed on the cluster"
            )
    elif flux_extension.provisioning_state == consts.CREATING:
        raise DeploymentError(
            consts.FLUX_EXTENSION_CREATING_ERROR, consts.FLUX_EXTENSION_CREATING_HELP
        )
    elif flux_extension.provisioning_state != consts.SUCCEEDED:
        raise DeploymentError(
            consts.FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_ERROR,
            consts.FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_HELP,
        )


def __add_identity(
    cmd, extension_instance, resource_group_name, cluster_rp, cluster_type, cluster_name
):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    if cluster_type.lower() == consts.MANAGED_CLUSTER_TYPE:
        return extension_instance

    cluster_rp, parent_api_version = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_rp)

    cluster_resource_id = (
        "/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}".format(
            subscription_id, resource_group_name, cluster_rp, cluster_type, cluster_name
        )
    )

    try:
        resource = resources.get_by_id(cluster_resource_id, parent_api_version)
        location = str(resource.location.lower())
    except HttpResponseError as ex:
        raise ex
    identity_type = "SystemAssigned"

    extension_instance.identity = Identity(type=identity_type)
    extension_instance.location = location
    return extension_instance


def source_kind_generator_factory(kind=consts.GIT, **kwargs):
    if kind == consts.GIT:
        return GitRepositoryGenerator(**kwargs)
    if kind == consts.BUCKET:
        return BucketGenerator(**kwargs)
    return AzureBlobGenerator(**kwargs)


def convert_to_cli_source_kind(rp_source_kind):
    if rp_source_kind == consts.GIT_REPOSITORY:
        return consts.GIT
    elif rp_source_kind == consts.BUCKET_CAPS:
        return consts.BUCKET
    return consts.AZBLOB


class SourceKindGenerator:
    def __init__(self, kind, required_params, valid_params):
        self.kind = kind
        self.valid_params = valid_params
        self.required_params = required_params

    def validate_required_params(self, **kwargs):
        copied_required = self.required_params.copy()
        for kwarg, value in kwargs.items():
            if value:
                copied_required.discard(kwarg)
        if len(copied_required) > 0:
            raise RequiredArgumentMissingError(
                consts.REQUIRED_VALUES_MISSING_ERROR.format(
                    ",".join(map(pretty_parameter, copied_required)), self.kind
                ),
                consts.REQUIRED_VALUES_MISSING_HELP,
            )

    def validate_params(self, **kwargs):
        bad_args = []
        for kwarg, value in kwargs.items():
            if value and kwarg not in self.valid_params:
                bad_args.append(kwarg)
        if len(bad_args) > 0:
            raise UnrecognizedArgumentError(
                consts.EXTRA_VALUES_PROVIDED_ERROR.format(
                    ",".join(map(pretty_parameter, bad_args)), self.kind
                ),
                consts.EXTRA_VALUES_PROVIDED_HELP.format(
                    self.kind, ",".join(map(pretty_parameter, self.valid_params))
                ),
            )


def pretty_parameter(parameter):
    parameter = parameter.replace("_", "-")
    return "'--" + parameter + "'"


# pylint: disable=too-many-instance-attributes
class GitRepositoryGenerator(SourceKindGenerator):
    def __init__(self, **kwargs):
        # Common Pre-Validation
        super().__init__(
            consts.GIT, consts.GIT_REPO_REQUIRED_PARAMS, consts.GIT_REPO_VALID_PARAMS
        )
        super().validate_params(**kwargs)

        # Pre-Validation
        validate_duration("--timeout", kwargs.get("timeout"))
        validate_duration("--sync-interval", kwargs.get("sync_interval"))

        self.kwargs = kwargs
        self.url = kwargs.get("url")
        self.timeout = kwargs.get("timeout")
        self.sync_interval = kwargs.get("sync_interval")
        self.local_auth_ref = kwargs.get("local_auth_ref")
        self.known_hosts = kwargs.get("known_hosts")
        self.known_hosts_file = kwargs.get("known_hosts_file")
        self.ssh_private_key = kwargs.get("ssh_private_key")
        self.ssh_private_key_file = kwargs.get("ssh_private_key_file")
        self.https_user = kwargs.get("https_user")
        self.https_key = kwargs.get("https_key")

        # Get the known hosts data and validate it
        self.knownhost_data = get_data_from_key_or_file(
            kwargs.get("known_hosts"),
            kwargs.get("known_hosts_file"),
            strip_newline=True,
        )
        if self.knownhost_data:
            validate_known_hosts(self.knownhost_data)

        self.https_ca_data = get_data_from_key_or_file(
            kwargs.get("https_ca_cert"),
            kwargs.get("https_ca_cert_file"),
            strip_newline=True,
        )
        self.repository_ref = None
        if any(
            [
                kwargs.get("branch"),
                kwargs.get("tag"),
                kwargs.get("semver"),
                kwargs.get("commit"),
            ]
        ):
            self.repository_ref = RepositoryRefDefinition(
                branch=kwargs.get("branch"),
                tag=kwargs.get("tag"),
                semver=kwargs.get("semver"),
                commit=kwargs.get("commit"),
            )

    def validate(self):
        super().validate_required_params(**self.kwargs)
        validate_git_url(self.url)
        validate_url_with_params(
            self.url,
            self.ssh_private_key,
            self.ssh_private_key_file,
            self.known_hosts,
            self.known_hosts_file,
            self.https_user,
            self.https_key,
        )
        validate_repository_ref(self.repository_ref)

    def generate_update_func(self):
        """
        generate_update_func(self) generates a function to add a GitRepository
        object to the flux configuration for the PUT case
        """
        self.validate()

        def updater(config):
            config.git_repository = GitRepositoryDefinition(
                url=self.url,
                timeout_in_seconds=parse_duration(self.timeout),
                sync_interval_in_seconds=parse_duration(self.sync_interval),
                repository_ref=self.repository_ref,
                ssh_known_hosts=self.knownhost_data,
                https_user=self.https_user,
                local_auth_ref=self.local_auth_ref,
                https_ca_cert=self.https_ca_data,
            )
            config.source_kind = SourceKindType.GIT_REPOSITORY
            return config

        return updater

    def generate_patch_update_func(self, swapped_kind):
        """
        generate_patch_update_func(self) generates a function update the GitRepository
        object to the flux configuration for the PATCH case.
        If the source kind has been changed, we also set the Bucket to null
        """

        def git_repository_updater(config):
            if any(kwarg is not None for kwarg in self.kwargs.values()):
                config.git_repository = GitRepositoryPatchDefinition(
                    url=self.url,
                    timeout_in_seconds=parse_duration(self.timeout),
                    sync_interval_in_seconds=parse_duration(self.sync_interval),
                    repository_ref=self.repository_ref,
                    ssh_known_hosts=self.knownhost_data,
                    https_user=self.https_user,
                    local_auth_ref=self.local_auth_ref,
                    https_ca_cert=self.https_ca_data,
                )
            if swapped_kind:
                self.validate()
                config.source_kind = SourceKindType.GIT_REPOSITORY

                config.bucket = BucketPatchDefinition()
                config.azure_blob = AzureBlobPatchDefinition()
            return config

        return git_repository_updater


class BucketGenerator(SourceKindGenerator):
    def __init__(self, **kwargs):
        # Common Pre-Validation
        super().__init__(
            consts.BUCKET, consts.BUCKET_REQUIRED_PARAMS, consts.BUCKET_VALID_PARAMS
        )
        super().validate_params(**kwargs)

        # Pre-Validations
        validate_duration("--timeout", kwargs.get("timeout"))
        validate_duration("--sync-interval", kwargs.get("sync_interval"))

        self.kwargs = kwargs
        self.url = kwargs.get("url")
        self.bucket_name = kwargs.get("bucket_name")
        self.timeout = kwargs.get("timeout")
        self.sync_interval = kwargs.get("sync_interval")
        self.bucket_access_key = kwargs.get("bucket_access_key")
        self.bucket_secret_key = kwargs.get("bucket_secret_key")
        self.local_auth_ref = kwargs.get("local_auth_ref")
        self.bucket_insecure = kwargs.get("bucket_insecure")

    def validate(self):
        super().validate_required_params(**self.kwargs)
        validate_bucket_url(self.url)
        if not (
            (self.bucket_access_key and self.bucket_secret_key) or self.local_auth_ref
        ):
            raise RequiredArgumentMissingError(
                consts.REQUIRED_BUCKET_VALUES_MISSING_ERROR,
                consts.REQUIRED_BUCKET_VALUES_MISSING_HELP,
            )

    def generate_update_func(self):
        """
        generate_update_func(self) generates a function to add a Bucket
        object to the flux configuration for the PUT case
        """
        self.validate()

        def bucket_updater(config):
            config.bucket = BucketDefinition(
                url=self.url,
                bucket_name=self.bucket_name,
                timeout_in_seconds=parse_duration(self.timeout),
                sync_interval_in_seconds=parse_duration(self.sync_interval),
                access_key=self.bucket_access_key,
                local_auth_ref=self.local_auth_ref,
                insecure=self.bucket_insecure,
            )
            config.source_kind = SourceKindType.BUCKET
            return config

        return bucket_updater

    def generate_patch_update_func(self, swapped_kind):
        """
        generate_patch_update_func(self) generates a function update the Bucket
        object to the flux configuration for the PATCH case.
        If the source kind has been changed, we also set the GitRepository to null
        """

        def bucket_patch_updater(config):
            if any(kwarg is not None for kwarg in self.kwargs.values()):
                config.bucket = BucketPatchDefinition(
                    url=self.url,
                    bucket_name=self.bucket_name,
                    timeout_in_seconds=parse_duration(self.timeout),
                    sync_interval_in_seconds=parse_duration(self.sync_interval),
                    access_key=self.bucket_access_key,
                    local_auth_ref=self.local_auth_ref,
                    insecure=self.bucket_insecure,
                )
                if swapped_kind:
                    self.validate()
                    config.source_kind = SourceKindType.BUCKET
                    config.git_repository = GitRepositoryPatchDefinition()
                    config.azure_blob = AzureBlobPatchDefinition()
            return config

        return bucket_patch_updater


class AzureBlobGenerator(SourceKindGenerator):
    def __init__(self, **kwargs):
        # Common Pre-Validation
        super().__init__(
            consts.AZBLOB, consts.AZUREBLOB_REQUIRED_PARAMS, consts.AZUREBLOB_VALID_PARAMS
        )
        super().validate_params(**kwargs)

        # Pre-Validations
        validate_duration("--timeout", kwargs.get("timeout"))
        validate_duration("--sync-interval", kwargs.get("sync_interval"))

        self.kwargs = kwargs
        self.url = kwargs.get("url")
        self.container_name = kwargs.get("container_name")
        self.timeout = kwargs.get("timeout")
        self.sync_interval = kwargs.get("sync_interval")
        self.account_key = kwargs.get("account_key")
        self.sas_token = kwargs.get("sas_token")
        self.local_auth_ref = kwargs.get("local_auth_ref")

        self.service_principal = None
        if any(
            [
                kwargs.get("sp_client_id"),
                kwargs.get("sp_tenant_id"),
                kwargs.get("sp_client_secret"),
                kwargs.get("sp_client_cert"),
                kwargs.get("sp_client_cert_password"),
                kwargs.get("sp_client_cert_send_chain")
            ]
        ):
            self.service_principal = ServicePrincipalDefinition(
                client_id=kwargs.get("sp_client_id"),
                tenant_id=kwargs.get("sp_tenant_id"),
                client_secret=kwargs.get("sp_client_secret"),
                client_certificate=kwargs.get("sp_client_cert"),
                client_certificate_password=kwargs.get("sp_client_cert_password"),
                client_certificate_send_chain=kwargs.get("sp_client_cert_send_chain")
            )

        self.managed_identity = None
        if any(
            [
                kwargs.get("mi_client_id"),
            ]
        ):
            self.managed_identity = ManagedIdentityDefinition(
                client_id=kwargs.get("mi_client_id"),
            )

    def validate(self):
        super().validate_required_params(**self.kwargs)
        validate_bucket_url(self.url)
        validate_azure_blob_auth(self)

    def generate_update_func(self):
        """
        generate_update_func(self) generates a function to add a Azure Blob
        object to the flux configuration for the PUT case
        """
        self.validate()

        def azure_blob_updater(config):
            config.azure_blob = AzureBlobDefinition(
                url=self.url,
                container_name=self.container_name,
                timeout_in_seconds=parse_duration(self.timeout),
                sync_interval_in_seconds=parse_duration(self.sync_interval),
                account_key=self.account_key,
                sas_token=self.sas_token,
                service_principal=self.service_principal,
                managed_identity=self.managed_identity,
                local_auth_ref=self.local_auth_ref,
            )
            config.source_kind = SourceKindType.AZURE_BLOB
            return config

        return azure_blob_updater

    def generate_patch_update_func(self, swapped_kind):
        """
        generate_patch_update_func(self) generates a function update the AzureBlob
        object to the flux configuration for the PATCH case.
        If the source kind has been changed, we also set the GitRepository and Bucket to null
        """

        def azure_blob_patch_updater(config):
            if any(kwarg is not None for kwarg in self.kwargs.values()):
                config.azure_blob = AzureBlobPatchDefinition(
                    url=self.url,
                    container_name=self.container_name,
                    timeout_in_seconds=parse_duration(self.timeout),
                    sync_interval_in_seconds=parse_duration(self.sync_interval),
                    account_key=self.account_key,
                    sas_token=self.sas_token,
                    local_auth_ref=self.local_auth_ref,
                    service_principal=self.service_principal,
                    managed_identity=self.managed_identity,
                )
                if swapped_kind:
                    self.validate()
                    config.source_kind = SourceKindType.AZURE_BLOB
                    config.bucket = BucketPatchDefinition()
                    config.git_repository = GitRepositoryPatchDefinition()
            return config

        return azure_blob_patch_updater


def get_protected_settings(
    ssh_private_key, ssh_private_key_file, https_key, bucket_secret_key
):
    protected_settings = {}
    ssh_private_key_data = get_data_from_key_or_file(
        ssh_private_key, ssh_private_key_file
    )

    # Add gitops private key data to protected settings if exists
    if ssh_private_key_data:
        protected_settings[consts.SSH_PRIVATE_KEY_KEY] = ssh_private_key_data

    if https_key:
        protected_settings[consts.HTTPS_KEY_KEY] = to_base64(https_key)

    if bucket_secret_key:
        protected_settings[consts.BUCKET_SECRET_KEY_KEY] = to_base64(bucket_secret_key)

    # Return the protected settings dict if there are any values there
    return protected_settings if len(protected_settings) > 0 else None
