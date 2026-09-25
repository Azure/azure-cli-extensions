# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals

from knack.log import get_logger
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError, InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait, user_confirmation
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from ..utils.temp_cluster_capabilities import temp_cluster_capabilities
from ..utils.validators import (
    is_supported_vcore,
    validate_resource_group)
from ..utils._util import (
    check_resource_group,
    generate_missing_cluster_parameters)
from ..utils._network import resolve_public_access_range

logger = get_logger(__name__)

HORIZONDB_VERSION_DEFAULT = 17


def _resolve_source_cluster(client, resource_group_name, source_cluster):
    if is_valid_resource_id(source_cluster):
        source_cluster_id_parts = parse_resource_id(source_cluster)
        source_resource_group = source_cluster_id_parts.get("resource_group")
        source_cluster_name = source_cluster_id_parts.get("name")
        if not source_resource_group or not source_cluster_name:
            raise ArgumentUsageError(
                "Invalid source cluster resource identifier. Ensure it contains both resource group and cluster name."
            )
        return client.get(resource_group_name=source_resource_group, cluster_name=source_cluster_name)
    return client.get(resource_group_name=resource_group_name, cluster_name=source_cluster)


def horizondb_cluster_create(cmd, client, resource_group_name=None, cluster_name=None, location=None,
                             administrator_login=None, administrator_login_password=None,
                             tags=None, version=None,
                             replica_count=None, v_cores=None,
                             zone_placement_policy=None,
                             public_access=None, yes=False,
                             no_wait=False):
    from azext_horizondb.vendored_sdks.models import HorizonDbCluster, HorizonDbClusterProperties

    if not check_resource_group(resource_group_name):
        resource_group_name = None

    # Generate missing parameters
    resource_group_name, cluster_name, location = generate_missing_cluster_parameters(cmd, resource_group_name, cluster_name,
                                                                                      location)

    if version is None:
        version = HORIZONDB_VERSION_DEFAULT

    if v_cores is not None:
        cluster_capability = (temp_cluster_capabilities.get("value") or [{}])[0]
        processor_capabilities = (cluster_capability.get("supportedProcessor") or [{}])[0]

        if not is_supported_vcore(processor_capabilities, v_cores):
            supported_vcores = processor_capabilities.get("supportedVcores", [])
            raise ArgumentUsageError(
                "Invalid value for '--v-cores'. Supported values: {}".format(
                    ", ".join(str(v) for v in supported_vcores)
                )
            )

    properties = HorizonDbClusterProperties(
        administrator_login=administrator_login,
        administrator_login_password=administrator_login_password,
        version=version,
        create_mode="Create",
        replica_count=replica_count,
        v_cores=v_cores,
        zone_placement_policy=zone_placement_policy,
    )

    resource = HorizonDbCluster(
        location=location,
        tags=tags,
        properties=properties,
    )

    # Resolve --public-access up front (including client-IP detection / prompts for 'Enabled') so any
    # failure happens before the cluster is provisioned. HorizonDB's publicNetworkAccess flag is
    # service-computed (read-only), so public access is opened by creating a firewall rule.
    firewall_range = _resolve_public_access_range_for_command(public_access, yes, is_update=False)

    result = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name=resource_group_name,
                         cluster_name=cluster_name,
                         resource=resource)

    if firewall_range is None:
        return result

    cluster = result.result() if hasattr(result, 'result') else result
    _create_public_access_firewall_rule(cmd, resource_group_name, cluster_name, firewall_range, no_wait)
    return cluster


def _parse_restore_time(restore_time):
    import datetime
    if restore_time is None:
        # During preview, default to 6 minutes before now to satisfy the minimum 5-minute buffer.
        return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(minutes=6)
    from dateutil import parser
    try:
        parsed = parser.parse(restore_time)
    except (ValueError, OverflowError):
        raise InvalidArgumentValueError(
            "The restore time value has an incorrect date format. "
            "Please use ISO8601 format, e.g., 2026-07-15T02:10:00+00:00.")
    # Normalize to a UTC-aware datetime so the value sent to the service is unambiguous.
    # A value without an explicit offset is interpreted as UTC (per the --restore-time contract);
    # an offset-aware value is converted to UTC.
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def horizondb_cluster_restore(client, resource_group_name, cluster_name, source_cluster,
                              restore_time=None, tags=None, no_wait=False):
    from azext_horizondb.vendored_sdks.models import HorizonDbCluster, HorizonDbClusterProperties

    source_cluster_resource = _resolve_source_cluster(client, resource_group_name, source_cluster)
    properties = HorizonDbClusterProperties(
        create_mode="PointInTimeRestore",
        source_cluster_resource_id=source_cluster_resource.id,
        point_in_time_utc=_parse_restore_time(restore_time),
    )

    resource = HorizonDbCluster(
        location=source_cluster_resource.location,
        tags=tags,
        properties=properties,
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       resource=resource)


