# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from ..managed_components.managed_component import supported_components
from .._validators import validate_log_lines as _validate_n_normalize_component_log_lines
from .._validators import validate_log_since as _validate_n_normalize_component_log_since
from .._validators import validate_log_limit as _validate_n_normalize_component_log_limit
from .._clierror import NotSupportedPricingTierError
from .._util_enterprise import is_enterprise_tier


logger = get_logger(__name__)


def validate_component_logs(cmd, namespace):
    _validate_component_log_mutual_exclusive_param(namespace)
    _validate_component_log_required_param(namespace)
    _validate_n_normalize_component_for_logs(namespace)
    _validate_n_normalize_component_log_lines(namespace)
    _validate_n_normalize_component_log_since(namespace)
    _validate_n_normalize_component_log_limit(namespace)
    _validate_max_log_requests(namespace)
    _validate_is_enterprise_tier(cmd, namespace)


def validate_component_list(cmd, namespace):
    _validate_is_enterprise_tier(cmd, namespace)


def validate_instance_list(cmd, namespace):
    _validate_component_for_instance_list(namespace)
    _validate_is_enterprise_tier(cmd, namespace)


def _validate_max_log_requests(namespace):
    if namespace.max_log_requests <= 1:
        raise InvalidArgumentValueError("--max-log-requests should be larger than 0.")


def _validate_is_enterprise_tier(cmd, namespace):
    if is_enterprise_tier(cmd, namespace.resource_group, namespace.service) is False:
        raise NotSupportedPricingTierError("Only enterprise tier service instance is supported in this command.")


def _validate_n_normalize_component_for_logs(namespace):
    # Component name is optional for logs
    if namespace.name is None:
        return

    (is_supported, component_standard_name) = _is_component_supported(namespace.name)
    if is_supported:
        namespace.name = component_standard_name
        return

    _raise_invalid_component_error(namespace.name)


def _validate_component_for_instance_list(namespace):
    if namespace.component:
        (is_supported, component_standard_name) = _is_component_supported(namespace.component)
        if is_supported:
            namespace.component = component_standard_name
            return

    _raise_invalid_component_error(namespace.component)


def _is_component_supported(user_input_component_name):
    for c in supported_components:
        if c.match_ignore_case(user_input_component_name):
            return (True, c.get_name())
    return (False, None)


def _raise_invalid_component_error(user_input_component_name):
    msg_template = "Component '{}' is not supported. Supported components are: '{}'."
    component_names = list(map(lambda c: c.get_name(), supported_components))
    raise InvalidArgumentValueError(msg_template.format(user_input_component_name, ",".join(component_names)))


def _validate_component_log_mutual_exclusive_param(namespace):
    if namespace.all_instances is True and namespace.instance is not None:
        raise InvalidArgumentValueError("--all-instances cannot be set together with --instance/-i.")


def _validate_component_log_required_param(namespace):
    if namespace.name is None and not namespace.instance:
        raise InvalidArgumentValueError("When --name/-n is not set, --instance/-i is required.")
    if namespace.name is None and namespace.instance:
        logger.warning("--instance/-i is specified without --name/-n, will try best effort get logs by instance.")
