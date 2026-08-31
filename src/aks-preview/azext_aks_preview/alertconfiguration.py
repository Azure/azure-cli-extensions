# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ResourceNotFoundError,
)
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import ResourceNotFoundError as SdkResourceNotFoundError

from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
    AlertConfiguration,
    AlertConfigurationProperties,
    AlertNotification,
)


def aks_alert_config_add_internal(cmd, client, raw_parameters, headers, no_wait):  # pylint: disable=unused-argument
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    name = raw_parameters.get("name")
    mode = raw_parameters.get("mode")
    action_group_id = raw_parameters.get("action_group_id")

    if not name:
        raise RequiredArgumentMissingError(
            "Please specify --name for the alert configuration."
        )
    if not mode:
        raise RequiredArgumentMissingError(
            "Please specify --mode for the alert configuration. "
            "Allowed values are 'Managed' and 'Disabled'."
        )

    alert_config = AlertConfiguration(
        properties=AlertConfigurationProperties(
            mode=mode,
            notification=AlertNotification(action_group_id=action_group_id or ""),
        )
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        name,
        alert_config,
        headers=headers,
    )


def aks_alert_config_update_internal(cmd, client, raw_parameters, headers, no_wait):  # pylint: disable=unused-argument
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    name = raw_parameters.get("name")
    mode = raw_parameters.get("mode")
    action_group_id = raw_parameters.get("action_group_id")

    if not name:
        raise RequiredArgumentMissingError(
            "Please specify --name for the alert configuration."
        )
    # An empty string is a meaningful value for --action-group-id (it clears the action
    # group), so distinguish "not supplied" (None) from "supplied as empty".
    if mode is None and action_group_id is None:
        raise RequiredArgumentMissingError(
            "Please specify at least one of --mode or --action-group-id to update."
        )

    try:
        existing = client.get(resource_group_name, cluster_name, name, headers=headers)
    except SdkResourceNotFoundError as ex:
        raise ResourceNotFoundError(
            f"Alert configuration '{name}' was not found in cluster '{cluster_name}'. "
            "Use 'az aks alert-config add' to create it."
        ) from ex

    existing_properties = getattr(existing, "properties", None)
    existing_mode = getattr(existing_properties, "mode", None)
    existing_notification = getattr(existing_properties, "notification", None)
    existing_action_group_id = getattr(existing_notification, "action_group_id", None)

    merged_mode = mode if mode is not None else existing_mode
    merged_action_group_id = (
        action_group_id if action_group_id is not None else existing_action_group_id
    )

    if merged_mode is None:
        raise RequiredArgumentMissingError(
            "Unable to determine the existing alert configuration mode. "
            "Please specify --mode to update this alert configuration."
        )

    alert_config = AlertConfiguration(
        properties=AlertConfigurationProperties(
            mode=merged_mode,
            notification=AlertNotification(action_group_id=merged_action_group_id or ""),
        )
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        name,
        alert_config,
        headers=headers,
    )
