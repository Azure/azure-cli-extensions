# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azure.cli.core.azclierror import (
    ArgumentUsageError,
    ValidationError,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
import azext_arcdata.core.common_validators as validators
import os
import pydash as _


def force_indirect(namespace):
    namespace.use_k8s = True


def validate_copy_logs(namespace):
    if (namespace.resource_kind is None) ^ (namespace.resource_name is None):
        raise ValidationError(
            "Either --resource-kind or --resource-name is not specified. They "
            "need to be provided or omitted at the same time."
        )
    force_indirect(namespace)


def validate_create(namespace):
    arm_only = [
        "auto_upload_logs",
        "auto_upload_metrics",
        "custom_location",
        "cluster_name",
        "least_privilege",
    ]
    kubernetes_only = [
        "annotations",
        "labels",
        "logs_ui_private_key_file",
        "logs_ui_public_key_file",
        "metrics_ui_private_key_file",
        "metrics_ui_public_key_file",
        "service-annotations",
        "service_labels",
        "storage_annotations",
        "storage_labels",
        "use_k8s",
    ]

    if namespace.profile_name and namespace.path:
        raise ArgumentUsageError(
            "Cannot specify both '[--profile-name]' and '[--path]'. "
            "Specify only one."
        )

    if not namespace.use_k8s:
        # -- monitoring specific messages --
        monitoring_cert_keys = [
            "logs_ui_public_key_file",
            "logs_ui_private_key_file",
            "metrics_ui_public_key_file",
            "metrics_ui_private_key_file",
        ]
        for key in monitoring_cert_keys:
            if getattr(namespace, key, None):
                raise ArgumentUsageError(
                    "Cannot specify {0} in direct mode. Monitoring endpoint "
                    "certificate arguments are for indirect mode only.".format(
                        "--" + "-".join(key.split("_"))
                    )
                )

    validators.validate_mutually_exclusive_arm_kubernetes(
        namespace, kubernetes_only, arm_only
    )


def validate_delete(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_controldb_cdc_retention(namespace):
    min_hrs = 1
    max_hrs = 24
    if not (min_hrs <= namespace.retention_hours <= max_hrs):
        raise ArgumentUsageError(
            f"ControlDB Change Data Capture retention hours must be between {min_hrs} and {max_hrs}."
        )
    force_indirect(namespace)


def validate_status_show(namespace):
    validators.validate_mutually_exclusive_direct_indirect(namespace)


def validate_update(namespace):
    """
    Validates the supplied arguments for 'arc dc update' command
    """
    direct_only = []

    common_args = ["desired_version"]

    maintenance_window_args = [
        "maintenance_start",
        "maintenance_duration",
        "maintenance_recurrence",
        "maintenance_time_zone",
        "maintenance_enabled",
    ]

    valid_update = False

    # -- indirect --
    if namespace.use_k8s:
        if namespace.auto_upload_logs:
            direct_only.append("--auto-upload-logs")
        if namespace.auto_upload_metrics:
            direct_only.append("--auto-upload-metrics")

        indirect_update_args = common_args + maintenance_window_args

        # make sure at least one property is being updated
        for key in indirect_update_args:
            if getattr(namespace, key, None):
                valid_update = True

        if not valid_update:
            args = [
                "--" + "-".join(arg.split("_")) for arg in indirect_update_args
            ]
            raise ArgumentUsageError(
                "Atleast one of the following is required when "
                "running this command with Kubernetes API-targeted arguments: [{args}]".format(
                    args=", ".join(args)
                )
            )

    if not namespace.use_k8s:
        for key in maintenance_window_args:
            if getattr(namespace, key, None):
                raise ArgumentUsageError(
                    "Cannot specify '{0}' without '--use-k8s'. "
                    "Maintenance window arguments are only available for commands using the Kubernetes API.".format(
                        "--" + "-".join(key.split("_"))
                    )
                )

        direct_update_args = common_args + [
            "auto_upload_logs",
            "auto_upload_metrics",
        ]

        # make sure at least one property is being updated
        for key in direct_update_args:
            if getattr(namespace, key, None):
                valid_update = True

        if not valid_update:
            args = [
                "--" + "-".join(arg.split("_")) for arg in direct_update_args
            ]
            raise ArgumentUsageError(
                "Atleast one of the following is required when "
                "running this command with ARM-targeted arguments: [{args}]".format(
                    args=", ".join(args)
                )
            )

    validators.validate_mutually_exclusive_direct_indirect(
        namespace, direct_only=direct_only
    )


def validate_upgrade(namespace):
    required_for_direct = []

    # -- direct --
    if not namespace.use_k8s:
        if hasattr(namespace, "desired_version"):
            if not namespace.desired_version:
                required_for_direct.append("--desired-version")

        if not namespace.name:
            required_for_direct.append("--name")

    # -- assert common indirect/direct argument combos --
    validators.validate_mutually_exclusive_direct_indirect(
        namespace, required_direct=required_for_direct
    )

    validate_client_version_for_upgrade(command_values=namespace)


def validate_upload(namespace):
    if not os.path.exists(namespace.path):
        raise FileNotFoundError(
            'Cannot find file: "{}". Please provide the correct file name '
            "and try again".format(namespace.path)
        )


def validate_client_version_for_upgrade(command_values):
    """
    Upgrading beyond the current version in the CLI is not currently supported.
    We need to provide an error to the user indicating that the version selected is not
    allowed.
    """

    if not command_values.desired_version:
        # in this case, we expect later code to select the correct version.
        return

    if not ArcDataImageService.is_image_version_supported_by_cli(
        command_values.desired_version
    ):
        raise ValueError(
            f"The desired version {command_values.desired_version} is not supported by this version of the "
            "ArcData CLI extension. Please upgrade the extension using the following command and try again: "
            "\naz extension update -n arcdata"
        )
