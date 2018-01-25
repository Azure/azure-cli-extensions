# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azext_eventhub._utils import accessrights_converter

from azext_eventhub.eventhub.models import (EHNamespace, Sku, Eventhub, CaptureDescription, Destination)


# Namespace Region
def cli_namespace_create(client, resource_group_name, namespace_name, location, tags=None, sku='Standard', skutier=None, capacity=None, is_auto_inflate_enabled=None, maximum_throughput_units=None):
    return client.create_or_update(resource_group_name, namespace_name, EHNamespace(location, tags,
                                                                                    Sku(sku,
                                                                                        skutier,
                                                                                        capacity), is_auto_inflate_enabled, maximum_throughput_units))


def cli_namespace_list(client, resource_group_name=None):
    cmd_result = None

    if resource_group_name:
        cmd_result = client.list_by_resource_group(resource_group_name)

    if not resource_group_name:
        cmd_result = client.list()

    return cmd_result


# Namespace Authorization rule:
def cli_namespaceautho_create(client, resource_group_name, namespace_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, name,
                                                      accessrights_converter(accessrights))


# Eventhub Region
def cli_eheventhub_create(client, resource_group_name, namespace_name, name, message_retention_in_days=None, partition_count=None, status=None,
                          enabled=None, encoding=None, capture_interval_seconds=None, capture_size_limit_bytes=None, destination_name=None, storage_account_resource_id=None, blob_container=None, archive_name_format=None):
    eventhubparameter1 = Eventhub()
    if message_retention_in_days:
        eventhubparameter1.message_retention_in_days = message_retention_in_days

    if partition_count:
        eventhubparameter1.partition_count = partition_count

    if status:
        eventhubparameter1.status = status

    if enabled and enabled is True:
        eventhubparameter1.capture_description = CaptureDescription(
            enabled=enabled,
            encoding=encoding,
            interval_in_seconds=capture_interval_seconds,
            size_limit_in_bytes=capture_size_limit_bytes,
            destination=Destination(
                name=destination_name,
                storage_account_resource_id=storage_account_resource_id,
                blob_container=blob_container,
                archive_name_format=archive_name_format)
        )
    return client.create_or_update(resource_group_name, namespace_name, name, eventhubparameter1)


def cli_eheventhubautho_create(client, resource_group_name, namespace_name, event_hub_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, event_hub_name, name,
                                                      accessrights_converter(accessrights))


def cli_ehconsumergroup_create(client, resource_group_name, namespace_name, event_hub_name, name, user_metadata):
    return client.create_or_update(resource_group_name, namespace_name, event_hub_name, name, user_metadata)


# pylint: disable=inconsistent-return-statements
def empty_on_404(ex):
    from azext_eventhub.eventhub.models import ErrorResponseException
    if isinstance(ex, ErrorResponseException) and ex.response.status_code == 404:
        return None
    raise ex
