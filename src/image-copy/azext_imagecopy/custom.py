# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from multiprocessing import Pool

from azext_imagecopy.cli_utils import run_cli_command, prepare_cli_command
from azext_imagecopy.create_target import create_target_image

from knack.util import CLIError
from knack.log import get_logger
logger = get_logger(__name__)


# pylint: disable=too-many-statements
def imagecopy(source_resource_group_name, source_object_name, target_location,
              target_resource_group_name, source_type='image', cleanup='false',
              parallel_degree=-1, tags=None, target_name=None):

    # get the os disk id from source vm/image
    logger.warn("Getting os disk id of the source vm/image")
    cli_cmd = prepare_cli_command([source_type, 'show',
                                   '--name', source_object_name,
                                   '--resource-group', source_resource_group_name])

    json_cmd_output = run_cli_command(cli_cmd, return_as_json=True)

    if 'id' not in json_cmd_output['storageProfile']['osDisk']['managedDisk']:
        logger.error(
            "It looks like the source resource isn't backed by a managed OS disk. Quitting...")
        raise CLIError('Source with no Managed OS disk')

    if json_cmd_output['storageProfile']['dataDisks']:
        logger.warn("Data disks in the source detected, but are ignored by this extension!")

    source_os_disk_id = json_cmd_output['storageProfile']['osDisk']['managedDisk']['id']
    source_os_type = json_cmd_output['storageProfile']['osDisk']['osType']
    logger.debug("source_os_disk_id: %s. source_os_type: %s",
                 source_os_disk_id, source_os_type)

    # create source snapshots
    logger.warn("Creating source snapshot")
    source_os_disk_snapshot_name = source_object_name + '_os_disk_snapshot'
    cli_cmd = prepare_cli_command(['snapshot', 'create',
                                   '--name', source_os_disk_snapshot_name,
                                   '--resource-group', source_resource_group_name,
                                   '--source', source_os_disk_id])

    run_cli_command(cli_cmd)

    # Get SAS URL for the snapshotName
    logger.warn("Getting sas url for the source snapshot")
    cli_cmd = prepare_cli_command(['snapshot', 'grant-access',
                                   '--name', source_os_disk_snapshot_name,
                                   '--resource-group', source_resource_group_name,
                                   '--duration-in-seconds', '3600'])

    json_output = run_cli_command(cli_cmd, return_as_json=True)

    source_os_disk_snapshot_url = json_output['accessSas']
    logger.debug("source os disk snapshot url: %s",
                 source_os_disk_snapshot_url)

    # Start processing in the target locations

    transient_resource_group_name = 'image-copy-rg'
    create_resource_group(transient_resource_group_name, 'eastus')

    target_locations_count = len(target_location)
    logger.warn("Target location count: %s", target_locations_count)

    create_resource_group(target_resource_group_name,
                          target_location[0].strip())

    if parallel_degree == -1:
        pool = Pool(target_locations_count)
    else:
        pool = Pool(min(parallel_degree, target_locations_count))

    # try to get a handle on arm's 409s
    azure_pool_frequency = 5
    if target_locations_count >= 5:
        azure_pool_frequency = 15
    elif target_locations_count >= 3:
        azure_pool_frequency = 10

    tasks = []
    for location in target_location:
        location = location.strip()
        tasks.append((location, transient_resource_group_name, source_type,
                      source_object_name, source_os_disk_snapshot_name, source_os_disk_snapshot_url,
                      source_os_type, target_resource_group_name, azure_pool_frequency,
                      tags, target_name))

    logger.warn("Starting async process for all locations")

    for task in tasks:
        pool.apply_async(create_target_image, task)

    try:
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        logger.warn('User cancelled the operation')
        if cleanup:
            logger.warn('To cleanup temporary resources look for ones tagged with "image-copy-extension". \n'
                        'You can use the following command: az resource list --tag created_by=image-copy-extension')
        pool.terminate()
        return

    # Cleanup
    if cleanup:
        logger.warn('Deleting transient resources')

        # Delete resource group
        cli_cmd = prepare_cli_command(['group', 'delete', '--no-wait', '--yes',
                                       '--name', transient_resource_group_name])
        run_cli_command(cli_cmd)

        # Revoke sas for source snapshot
        cli_cmd = prepare_cli_command(['snapshot', 'revoke-access',
                                       '--name', source_os_disk_snapshot_name,
                                       '--resource-group', source_resource_group_name])
        run_cli_command(cli_cmd)

        # Delete source snapshot
        cli_cmd = prepare_cli_command(['snapshot', 'delete',
                                       '--name', source_os_disk_snapshot_name,
                                       '--resource-group', source_resource_group_name])
        run_cli_command(cli_cmd)


def create_resource_group(resource_group_name, location):
    # check if target resource group exists
    cli_cmd = prepare_cli_command(['group', 'exists',
                                   '--name', resource_group_name], output_as_json=False)

    cmd_output = run_cli_command(cli_cmd)

    if 'true' in cmd_output:
        return

    # create the target resource group
    logger.warn("Creating resource group: %s", resource_group_name)
    cli_cmd = prepare_cli_command(['group', 'create',
                                   '--name', resource_group_name,
                                   '--location', location])

    run_cli_command(cli_cmd)
