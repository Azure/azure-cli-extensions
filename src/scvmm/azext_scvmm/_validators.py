# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError,
)
from msrestazure.tools import is_valid_resource_id
from azext_scvmm.scvmm_constants import (
    CLOUD_RESOURCE_TYPE,
    CUSTOM_LOCATION_RESOURCE_TYPE,
    EXTENDED_LOCATION_NAMESPACE,
    INVENTORY_ITEM_TYPE,
    SCVMM_NAMESPACE,
    VMMSERVER_RESOURCE_TYPE,
    VMTEMPLATE_RESOURCE_TYPE,
)

from .scvmm_utils import get_resource_id


def validate_custom_location_name_or_id(cmd, namespace):
    if namespace.custom_location is None:
        raise RequiredArgumentMissingError(
            '"custom_location" name or id is required for resource PUT operation.'
        )
    namespace.custom_location = get_resource_id(
        cmd,
        namespace.resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        namespace.custom_location,
    )


def validate_vmmserver_name_or_id(cmd, namespace):
    if namespace.vmmserver:
        namespace.vmmserver = get_resource_id(
            cmd,
            namespace.resource_group_name,
            SCVMM_NAMESPACE,
            VMMSERVER_RESOURCE_TYPE,
            namespace.vmmserver,
        )


def validate_inventory_item_name_or_id(namespace):
    if namespace.inventory_item and not is_valid_resource_id(namespace.inventory_item):
        if not namespace.vmmserver:
            raise RequiredArgumentMissingError(
                '"vmmserver" name or id is required when inventory item name is provided.'
            )
        namespace.inventory_item = "/".join(
            [
                namespace.vmmserver,
                INVENTORY_ITEM_TYPE,
                namespace.inventory_item,
            ]
        )


def validate_param_combos(cmd, namespace):
    if (
        len(
            [
                key
                for key in ['uuid', 'inventory_item']
                if getattr(namespace, key) is not None
            ]
        )
        != 1  # noqa: W503
    ):
        raise MutuallyExclusiveArgumentError(
            'Exactly one of "uuid" and "inventory_item" must be provided.'
        )
    if namespace.uuid and not namespace.vmmserver:
        raise RequiredArgumentMissingError(
            '"vmmserver" name or id is required when "uuid" is provided.'
        )
    validate_custom_location_name_or_id(cmd, namespace)
    validate_vmmserver_name_or_id(cmd, namespace)
    validate_inventory_item_name_or_id(namespace)


def validate_param_combos_for_vm(cmd, namespace):
    is_existing = namespace.inventory_item is not None
    is_new = all(getattr(namespace, k) is not None for k in ['vm_template', 'cloud'])
    if not all([any([is_existing, is_new]), (not all([is_existing, is_new]))]):
        raise MutuallyExclusiveArgumentError(
            'Either "inventory_id" has to be specified or both "vm_template" and "cloud" have to be specified.'
        )
    validate_custom_location_name_or_id(cmd, namespace)
    validate_vmmserver_name_or_id(cmd, namespace)
    validate_inventory_item_name_or_id(namespace)
    if is_new:
        namespace.vm_template = get_resource_id(
            cmd,
            namespace.resource_group_name,
            SCVMM_NAMESPACE,
            VMTEMPLATE_RESOURCE_TYPE,
            namespace.vm_template,
        )
        namespace.cloud = get_resource_id(
            cmd,
            namespace.resource_group_name,
            SCVMM_NAMESPACE,
            CLOUD_RESOURCE_TYPE,
            namespace.cloud,
        )
    if namespace.availability_sets is not None and len(namespace.availability_sets) > 1:
        raise InvalidArgumentValueError(
            'Only one availability set can be specified while creating the VM'
        )


def validate_param_combos_for_avset(cmd, namespace):
    validate_custom_location_name_or_id(cmd, namespace)
    validate_vmmserver_name_or_id(cmd, namespace)
