# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait
from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger
from knack.util import CLIError

from azext_aimanager._client_factory import CUSTOM_MGMT_AIMANAGER
from azext_aimanager._helpers import (
    get_aks_custom_headers,
    parse_key_value_list,
    print_or_merge_credentials,
)

logger = get_logger(__name__)


def _get_model(cmd, name, operation_group):
    return cmd.get_models(
        name,
        resource_type=CUSTOM_MGMT_AIMANAGER,
        operation_group=operation_group,
    )


# region AI Manager

def _construct_aimanager(cmd, location, tags, delete_policy, identity=None):
    ai_manager_properties_model = _get_model(cmd, "AIManagerProperties", "ai_managers")
    ai_manager_model = _get_model(cmd, "AIManager", "ai_managers")

    ai_manager = ai_manager_model()
    ai_manager.location = location
    ai_manager.tags = tags
    ai_manager.properties = ai_manager_properties_model(delete_policy=delete_policy)
    if identity is not None:
        ai_manager.identity = identity
    return ai_manager


# pylint: disable=unused-argument
def create_aimanager(cmd,
                     client,
                     resource_group_name,
                     ai_manager_name,
                     location=None,
                     tags=None,
                     delete_policy=None,
                     aks_custom_headers=None,
                     no_wait=False):
    existing = None
    try:
        existing = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        pass
    if existing:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' already exists. "
            "Please use 'az aimanager update' to update it.")

    headers = get_aks_custom_headers(aks_custom_headers)
    ai_manager = _construct_aimanager(cmd, location, tags, delete_policy)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )


# pylint: disable=unused-argument
def update_aimanager(cmd,
                     client,
                     resource_group_name,
                     ai_manager_name,
                     tags=None,
                     delete_policy=None,
                     aks_custom_headers=None,
                     no_wait=False):
    try:
        existing = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers.")

    if tags is None:
        tags = existing.tags
    existing_properties = existing.properties
    if delete_policy is None and existing_properties is not None:
        delete_policy = existing_properties.delete_policy

    headers = get_aks_custom_headers(aks_custom_headers)
    # Preserve the existing identity so a tags/delete-policy update does not drop a
    # managed identity configured through ARM or another client on the create-or-replace PUT.
    ai_manager = _construct_aimanager(
        cmd, existing.location, tags, delete_policy, identity=existing.identity)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )


def show_aimanager(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name)


def list_aimanager(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def delete_aimanager(cmd, client, resource_group_name, ai_manager_name, no_wait=False):  # pylint: disable=unused-argument
    try:
        client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers.")

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name)


def _write_kubeconfig(credential_results, path, overwrite_existing, context_name):
    # Check if KUBECONFIG environmental variable is set
    # If path is different than default then that means -f/--file is passed
    # in which case we ignore the KUBECONFIG variable
    # KUBECONFIG can be colon separated. If we find that condition, use the first entry
    if "KUBECONFIG" in os.environ and path == os.path.join(os.path.expanduser('~'), '.kube', 'config'):
        kubeconfig_path = os.environ["KUBECONFIG"].split(os.pathsep)[0]
        if kubeconfig_path:
            logger.info("The default path '%s' is replaced by '%s' defined in KUBECONFIG.", path, kubeconfig_path)
            path = kubeconfig_path
        else:
            logger.warning("Invalid path '%s' defined in KUBECONFIG.", kubeconfig_path)

    if not credential_results:
        raise CLIError("No Kubernetes credentials found.")
    try:
        kubeconfig = credential_results.kubeconfigs[0].value.decode(encoding='UTF-8')
        print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name)
    except (IndexError, ValueError) as exc:
        raise CLIError(
            "Failed to extract the kubeconfig from the service response. "
            "The returned credentials did not contain a valid kubeconfig.") from exc


# pylint: disable=unused-argument
def aimanager_get_credentials(cmd,
                              client,
                              resource_group_name,
                              ai_manager_name,
                              path=os.path.join(os.path.expanduser("~"), ".kube", "config"),
                              overwrite_existing=False,
                              context_name=None,
                              aks_custom_headers=None):
    headers = get_aks_custom_headers(aks_custom_headers)
    credential_results = client.list_credential(
        resource_group_name, ai_manager_name, headers=headers)
    _write_kubeconfig(credential_results, path, overwrite_existing, context_name)

# endregion


# region AI Manager namespace

