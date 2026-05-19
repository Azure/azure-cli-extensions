# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Support bundle package for workload-orchestration CLI extension.

This package provides the ``az workload-orchestration support create-bundle`` command
which collects Kubernetes cluster diagnostics, runs prerequisite validation checks,
and packages everything into a zip bundle for troubleshooting.

Modules:
    consts      — Constants (namespaces, thresholds, folder names, API groups)
    utils       — K8s client initialization, safe API calls, file writers, parsers
    collectors  — Resource descriptions, container logs, and metrics collection
    validators  — 10 prerequisite validation categories with 50+ individual checks
    bundle      — Main orchestration logic that ties everything together
"""

from azext_workload_orchestration.support.bundle import create_support_bundle

__all__ = ["create_support_bundle"]
