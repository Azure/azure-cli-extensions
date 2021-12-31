# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from re import match

from azure.cli.core.azclierror import ClientRequestError, ValidationError
from knack.log import get_logger

from ._resource_quantity import validate_cpu as validate_and_normalize_cpu
from ._resource_quantity import \
    validate_memory as validate_and_normalize_memory
from ._util_enterprise import is_enterprise_tier
from ._validators import validate_instance_count

logger = get_logger(__name__)


def only_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' only supports for Enterprise tier Spring instance.".format(namespace.command))


def not_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' doesn't support for Enterprise tier Spring instance.".format(namespace.command))


def validate_cpu(namespace):
    namespace.cpu = validate_and_normalize_cpu(namespace.cpu)


def validate_memory(namespace):
    namespace.memory = validate_and_normalize_memory(namespace.memory)


def validate_git_uri(namespace):
    uri = namespace.uri
    if uri and (not uri.startswith("https://")) and (not uri.startswith("git@")):
        raise ValidationError("Git URI should start with \"https://\" or \"git@\"")


def validate_config_file_patterns(namespace):
    if namespace.config_file_patterns:
        _validate_patterns(namespace.config_file_patterns)


def validate_acs_patterns(namespace):
    if namespace.patterns:
        _validate_patterns(namespace.patterns)


def _validate_patterns(patterns):
    pattern_list = patterns.split(',')
    invalid_list = [p for p in pattern_list if not _is_valid_pattern(p)]
    if len(invalid_list) > 0:
        logger.warning("Patterns '%s' are invalid.", ','.join(invalid_list))
        raise ValidationError("Patterns should be the collection of patterns separated by comma, each pattern in the format of 'application' or 'application/profile'")


def _is_valid_pattern(pattern):
    return _is_valid_app_name(pattern) or _is_valid_app_and_profile_name(pattern)


def _is_valid_app_name(pattern):
    return match(r"^[a-zA-Z][-_a-zA-Z0-9]*$", pattern) is not None


def _is_valid_profile_name(profile):
    return profile == "*" or _is_valid_app_name(profile)


def _is_valid_app_and_profile_name(pattern):
    parts = pattern.split('/')
    return len(parts) == 2 and _is_valid_app_name(parts[0]) and _is_valid_profile_name(parts[1])


def validate_gateway_update(namespace):
    _validate_sso(namespace)
    validate_cpu(namespace)
    validate_memory(namespace)
    validate_instance_count(namespace)


def validate_api_portal_update(namespace):
    _validate_sso(namespace)
    validate_instance_count(namespace)


def _validate_sso(namespace):
    all_provided = namespace.scope and namespace.client_id and namespace.client_secret and namespace.issuer_uri
    none_provided = namespace.scope is None and namespace.client_id is None and namespace.client_secret is None and namespace.issuer_uri is None
    if not all_provided and not none_provided :
        raise ValidationError("Single Sign On configurations '--scope --client-id --client-secret --issuer-uri' should be all provided or none provided.")
    if namespace.scope:
        namespace.scope = namespace.scope.split(",")


def validate_routes(namespace):
    if namespace.routes_json is not None and namespace.routes_file is not None:
        raise ValidationError("You can only specify either --routes-json or --routes-file.")


def validate_gateway_instance_count(namespace):
    if namespace.gateway_instance_count is not None:
        if namespace.gateway_instance_count < 1:
            raise ValidationError("--gateway-instance-count must be greater than 0")


def validate_api_portal_instance_count(namespace):
    if namespace.api_portal_instance_count is not None:
        if namespace.api_portal_instance_count < 1:
            raise ValidationError("--api-portal-instance-count must be greater than 0")