def _construct_namespace(cmd, labels, annotations):
    namespace_properties_model = _get_model(cmd, "AIManagerNamespaceProperties", "ai_manager_namespaces")
    namespace_model = _get_model(cmd, "AIManagerNamespace", "ai_manager_namespaces")

    namespace_config = namespace_model()
    namespace_config.properties = namespace_properties_model(labels=labels, annotations=annotations)
    return namespace_config


# pylint: disable=unused-argument
def add_aimanager_namespace(cmd,
                            client,
                            resource_group_name,
                            ai_manager_name,
                            namespace_name,
                            labels=None,
                            annotations=None,
                            aks_custom_headers=None,
                            no_wait=False):
    existing = None
    try:
        existing = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        pass
    if existing:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' already exists. "
            "Please use 'az aimanager namespace update' to update it.")

    headers = get_aks_custom_headers(aks_custom_headers)
    namespace_config = _construct_namespace(
        cmd, parse_key_value_list(labels), parse_key_value_list(annotations))

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )


# pylint: disable=unused-argument
def update_aimanager_namespace(cmd,
                               client,
                               resource_group_name,
                               ai_manager_name,
                               namespace_name,
                               labels=None,
                               annotations=None,
                               aks_custom_headers=None,
                               no_wait=False):
    try:
        existing = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces.")

    existing_properties = existing.properties
    if labels is None:
        new_labels = existing_properties.labels if existing_properties is not None else None
    else:
        new_labels = parse_key_value_list(labels)
    if annotations is None:
        new_annotations = existing_properties.annotations if existing_properties is not None else None
    else:
        new_annotations = parse_key_value_list(annotations)

    headers = get_aks_custom_headers(aks_custom_headers)
    namespace_config = _construct_namespace(cmd, new_labels, new_annotations)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )


def show_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name, namespace_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name, namespace_name)


def list_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.list_by_ai_manager(resource_group_name, ai_manager_name)


def delete_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name, namespace_name, no_wait=False):  # pylint: disable=unused-argument
    try:
        client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces.")

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name, namespace_name)


# pylint: disable=unused-argument
def aimanager_namespace_get_credentials(cmd,
                                        client,
                                        resource_group_name,
                                        ai_manager_name,
                                        namespace_name,
                                        path=os.path.join(os.path.expanduser("~"), ".kube", "config"),
                                        overwrite_existing=False,
                                        context_name=None,
                                        aks_custom_headers=None):
    headers = get_aks_custom_headers(aks_custom_headers)
    credential_results = client.list_credential(
        resource_group_name, ai_manager_name, namespace_name, headers=headers)
    _write_kubeconfig(credential_results, path, overwrite_existing, context_name)

# endregion


# region Model deployment

def _construct_scaling_profile(cmd, replicas=None, min_replicas=None, max_replicas=None,
                               existing_scale=None, required=False):
    scaling_requested = any(value is not None for value in (replicas, min_replicas, max_replicas))
    if not scaling_requested:
        if existing_scale is not None:
            return existing_scale
        if required:
            raise InvalidArgumentValueError(
                "Specify either --replicas or --min-replicas for the model deployment.")
        return None

    if replicas is not None:
        if min_replicas is not None or max_replicas is not None:
            raise InvalidArgumentValueError(
                "--replicas cannot be combined with --min-replicas or --max-replicas.")
        if replicas < 0:
            raise InvalidArgumentValueError("--replicas must be zero or greater.")
        manual_model = _get_model(cmd, "ManualScalingProfile", "model_deployments")
        scaling_model = _get_model(cmd, "ScalingProfile", "model_deployments")
        return scaling_model(manual=manual_model(replicas=replicas))

    existing_autoscale = getattr(existing_scale, "autoscale", None)
    if min_replicas is None:
        if existing_autoscale is None:
            raise InvalidArgumentValueError(
                "--min-replicas is required when enabling autoscale.")
        min_replicas = existing_autoscale.min_replicas
    if max_replicas is None and existing_autoscale is not None:
        max_replicas = existing_autoscale.max_replicas
    if min_replicas < 1:
        raise InvalidArgumentValueError("--min-replicas must be at least 1.")
    if max_replicas is not None and max_replicas < min_replicas:
        raise InvalidArgumentValueError(
            "--max-replicas must be greater than or equal to --min-replicas.")

    autoscale_model = _get_model(cmd, "AutoscaleProfile", "model_deployments")
    scaling_model = _get_model(cmd, "ScalingProfile", "model_deployments")
    return scaling_model(
        autoscale=autoscale_model(min_replicas=min_replicas, max_replicas=max_replicas))


