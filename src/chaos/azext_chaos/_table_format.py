# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict

from azure.mgmt.core.tools import parse_resource_id
from jmespath import compile as compile_jmes, Options


def _project(result, expr):
    parsed = compile_jmes(expr)
    return parsed.search(result, Options(dict_cls=OrderedDict))


# ── workspace ────────────────────────────────────────────────────────────


def workspace_show_table_format(result):
    """Table formatter for a single workspace.

    ``resourceGroup`` is not on the ARM tracked-resource body; aaz-dev-generated
    commands return raw API responses without the CLI core's resource-group
    injection.  Derive it from ``id`` to match the column users expect.
    """
    proj = dict(result)  # copy to avoid mutating the input
    rid = proj.get('id') or ''
    proj['_resourceGroup'] = (
        parse_resource_id(rid).get('resource_group', '') if rid else ''
    )
    return _project(proj, """{
        Name: name,
        ResourceGroup: _resourceGroup,
        Location: location,
        ProvisioningState: properties.provisioningState,
        IdentityType: identity.type
    }""")


def workspace_list_table_format(results):
    return [workspace_show_table_format(r) for r in results]


# ── workspace show-discovery / show-evaluation ───────────────────────────


def workspace_discovery_show_table_format(result):
    """Table formatter for the latest workspace discovery result."""
    return _project(result, """{
        Status: properties.status,
        StartTime: properties.startTime,
        EndTime: properties.endTime
    }""")


def workspace_evaluation_show_table_format(result):
    """Table formatter for the latest workspace evaluation result.

    Intentionally identical to workspace_discovery_show_table_format —
    both API operations return the same shape but represent semantically
    distinct operations (discovery vs. evaluation).
    """
    return _project(result, """{
        Status: properties.status,
        StartTime: properties.startTime,
        EndTime: properties.endTime
    }""")


# ── scenario ─────────────────────────────────────────────────────────────


def scenario_show_table_format(result):
    return _project(result, """{
        Name: name,
        Version: properties.version,
        Description: properties.description,
        Recommendation: properties.recommendation.recommendationStatus
    }""")


def scenario_list_table_format(results):
    return [scenario_show_table_format(r) for r in results]


# ── scenario config ──────────────────────────────────────────────────────


def scenario_config_show_table_format(result):
    """Table formatter for a single scenario configuration.

    ``properties.scenarioId`` is a full ARM resource ID
    (e.g., ``/subscriptions/.../scenarios/ZoneDown-1.0``).  We extract the
    scenario name for display — this is the case that forces a Python
    callable; a bare JMESPath string cannot call ``parse_resource_id()``.
    """
    proj = dict(result)  # copy to avoid mutating the input
    scenario_id = (proj.get('properties') or {}).get('scenarioId') or ''
    # parse_resource_id returns 'resource_name' for the deepest child segment
    # (scenarios/{name}); 'name' would return the workspace, not the scenario.
    proj['_scenarioName'] = (
        parse_resource_id(scenario_id).get('resource_name', '')
        if scenario_id else ''
    )
    return _project(proj, """{
        Name: name,
        Scenario: _scenarioName,
        ProvisioningState: properties.provisioningState
    }""")


def scenario_config_list_table_format(results):
    return [scenario_config_show_table_format(r) for r in results]


# ── scenario run ─────────────────────────────────────────────────────────


def scenario_run_show_table_format(result):
    return _project(result, """{
        RunId: name,
        Status: properties.status,
        StartTime: properties.startTime,
        EndTime: properties.endTime
    }""")


def scenario_run_list_table_format(results):
    return [scenario_run_show_table_format(r) for r in results]


# ── validation ───────────────────────────────────────────────────────────


def validation_show_table_format(result):
    """Table formatter for validation results.

    Surfaces status, timing, and error counts so failed validations are
    diagnosable from ``--output table``; full bodies live in ``--output json``.
    """
    props = result.get('properties') or {}
    sys_errs = props.get('errors') or []
    biz_errs = (props.get('validationErrors') or {}).get('errors') or []
    error_summary = (
        '' if not (sys_errs or biz_errs)
        else f'{len(sys_errs)} system, {len(biz_errs)} validation'
    )
    proj = dict(result)
    proj['_errorSummary'] = error_summary
    return _project(proj, """{
        Status: properties.status,
        StartTime: properties.startTime,
        EndTime: properties.endTime,
        Errors: _errorSummary
    }""")


# ── permission fix ───────────────────────────────────────────────────────


def permission_fix_show_table_format(result):
    """Table formatter for permission-fix results."""
    return _project(result, """{
        State: properties.state,
        Summary: properties.summary,
        WhatIfMode: properties.whatIfMode
    }""")


# ── discovered resource ──────────────────────────────────────────────────


def discovered_resource_show_table_format(result):
    """Table formatter for a single discovered resource.

    Columns derived from the ``DiscoveredResourceProperties`` schema:
    namespace, resourceName, resourceType, fullyQualifiedIdentifier,
    discoveredAt, scope.  We surface the most useful subset for table width.
    """
    return _project(result, """{
        Name: name,
        ResourceName: properties.resourceName,
        ResourceType: properties.resourceType,
        Namespace: properties.namespace,
        DiscoveredAt: properties.discoveredAt
    }""")


def discovered_resource_list_table_format(results):
    return [discovered_resource_show_table_format(r) for r in results]
