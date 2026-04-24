# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Onboarding simplification commands for Workload Orchestration.

Provides convenience CLI commands that wrap multiple API calls
into single-command operations to reduce onboarding steps.
"""

from azext_workload_orchestration.onboarding.target_prepare import target_prepare
from azext_workload_orchestration.onboarding.target_deploy import target_deploy as _target_deploy
from azext_workload_orchestration.onboarding.hierarchy_create import hierarchy_create as _hierarchy_create


def _validate_dependency_versions(data):
    """Validate the pre-parsed ``--extension-dependency-version`` dict against
    the EXTENSION_DEPENDENCIES registry. AAZ has already parsed the shorthand
    into a ``dict[str,str]`` for us.
    """
    from azure.cli.core.azclierror import ValidationError
    from azext_workload_orchestration.onboarding.consts import EXTENSION_DEPENDENCIES

    if not data:
        return {}
    if not isinstance(data, dict):
        raise ValidationError(
            "--extension-dependency-version must be a dependency-map object."
        )

    allowed = {k.lower(): k for k in EXTENSION_DEPENDENCIES}
    seen_lower = set()
    normalized = {}
    for key, value in data.items():
        if not isinstance(key, str) or not key:
            raise ValidationError("--extension-dependency-version key must be a non-empty string.")
        low = key.lower()
        if low in seen_lower:
            raise ValidationError(f"Duplicate dependency key: {key}")
        seen_lower.add(low)
        if low not in allowed:
            raise ValidationError(
                f"Unknown dependency key: {key}. "
                f"Supported: {', '.join(sorted(EXTENSION_DEPENDENCIES))}"
            )
        if not isinstance(value, str) or not value:
            raise ValidationError(
                f"Dependency value for {key} must be a non-empty string."
            )
        normalized[allowed[low]] = value
    return normalized


def target_init(
    cmd,
    cluster_name,
    resource_group,
    location,
    release_train=None,
    extension_version=None,
    extension_name=None,
    custom_location_name=None,
    extension_dependency_version=None,
):
    """Prepare an Arc-connected cluster for Workload Orchestration."""
    dep_versions = _validate_dependency_versions(extension_dependency_version)
    iot_platform_version = dep_versions.get("iotplatform")

    return target_prepare(
        cmd=cmd,
        cluster_name=cluster_name,
        resource_group=resource_group,
        location=location,
        extension_name=extension_name,
        custom_location_name=custom_location_name,
        extension_version=extension_version,
        release_train=release_train,
        cert_manager_version=iot_platform_version,
    )


def target_deploy(
    cmd,
    resource_group,
    target_name,
    solution_template_version_id=None,
    solution_template_name=None,
    solution_template_version=None,
    config=None,
    config_hierarchy_id=None,
    config_template_rg=None,
    config_template_name=None,
    config_template_version=None,
):
    """Deploy a solution to a target: review -> publish -> install."""
    return _target_deploy(
        cmd=cmd,
        resource_group=resource_group,
        target_name=target_name,
        solution_template_version_id=solution_template_version_id,
        solution_template_name=solution_template_name,
        solution_template_version=solution_template_version,
        config=config,
        config_hierarchy_id=config_hierarchy_id,
        config_template_rg=config_template_rg,
        config_template_name=config_template_name,
        config_template_version=config_template_version,
    )


def hierarchy_create(cmd, resource_group=None, configuration_location=None, hierarchy_spec=None):
    """Create a hierarchy: Site + Configuration + ConfigurationReference.

    AAZ has already parsed ``hierarchy_spec`` into a dict for us.
    """
    return _hierarchy_create(
        cmd=cmd,
        resource_group=resource_group,
        configuration_location=configuration_location,
        hierarchy_spec=hierarchy_spec,
    )


__all__ = ['target_prepare', 'target_init', 'target_deploy', 'hierarchy_create']
