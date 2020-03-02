# pylint: disable=import-error,relative-import,unused-import
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from six.moves.urllib.parse import quote
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import parse_resource_id
from dateutil.parser import parse

from azure.cli.core.commands.client_factory import get_subscription_id
from azext_maintenance.vendored_sdks.models import (
    ApplyUpdate,
    ConfigurationAssignment,
    MaintenanceConfiguration,
    Update,
    UpdateStatus,
    MaintenanceScope,
    ImpactType)

logger = get_logger(__name__)

MAINTENANCE_NAMESPACE = "Microsoft.Maintenance"
RESOURCES_NAMESPACE = "Microsoft.Resources"
SUBSCRIPTIONS = "subscriptions"
RESOURCE_GROUPS = "resourcegroups"
EVENTGRID_DOMAINS = "domains"
EVENTGRID_TOPICS = "topics"
WEBHOOK_DESTINATION = "webhook"
EVENTHUB_DESTINATION = "eventhub"
STORAGEQUEUE_DESTINATION = "storagequeue"
HYBRIDCONNECTION_DESTINATION = "hybridconnection"
EVENTGRID_SCHEMA = "EventGridSchema"
CLOUDEVENTV01_SCHEMA = "CloudEventV01Schema"
CUSTOM_EVENT_SCHEMA = "CustomEventSchema"
CUSTOM_INPUT_SCHEMA = "CustomInputSchema"
GLOBAL = "global"

# Deprecated event delivery schema value (starting 2018-09-15-preview)
INPUT_EVENT_SCHEMA = "InputEventSchema"

# Constants for the target field names of the mapping
CONFIGURATION = "configuration"
SUBJECT = "subject"
ID = "id"
DEFAULT_SCOPE = "All"


def cli_configuration_create(
        client,
        resource_group_name,
        resource_name,
        location,
        tags=None,
        maintenanceScope=DEFAULT_SCOPE):

    configuration = MaintenanceConfiguration(
        location=location,
        tags=tags,
        namespace=MAINTENANCE_NAMESPACE,
        maintenance_scope=maintenanceScope)

    return client.create_or_update(
        resource_group_name=resource_group_name,
        resource_name=resource_name,
        configuration=configuration)


def cli_assignment_create(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        configuration_assignment_name,
        location,
        maintenance_configuration_id,
        resource_parent_type=None,
        resource_parent_name=None,
        resource_id=None):

    configuration_assignment = ConfigurationAssignment(
        location=location,
        maintenance_configuration_id=maintenance_configuration_id,
        resource_id=resource_id)

    if not resource_parent_type:
        return client.create_or_update(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name,
            configuration_assignment_name=configuration_assignment_name,
            configuration_assignment=configuration_assignment)

    return client.create_or_update_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name,
        configuration_assignment_name=configuration_assignment_name,
        configuration_assignment=configuration_assignment)


def cli_assignment_delete(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        configuration_assignment_name,
        resource_parent_type=None,
        resource_parent_name=None):

    if not resource_parent_type:
        return client.delete(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name,
            configuration_assignment_name=configuration_assignment_name)

    return client.delete_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name,
        configuration_assignment_name=configuration_assignment_name)


def cli_assignment_list(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        resource_parent_type=None,
        resource_parent_name=None):

    if not resource_parent_type:
        return client.list(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name)

    return client.list_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name)


def cli_applyupdate_create(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        resource_parent_type=None,
        resource_parent_name=None):

    if not resource_parent_type:
        return client.create_or_update(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name)

    return client.create_or_update_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name)


def cli_applyupdate_get(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        apply_update_name,
        resource_parent_type=None,
        resource_parent_name=None):

    if not resource_parent_type:
        return client.get(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name,
            apply_update_name=apply_update_name)

    return client.get_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name,
        apply_update_name=apply_update_name)


def cli_update_list(
        client,
        resource_group_name,
        provider_name,
        resource_type,
        resource_name,
        resource_parent_type=None,
        resource_parent_name=None):

    if not resource_parent_type:
        return client.list(
            resource_group_name=resource_group_name,
            provider_name=provider_name,
            resource_type=resource_type,
            resource_name=resource_name)

    return client.list_parent(
        resource_group_name=resource_group_name,
        provider_name=provider_name,
        resource_parent_type=resource_parent_type,
        resource_parent_name=resource_parent_name,
        resource_type=resource_type,
        resource_name=resource_name)
