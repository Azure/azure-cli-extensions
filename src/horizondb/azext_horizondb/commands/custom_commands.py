# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals

from knack.log import get_logger
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError, InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait, user_confirmation
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id

logger = get_logger(__name__)


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


def horizondb_cluster_create(client, resource_group_name, cluster_name, location,
                             administrator_login, administrator_login_password,
                             tags=None, version=None,
                             replica_count=None, v_cores=None,
                             zone_placement_policy=None,
                             no_wait=False):
    from azext_horizondb.vendored_sdks.models import HorizonDbCluster, HorizonDbClusterProperties

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

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       resource=resource)


def _parse_restore_time(restore_time):
    import datetime
    if restore_time is None:
        # During preview, default to 6 minutes before now to satisfy the minimum 5-minute buffer.
        return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(minutes=6)
    from dateutil import parser
    try:
        return parser.parse(restore_time)
    except (ValueError, OverflowError):
        raise InvalidArgumentValueError(
            "The restore time value has an incorrect date format. "
            "Please use ISO8601 format, e.g., 2026-07-15T02:10:00+00:00.")


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


def horizondb_cluster_update(client, resource_group_name, cluster_name,
                             administrator_login_password=None, tags=None,
                             v_cores=None,
                             parameter_group=None,
                             no_wait=False):
    from azext_horizondb.vendored_sdks.models import (
        HorizonDbClusterForPatchUpdate,
        HorizonDbClusterParameterGroupConnectionProperties,
        HorizonDbClusterPropertiesForPatchUpdate,
    )

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

    if not patch_properties:
        raise ArgumentUsageError("Specify at least one argument to update.")

    properties = HorizonDbClusterForPatchUpdate(**patch_properties)

    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       properties=properties)


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
