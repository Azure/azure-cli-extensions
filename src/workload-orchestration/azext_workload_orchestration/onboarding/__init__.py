# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Onboarding simplification commands for Workload Orchestration.

Provides convenience CLI commands that wrap multiple API calls
into single-command operations to reduce onboarding steps.
"""

from azext_workload_orchestration.onboarding.target_prepare import target_prepare


def target_init(
    cmd,
    cluster_name,
    resource_group,
    location,
    release_train=None,
    extension_version=None,
    extension_name=None,
    custom_location_name=None,
    skip_cert_manager=False,
    skip_trust_manager=False,
    kube_config=None,
    kube_context=None,
):
    """Prepare an Arc-connected cluster for Workload Orchestration."""
    result = target_prepare(
        cmd=cmd,
        cluster_name=cluster_name,
        resource_group=resource_group,
        location=location,
        extension_name=extension_name,
        custom_location_name=custom_location_name,
        extension_version=extension_version,
        release_train=release_train,
        skip_cert_manager=skip_cert_manager,
        skip_trust_manager=skip_trust_manager,
        kube_config=kube_config,
        kube_context=kube_context,
    )
    return result


__all__ = ['target_prepare', 'target_init']