def _resolve_public_access_range_for_command(public_access, yes, is_update):
    """Return an (start_ip, end_ip) tuple to open via a firewall rule, or None when no rule should be
    created. Handles the read-only-flag reality: 'Disabled'/'None'/unset create no rule."""
    if not public_access:
        return None
    if str(public_access).lower() == 'disabled':
        if is_update:
            logger.warning("HorizonDB public network access is managed through firewall rules. To "
                           "remove public access, delete rules with 'az horizondb firewall-rule "
                           "delete' (list them with 'az horizondb firewall-rule list').")
        return None

    start_ip, end_ip = resolve_public_access_range(public_access, yes)
    if start_ip == -1 or end_ip == -1:
        return None
    return start_ip, end_ip


def _create_public_access_firewall_rule(cmd, resource_group_name, cluster_name, firewall_range, no_wait):
    from .._client_factory import cf_horizondb_firewall_rules
    from .firewall_rule_commands import create_firewall_rule
    start_ip, end_ip = firewall_range
    firewall_client = cf_horizondb_firewall_rules(cmd.cli_ctx, None)
    poller = create_firewall_rule(cmd, firewall_client, resource_group_name, cluster_name,
                                  start_ip_address=start_ip, end_ip_address=end_ip)
    if not no_wait:
        poller.result()


def horizondb_cluster_update(cmd, client, resource_group_name, cluster_name,
                             administrator_login_password=None, tags=None,
                             v_cores=None,
                             parameter_group=None,
                             public_access=None, yes=False,
                             no_wait=False):
    from azext_horizondb.vendored_sdks.models import (
        HorizonDbClusterForPatchUpdate,
        HorizonDbClusterParameterGroupConnectionProperties,
        HorizonDbClusterPropertiesForPatchUpdate,
    )

    validate_resource_group(resource_group_name)

    # Resolve --public-access up front so prompts/failures happen before any patch or firewall PUT.
    firewall_range = _resolve_public_access_range_for_command(public_access, yes, is_update=True)

    cluster_properties = {}
    if administrator_login_password is not None:
        cluster_properties["administrator_login_password"] = administrator_login_password
    if v_cores is not None:
        cluster_properties["v_cores"] = v_cores
    if parameter_group is not None:
        cluster_properties["parameter_group"] = HorizonDbClusterParameterGroupConnectionProperties(id=parameter_group)

    patch_properties = {}
    if tags is not None:
        patch_properties["tags"] = tags
    if cluster_properties:
        patch_properties["properties"] = HorizonDbClusterPropertiesForPatchUpdate(**cluster_properties)

    if not patch_properties and not public_access:
        raise ArgumentUsageError("Specify at least one argument to update.")

    update_result = None
    if patch_properties:
        properties = HorizonDbClusterForPatchUpdate(**patch_properties)
        update_result = sdk_no_wait(no_wait, client.begin_update,
                                    resource_group_name=resource_group_name,
                                    cluster_name=cluster_name,
                                    properties=properties)

    if firewall_range is not None:
        _create_public_access_firewall_rule(cmd, resource_group_name, cluster_name, firewall_range, no_wait)

    if update_result is not None:
        return update_result
    return client.get(resource_group_name=resource_group_name, cluster_name=cluster_name)


def horizondb_cluster_delete(cmd, client, resource_group_name, cluster_name, no_wait=False, yes=False):
    if not yes:
        user_confirmation(
            "Are you sure you want to delete the cluster '{0}' in resource group '{1}'".format(cluster_name,
                                                                                               resource_group_name), yes=yes)
    try:
        result = sdk_no_wait(no_wait, client.begin_delete,
                             resource_group_name=resource_group_name,
                             cluster_name=cluster_name)
        if cmd.cli_ctx.local_context.is_on:
            local_context_file = cmd.cli_ctx.local_context._get_local_context_file()  # pylint: disable=protected-access
            local_context_file.remove_option('horizondb', 'cluster_name')
    except Exception as ex:  # pylint: disable=broad-except
        logger.error(ex)
        raise CLIInternalError(str(ex)) from ex
    return result


def horizondb_cluster_list(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