def _construct_modeldeployment(cmd, model_resource_id, vm_size, model_source_resource_id=None,
                               performance_mode=None, scale=None, overrides=None):
    deployment_model = _get_model(cmd, "ModelDeployment", "model_deployments")
    properties_model = _get_model(cmd, "ModelDeploymentProperties", "model_deployments")
    overrides_config = None
    if overrides is not None:
        overrides_model = _get_model(cmd, "ModelDeploymentOverrides", "model_deployments")
        overrides_config = overrides_model(values_property=overrides)

    return deployment_model(properties=properties_model(
        model_resource_id=model_resource_id,
        model_source_resource_id=model_source_resource_id,
        performance_mode=performance_mode,
        vm_size=vm_size,
        scale=scale,
        overrides=overrides_config,
    ))


# pylint: disable=unused-argument
def add_modeldeployment(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                        model_deployment_name, model_resource_id, vm_size,
                        model_source_resource_id=None, performance_mode=None, replicas=None,
                        min_replicas=None, max_replicas=None, overrides=None,
                        aks_custom_headers=None, no_wait=False):
    try:
        client.get(resource_group_name, ai_manager_name, namespace_name, model_deployment_name)
    except ResourceNotFoundError:
        pass
    else:
        raise ClientRequestError(
            f"Model deployment '{model_deployment_name}' already exists. "
            "Please use 'az aimanager namespace modeldeployment update' to update it.")

    scale = _construct_scaling_profile(
        cmd, replicas, min_replicas, max_replicas, required=True)
    deployment = _construct_modeldeployment(
        cmd, model_resource_id, vm_size, model_source_resource_id, performance_mode,
        scale, parse_key_value_list(overrides) if overrides is not None else None)
    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(
        no_wait, client.begin_create_or_update, resource_group_name, ai_manager_name,
        namespace_name, model_deployment_name, deployment, headers=headers)


# pylint: disable=unused-argument
def update_modeldeployment(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                           model_deployment_name, performance_mode=None, replicas=None,
                           min_replicas=None, max_replicas=None, overrides=None,
                           aks_custom_headers=None, no_wait=False):
    try:
        existing = client.get(
            resource_group_name, ai_manager_name, namespace_name, model_deployment_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Model deployment '{model_deployment_name}' doesn't exist. "
            "Please use 'az aimanager namespace modeldeployment list' to list deployments.")

    properties = existing.properties
    scale = _construct_scaling_profile(
        cmd, replicas, min_replicas, max_replicas, existing_scale=properties.scale)
    if performance_mode is None:
        performance_mode = properties.performance_mode
    if overrides is None:
        override_values = (
            properties.overrides.values_property if properties.overrides is not None else None)
    else:
        override_values = parse_key_value_list(overrides)

    deployment = _construct_modeldeployment(
        cmd, properties.model_resource_id, properties.vm_size,
        properties.model_source_resource_id, performance_mode, scale, override_values)
    headers = get_aks_custom_headers(aks_custom_headers)
    etag = existing.e_tag
    match_condition = MatchConditions.IfNotModified if etag is not None else None
    return sdk_no_wait(
        no_wait, client.begin_create_or_update, resource_group_name, ai_manager_name,
        namespace_name, model_deployment_name, deployment, headers=headers,
        etag=etag, match_condition=match_condition)


def show_modeldeployment(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                         model_deployment_name):  # pylint: disable=unused-argument
    return client.get(
        resource_group_name, ai_manager_name, namespace_name, model_deployment_name)


def list_modeldeployment(cmd, client, resource_group_name, ai_manager_name,
                         namespace_name):  # pylint: disable=unused-argument
    return client.list_by_ai_manager_namespace(
        resource_group_name, ai_manager_name, namespace_name)


def delete_modeldeployment(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                           model_deployment_name, no_wait=False):  # pylint: disable=unused-argument
    try:
        client.get(resource_group_name, ai_manager_name, namespace_name, model_deployment_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Model deployment '{model_deployment_name}' doesn't exist. "
            "Please use 'az aimanager namespace modeldeployment list' to list deployments.")
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, ai_manager_name,
        namespace_name, model_deployment_name)

# endregion
