# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals

from knack.log import get_logger
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError
from azure.cli.core.util import sdk_no_wait, user_confirmation
from ..utils.temp_cluster_capabilities import temp_cluster_capabilities
from ..utils.validators import (
    is_supported_vcore,
    validate_resource_group)
from ..utils._util import (
    check_resource_group,
    generate_missing_cluster_parameters)

logger = get_logger(__name__)

HORIZONDB_VERSION_DEFAULT = 17


def horizondb_cluster_create(cmd, client, resource_group_name=None, cluster_name=None, location=None,
                             administrator_login=None, administrator_login_password=None,
                             tags=None, version=None,
                             replica_count=None, v_cores=None,
                             zone_placement_policy=None,
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

    validate_resource_group(resource_group_name)

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
