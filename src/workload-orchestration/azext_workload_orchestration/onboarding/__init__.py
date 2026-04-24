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


def _parse_dependency_versions(raw_pairs):
    """Parse ``key=value`` pairs into ``{key: version}`` dict."""
    from azext_workload_orchestration.onboarding.consts import EXTENSION_DEPENDENCIES
    from azure.cli.core.azclierror import ValidationError

    if not raw_pairs:
        return {}

    result = {}
    for pair in raw_pairs:
        if '=' not in pair:
            raise ValidationError(
                f"Invalid dependency format: '{pair}'. "
                "Expected key=value (e.g., iotplatform=1.6.1)."
            )
        key, version = pair.split('=', 1)
        key = key.strip().lower()
        version = version.strip()
        if key not in EXTENSION_DEPENDENCIES:
            supported = ', '.join(sorted(EXTENSION_DEPENDENCIES))
            raise ValidationError(
                f"Unsupported dependency '{key}'. "
                f"Supported values: {supported}."
            )
        if key in result:
            raise ValidationError(f"Duplicate dependency key '{key}'.")
        if not version:
            raise ValidationError(
                f"Empty version for dependency '{key}'."
            )
        result[key] = version
    return result


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
    dep_versions = _parse_dependency_versions(
        extension_dependency_version
    )
    iot_platform_version = dep_versions.get("iotplatform")

    result = target_prepare(
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
    return result


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


__all__ = ['target_prepare', 'target_init', 'target_deploy', 'hierarchy_create']


def hierarchy_create(cmd, resource_group=None, configuration_location=None, hierarchy_spec=None):
    """Create a hierarchy: Site + Configuration + ConfigurationReference."""
    return _hierarchy_create(
        cmd=cmd,
        resource_group=resource_group,
        configuration_location=configuration_location,
        hierarchy_spec=hierarchy_spec,
    )
