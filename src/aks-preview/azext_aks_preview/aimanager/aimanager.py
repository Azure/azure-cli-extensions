# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Model builders and SDK invocations for the ``az aimanager`` command group.

Mirrors the ``managednamespace.py`` structure: command handlers in ``custom.py`` gather the
raw parameters and delegate here, where the models are resolved through
``cmd.get_models`` (the vendored SDK registered as ``CUSTOM_MGMT_AIMANAGER``) and the
operation-group methods are called through ``sdk_no_wait``.
"""

from azure.cli.core.util import sdk_no_wait

from ._client_factory import CUSTOM_MGMT_AIMANAGER


def parse_key_value_list(pairs):
    result = {}
    if pairs is None:
        return result
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid format '{pair}'. Expected format key=value.")
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _get_model(cmd, name, operation_group):
    return cmd.get_models(
        name,
        resource_type=CUSTOM_MGMT_AIMANAGER,
        operation_group=operation_group,
    )


# region AI Manager

def constructAIManager(cmd, raw_parameters):
    location = raw_parameters.get("location")
    tags = raw_parameters.get("tags")
    delete_policy = raw_parameters.get("delete_policy")

    AIManagerProperties = _get_model(cmd, "AIManagerProperties", "ai_managers")
    AIManager = _get_model(cmd, "AIManager", "ai_managers")

    ai_manager = AIManager()
    ai_manager.location = location
    ai_manager.tags = tags
    ai_manager.properties = AIManagerProperties(delete_policy=delete_policy)
    return ai_manager


def updateAIManager(cmd, raw_parameters, existedAIManager):
    tags = raw_parameters.get("tags")
    delete_policy = raw_parameters.get("delete_policy")

    if tags is None:
        tags = existedAIManager.tags

    existing_properties = existedAIManager.properties
    if delete_policy is None and existing_properties is not None:
        delete_policy = existing_properties.delete_policy

    AIManagerProperties = _get_model(cmd, "AIManagerProperties", "ai_managers")
    AIManager = _get_model(cmd, "AIManager", "ai_managers")

    ai_manager = AIManager()
    ai_manager.location = existedAIManager.location
    ai_manager.tags = tags
    ai_manager.properties = AIManagerProperties(delete_policy=delete_policy)
    return ai_manager


def aks_aimanager_create(cmd, client, raw_parameters, headers, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    ai_manager_name = raw_parameters.get("ai_manager_name")

    ai_manager = constructAIManager(cmd, raw_parameters)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )


def aks_aimanager_update(cmd, client, raw_parameters, headers, existedAIManager, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    ai_manager_name = raw_parameters.get("ai_manager_name")

    ai_manager = updateAIManager(cmd, raw_parameters, existedAIManager)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )

# endregion


# region AI Manager namespace

def constructNamespace(cmd, raw_parameters):
    labels = parse_key_value_list(raw_parameters.get("labels"))
    annotations = parse_key_value_list(raw_parameters.get("annotations"))

    NamespaceProperties = _get_model(cmd, "AIManagerNamespaceProperties", "ai_manager_namespaces")
    Namespace = _get_model(cmd, "AIManagerNamespace", "ai_manager_namespaces")

    namespace_config = Namespace()
    namespace_config.properties = NamespaceProperties(labels=labels, annotations=annotations)
    return namespace_config


def updateNamespace(cmd, raw_parameters, existedNamespace):
    labels_raw = raw_parameters.get("labels")
    annotations_raw = raw_parameters.get("annotations")

    existing_properties = existedNamespace.properties

    if labels_raw is None:
        labels = existing_properties.labels if existing_properties is not None else None
    else:
        labels = parse_key_value_list(labels_raw)

    if annotations_raw is None:
        annotations = existing_properties.annotations if existing_properties is not None else None
    else:
        annotations = parse_key_value_list(annotations_raw)

    NamespaceProperties = _get_model(cmd, "AIManagerNamespaceProperties", "ai_manager_namespaces")
    Namespace = _get_model(cmd, "AIManagerNamespace", "ai_manager_namespaces")

    namespace_config = Namespace()
    namespace_config.properties = NamespaceProperties(labels=labels, annotations=annotations)
    return namespace_config


def aks_aimanager_namespace_add(cmd, client, raw_parameters, headers, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    ai_manager_name = raw_parameters.get("ai_manager_name")
    namespace_name = raw_parameters.get("namespace_name")

    namespace_config = constructNamespace(cmd, raw_parameters)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )


def aks_aimanager_namespace_update(cmd, client, raw_parameters, headers, existedNamespace, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    ai_manager_name = raw_parameters.get("ai_manager_name")
    namespace_name = raw_parameters.get("namespace_name")

    namespace_config = updateNamespace(cmd, raw_parameters, existedNamespace)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )

# endregion
