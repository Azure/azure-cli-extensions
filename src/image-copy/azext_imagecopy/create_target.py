import hashlib
import datetime
import time
from azext_imagecopy.cli_utils import run_cli_command, prepare_cli_command
from azure.cli.core.application import APPLICATION
from azure.cli.core.util import CLIError
import azure.cli.core.azlogging as azlogging

logger = azlogging.get_az_logger(__name__)

PROGRESS_LINE_LENGTH = 40

def create_target_image(location, transient_resource_group_name, source_type, source_object_name, \
    source_os_disk_snapshot_name, source_os_disk_snapshot_url, source_os_type, \
    target_resource_group_name, azure_pool_frequency):

    subscription_id = get_subscription_id()

    subscription_hash = hashlib.sha1(subscription_id.encode("UTF-8")).hexdigest()
    unique_subscription_string = subscription_hash[:7]


    # create the target storage account
    logger.warn("{0} - Creating target storage account (can be slow sometimes)".format(location))
    target_storage_account_name = location + unique_subscription_string
    cmd = prepare_cli_command(['storage', 'account', 'create', \
        '--name', target_storage_account_name, \
        '--resource-group', transient_resource_group_name, \
        '--location', location, \
        '--sku', 'Standard_LRS'])

    json_output = run_cli_command(cmd, return_as_json=True)
    target_blob_endpoint = json_output['primaryEndpoints']['blob']


    # Setup the target storage account
    cmd = prepare_cli_command(['storage', 'account', 'keys', 'list', \
        '--account-name', target_storage_account_name, \
        '--resource-group', transient_resource_group_name])

    json_output = run_cli_command(cmd, return_as_json=True)

    target_storage_account_key = json_output[0]['value']
    logger.debug(target_storage_account_key)

    expiry_format = "%Y-%m-%dT%H:%MZ"
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    cmd = prepare_cli_command(['storage', 'account', 'generate-sas', \
        '--account-name', target_storage_account_name, \
        '--account-key', target_storage_account_key, \
        '--expiry', expiry.strftime(expiry_format), \
        '--permissions', 'aclrpuw', '--resource-types', \
        'sco', '--services', 'b', '--https-only'], \
        output_as_json=False)

    sas_token = run_cli_command(cmd)
    sas_token = sas_token.rstrip("\n\r") #STRANGE
    logger.debug("sas token: " + sas_token)


    # create a container in the target blob storage account
    logger.warn("{0} - Creating container in the target storage account".format(location))
    target_container_name = 'snapshots'
    cmd = prepare_cli_command(['storage', 'container', 'create', \
        '--name', target_container_name, \
        '--account-name', target_storage_account_name])

    run_cli_command(cmd)


    # Copy the snapshot to the target region using the SAS URL
    blob_name = source_os_disk_snapshot_name + '.vhd'
    logger.warn("{0} - Copying blob to target storage account".format(location))
    cmd = prepare_cli_command(['storage', 'blob', 'copy', 'start', \
        '--source-uri', source_os_disk_snapshot_url, \
        '--destination-blob', blob_name, \
        '--destination-container', target_container_name, \
        '--account-name', target_storage_account_name, \
        '--sas-token', sas_token])

    run_cli_command(cmd)


    # Wait for the copy to complete
    start_datetime = datetime.datetime.now()
    wait_for_blob_copy_operation(blob_name, target_container_name, \
        target_storage_account_name, azure_pool_frequency, location)
    msg = "{0} - Copy time: {1}".format(location, datetime.datetime.now()-start_datetime).ljust(PROGRESS_LINE_LENGTH)
    logger.warn(msg)


    # Create the snapshot in the target region from the copied blob
    logger.warn("{0} - Creating snapshot in target region from the copied blob".format(location))
    target_blob_path = target_blob_endpoint + target_container_name + '/' + blob_name
    target_snapshot_name = source_os_disk_snapshot_name + '-' + location
    cmd = prepare_cli_command(['snapshot', 'create', \
        '--resource-group', transient_resource_group_name, \
        '--name', target_snapshot_name, \
        '--location', location, \
        '--source', target_blob_path])

    json_output = run_cli_command(cmd, return_as_json=True)
    target_snapshot_id = json_output['id']

    # Create the final image
    logger.warn("{0} - Creating final image".format(location))
    target_image_name = source_object_name
    if source_type != 'image':
        target_image_name += '-image'
    target_image_name += '-' + location

    cmd = prepare_cli_command(['image', 'create', \
        '--resource-group', target_resource_group_name, \
        '--name', target_image_name, \
        '--location', location, \
        '--source', target_blob_path, \
        '--os-type', source_os_type, \
        '--source', target_snapshot_id])

    run_cli_command(cmd)


def wait_for_blob_copy_operation(blob_name, target_container_name, target_storage_account_name, azure_pool_frequency, location):
    progress_controller = APPLICATION.get_progress_controller()
    copy_status = "pending"
    prev_progress = -1
    while copy_status == "pending":
        cmd = prepare_cli_command(['storage', 'blob', 'show', \
            '--name', blob_name, \
            '--container-name', target_container_name, \
            '--account-name', target_storage_account_name])

        json_output = run_cli_command(cmd, return_as_json=True)
        copy_status = json_output["properties"]["copy"]["status"]
        copy_progress_1, copy_progress_2 = json_output["properties"]["copy"]["progress"].split("/")
        current_progress = round(int(copy_progress_1)/int(copy_progress_2), 1)

        if current_progress != prev_progress:
            msg = "{0} - copy progress: {1}%"\
                .format(location, str(current_progress))\
                .ljust(PROGRESS_LINE_LENGTH) #need to justify since messages overide each other
            progress_controller.add(message=msg)

        prev_progress = current_progress

        try:
            time.sleep(azure_pool_frequency)
        except KeyboardInterrupt:
            progress_controller.stop()
            return


    if copy_status == 'success':
        progress_controller.stop()
    else:
        logger.error("The copy operation didn't succeed. Last status: %s", copy_status)
        raise CLIError('Blob copy failed')


def get_subscription_id():
    cmd = prepare_cli_command(['account', 'show'])
    json_output = run_cli_command(cmd, return_as_json=True)
    subscription_id = json_output['id']

    return subscription_id
