# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_ai_manager_name(namespace):
    if namespace.ai_manager_name is not None and not namespace.ai_manager_name.strip():
        raise InvalidArgumentValueError("AI Manager name must not be empty.")


def validate_namespace_name(namespace):
    if getattr(namespace, "namespace_name", None) is not None and not namespace.namespace_name.strip():
        raise InvalidArgumentValueError("--name/-n is not a valid namespace name.")


def validate_model_deployment_name(namespace):
    name = getattr(namespace, "model_deployment_name", None)
    if name is not None and not name.strip():
        raise InvalidArgumentValueError("--name/-n is not a valid model deployment name.")


def validate_ai_model_name(namespace):
    name = getattr(namespace, "ai_model_name", None)
    if name is not None and not name.strip():
        raise InvalidArgumentValueError("--name/-n is not a valid AI model name.")


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
