# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


def _validate_name(namespace, attr, label):
    name = getattr(namespace, attr, None)
    if name is not None and not name.strip():
        raise InvalidArgumentValueError(f"{label} is not a valid.")


def validate_ai_manager_name(namespace):
    _validate_name(namespace, "ai_manager_name", "AI Manager name")


def validate_namespace_name(namespace):
    _validate_name(namespace, "namespace_name", "namespace name")


def validate_model_deployment_name(namespace):
    _validate_name(namespace, "model_deployment_name", "model deployment name")


def validate_ai_model_name(namespace):
    _validate_name(namespace, "ai_model_name", "AI model name")


def validate_model_source_name(namespace):
    _validate_name(namespace, "model_source_name", "model source name")


def _validate_key_value_pairs(values, option):
    if not values:
        return
    for item in values:
        if "=" not in item or not item.split("=", 1)[0].strip():
            raise InvalidArgumentValueError(
                f"{option} '{item}' is not in the expected key=value format.")


def validate_labels(namespace):
    _validate_key_value_pairs(namespace.labels, "--labels")


def validate_annotations(namespace):
    _validate_key_value_pairs(namespace.annotations, "--annotations")


def validate_overrides(namespace):
    _validate_key_value_pairs(namespace.overrides, "--overrides")
