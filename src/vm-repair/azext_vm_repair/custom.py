# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals, too-many-statements, broad-except, too-many-branches
import json
import timeit
import os
import pkgutil
import traceback
import requests
from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from azure.cli.command_modules.storage.storage_url_helpers import StorageResourceIdentifier
from msrestazure.tools import parse_resource_id

from .command_helper_class import command_helper
from .repair_utils import (
    _uses_managed_disk,
    _call_az_command,
    _clean_up_resources,
    _fetch_compatible_sku,
    _list_resource_ids_in_rg,
    _get_repair_resource_tag,
    _fetch_compatible_windows_os_urn,
    _fetch_run_script_map,
    _fetch_run_script_path,
    _process_ps_parameters,
    _process_bash_parameters,
    _parse_run_script_raw_logs,
    _check_script_succeeded,
    _fetch_disk_info
)
from .exceptions import AzCommandError, SkuNotAvailableError, UnmanagedDiskCopyError, WindowsOsNotAvailableError, RunScriptNotFoundForIdError

logger = get_logger(__name__)


def create(cmd, vm_name, resource_group_name, repair_password=None, repair_username=None, repair_vm_name=None, copy_disk_name=None, repair_group_name=None):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair create')

    # Main command calling block
    try:
        # Fetch source VM data
        source_vm = get_vm(cmd, resource_group_name, vm_name)
        is_linux = _is_linux_os(source_vm)
        target_disk_name = source_vm.storage_profile.os_disk.name
        is_managed = _uses_managed_disk(source_vm)
        copy_disk_id = None
        resource_tag = _get_repair_resource_tag(resource_group_name, vm_name)

        # List of created resouces
        created_resources = []

        # Fetch OS image urn and set OS type for disk create
        if is_linux:
            os_image_urn = "UbuntuLTS"
            os_type = 'Linux'
        else:
            os_image_urn = _fetch_compatible_windows_os_urn(source_vm)
            os_type = 'Windows'

        # Set up base create vm command
        create_repair_vm_command = 'az vm create -g {g} -n {n} --tag {tag} --image {image} --admin-username {username} --admin-password {password}' \
                                   .format(g=repair_group_name, n=repair_vm_name, tag=resource_tag, image=os_image_urn, username=repair_username, password=repair_password)
        # fetch VM size of repair VM
        sku = _fetch_compatible_sku(source_vm)
        if not sku:
            raise SkuNotAvailableError('Failed to find compatible VM size for source VM\'s OS disk within given region and subscription.')
        create_repair_vm_command += ' --size {sku}'.format(sku=sku)

        # Create new resource group
        create_resource_group_command = 'az group create -l {loc} -n {group_name}' \
                                        .format(loc=source_vm.location, group_name=repair_group_name)
        logger.info('Creating resource group for repair VM and its resources...')
        _call_az_command(create_resource_group_command)

        # MANAGED DISK
        if is_managed:
            logger.info('Source VM uses managed disks. Creating repair VM with managed disks.\n')

            # Copy OS disk command
            disk_sku, location, os_type, hyperV_generation = _fetch_disk_info(resource_group_name, target_disk_name)
            copy_disk_command = 'az disk create -g {g} -n {n} --source {s} --sku {sku} --location {loc} --os-type {os_type} --hyper-v-generation {hyperV} --query id -o tsv' \
                                .format(g=resource_group_name, n=copy_disk_name, s=target_disk_name, sku=disk_sku, loc=location, os_type=os_type, hyperV=hyperV_generation)
            # Validate create vm create command to validate parameters before runnning copy disk command
            validate_create_vm_command = create_repair_vm_command + ' --validate'

            logger.info('Validating VM template before continuing...')
            _call_az_command(validate_create_vm_command, secure_params=[repair_password, repair_username])
            logger.info('Copying OS disk of source VM...')
            copy_disk_id = _call_az_command(copy_disk_command).strip('\n')

            attach_disk_command = 'az vm disk attach -g {g} --vm-name {repair} --name {id}' \
                                  .format(g=repair_group_name, repair=repair_vm_name, id=copy_disk_id)

            logger.info('Creating repair VM...')
            _call_az_command(create_repair_vm_command, secure_params=[repair_password, repair_username])
            logger.info('Attaching copied disk to repair VM...')
            _call_az_command(attach_disk_command)
        # UNMANAGED DISK
        else:
            logger.info('Source VM uses unmanaged disks. Creating repair VM with unmanaged disks.\n')
            os_disk_uri = source_vm.storage_profile.os_disk.vhd.uri
            copy_disk_name = copy_disk_name + '.vhd'
            storage_account = StorageResourceIdentifier(cmd.cli_ctx.cloud, os_disk_uri)
            # Validate create vm create command to validate parameters before runnning copy disk commands
            validate_create_vm_command = create_repair_vm_command + ' --validate'
            logger.info('Validating VM template before continuing...')
            _call_az_command(validate_create_vm_command, secure_params=[repair_password, repair_username])

            # get storage account connection string
            get_connection_string_command = 'az storage account show-connection-string -g {g} -n {n} --query connectionString -o tsv' \
                                            .format(g=resource_group_name, n=storage_account.account_name)
            logger.debug('Fetching storage account connection string...')
            connection_string = _call_az_command(get_connection_string_command).strip('\n')

            # Create Snapshot of Unmanaged Disk
            make_snapshot_command = 'az storage blob snapshot -c {c} -n {n} --connection-string "{con_string}" --query snapshot -o tsv' \
                                    .format(c=storage_account.container, n=storage_account.blob, con_string=connection_string)
            logger.info('Creating snapshot of OS disk...')
            snapshot_timestamp = _call_az_command(make_snapshot_command, secure_params=[connection_string]).strip('\n')
            snapshot_uri = os_disk_uri + '?snapshot={timestamp}'.format(timestamp=snapshot_timestamp)

            # Copy Snapshot into unmanaged Disk
            copy_snapshot_command = 'az storage blob copy start -c {c} -b {name} --source-uri {source} --connection-string "{con_string}"' \
                                    .format(c=storage_account.container, name=copy_disk_name, source=snapshot_uri, con_string=connection_string)
            logger.info('Creating a copy disk from the snapshot...')
            _call_az_command(copy_snapshot_command, secure_params=[connection_string])
            # Generate the copied disk uri
            copy_disk_id = os_disk_uri.rstrip(storage_account.blob) + copy_disk_name

            # Create new repair VM with copied ummanaged disk command
            create_repair_vm_command = create_repair_vm_command + ' --use-unmanaged-disk'
            logger.info('Creating repair VM while disk copy is in progress...')
            _call_az_command(create_repair_vm_command, secure_params=[repair_password, repair_username])

            logger.info('Checking if disk copy is done...')
            copy_check_command = 'az storage blob show -c {c} -n {name} --connection-string "{con_string}" --query properties.copy.status -o tsv' \
                                 .format(c=storage_account.container, name=copy_disk_name, con_string=connection_string)
            copy_result = _call_az_command(copy_check_command, secure_params=[connection_string]).strip('\n')
            if copy_result != 'success':
                raise UnmanagedDiskCopyError('Unmanaged disk copy failed.')

            # Attach copied unmanaged disk to new vm
            logger.info('Attaching copied disk to repair VM as data disk...')
            attach_disk_command = "az vm unmanaged-disk attach -g {g} -n {disk_name} --vm-name {vm_name} --vhd-uri {uri}" \
                                  .format(g=repair_group_name, disk_name=copy_disk_name, vm_name=repair_vm_name, uri=copy_disk_id)
            _call_az_command(attach_disk_command)

        created_resources = _list_resource_ids_in_rg(repair_group_name)
        command.set_status_success()

    # Some error happened. Stop command and clean-up resources.
    except KeyboardInterrupt:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command interrupted by user input."
        command.message = "Command interrupted by user input. Cleaning up resources."
    except AzCommandError as azCommandError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(azCommandError)
        command.message = "Repair create failed. Cleaning up created resources."
    except SkuNotAvailableError as skuNotAvailableError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(skuNotAvailableError)
        command.message = "Please check if the current subscription can create more VM resources. Cleaning up created resources."
    except UnmanagedDiskCopyError as unmanagedDiskCopyError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(unmanagedDiskCopyError)
        command.message = "Repair create failed. Please try again at another time. Cleaning up created resources."
    except WindowsOsNotAvailableError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = 'Compatible Windows OS image not available.'
        command.message = 'A compatible Windows OS image is not available at this time, please check subscription.'
    except Exception as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'
    finally:
        if command.error_stack_trace:
            logger.debug(command.error_stack_trace)

    # Generate return results depending on command state
    if not command.is_status_success():
        command.set_status_error()
        return_dict = command.init_return_dict()
        _clean_up_resources(repair_group_name, confirm=False)
    else:
        created_resources.append(copy_disk_id)
        command.message = 'Your repair VM \'{n}\' has been created in the resource group \'{repair_rg}\' with disk \'{d}\' attached as data disk. ' \
                          'Please use this VM to troubleshoot and repair. Once the repairs are complete use the command ' \
                          '\'az vm repair restore -n {source_vm} -g {rg} --verbose\' to restore disk to the source VM. ' \
                          'Note that the copied disk is created within the original resource group \'{rg}\'.' \
                          .format(n=repair_vm_name, repair_rg=repair_group_name, d=copy_disk_name, rg=resource_group_name, source_vm=vm_name)
        return_dict = command.init_return_dict()
        # Add additional custom return properties
        return_dict['repair_vm_name'] = repair_vm_name
        return_dict['copied_disk_name'] = copy_disk_name
        return_dict['copied_disk_uri'] = copy_disk_id
        return_dict['repair_resource_group'] = repair_group_name
        return_dict['resource_tag'] = resource_tag
        return_dict['created_resources'] = created_resources

        logger.info('\n%s\n', command.message)

    return return_dict


def restore(cmd, vm_name, resource_group_name, disk_name=None, repair_vm_id=None, yes=False):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair restore')

    try:
        # Fetch source and repair VM data
        source_vm = get_vm(cmd, resource_group_name, vm_name)
        is_managed = _uses_managed_disk(source_vm)
        repair_vm_id = parse_resource_id(repair_vm_id)
        repair_vm_name = repair_vm_id['name']
        repair_resource_group = repair_vm_id['resource_group']
        source_disk = None

        # MANAGED DISK
        if is_managed:
            source_disk = source_vm.storage_profile.os_disk.name
            # Detach repaired data disk command
            detach_disk_command = 'az vm disk detach -g {g} --vm-name {repair} --name {disk}' \
                                  .format(g=repair_resource_group, repair=repair_vm_name, disk=disk_name)
            # Update OS disk with repaired data disk
            attach_fixed_command = 'az vm update -g {g} -n {n} --os-disk {disk}' \
                                   .format(g=resource_group_name, n=vm_name, disk=disk_name)

            # Maybe run attach and delete concurrently
            logger.info('Detaching repaired data disk from repair VM...')
            _call_az_command(detach_disk_command)
            logger.info('Attaching repaired data disk to source VM as an OS disk...')
            _call_az_command(attach_fixed_command)
        # UNMANAGED DISK
        else:
            source_disk = source_vm.storage_profile.os_disk.vhd.uri
            # Get disk uri from disk name
            repair_vm = get_vm(cmd, repair_vm_id['resource_group'], repair_vm_id['name'])
            data_disks = repair_vm.storage_profile.data_disks
            # The params went through validator so no need for existence checks
            disk_uri = [disk.vhd.uri for disk in data_disks if disk.name == disk_name][0]

            detach_unamanged_command = 'az vm unmanaged-disk detach -g {g} --vm-name {repair} --name {disk}' \
                                       .format(g=repair_resource_group, repair=repair_vm_name, disk=disk_name)
            # Update OS disk with disk
            # storageProfile.osDisk.name="{disk}"
            attach_unmanaged_command = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"' \
                                       .format(g=resource_group_name, n=vm_name, uri=disk_uri)
            logger.info('Detaching repaired data disk from repair VM...')
            _call_az_command(detach_unamanged_command)
            logger.info('Attaching repaired data disk to source VM as an OS disk...')
            _call_az_command(attach_unmanaged_command)
        # Clean
        _clean_up_resources(repair_resource_group, confirm=not yes)
        command.set_status_success()
    except KeyboardInterrupt:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command interrupted by user input."
        command.message = "Command interrupted by user input. If the restore command fails at retry, please rerun the repair process from \'az vm repair create\'."
    except AzCommandError as azCommandError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(azCommandError)
        command.message = "Repair restore failed. If the restore command fails at retry, please rerun the repair process from \'az vm repair create\'."
    except Exception as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'
    finally:
        if command.error_stack_trace:
            logger.debug(command.error_stack_trace)

    if not command.is_status_success():
        command.set_status_error()
        return_dict = command.init_return_dict()
    else:
        # Construct return dict
        command.message = '\'{disk}\' successfully attached to \'{n}\' as an OS disk. Please test your repairs and once confirmed, ' \
                          'you may choose to delete the source OS disk \'{src_disk}\' within resource group \'{rg}\' manually if you no longer need it, to avoid any undesired costs.' \
                          .format(disk=disk_name, n=vm_name, src_disk=source_disk, rg=resource_group_name)
        return_dict = command.init_return_dict()
        logger.info('\n%s\n', return_dict['message'])

    return return_dict


def run(cmd, vm_name, resource_group_name, run_id=None, repair_vm_id=None, custom_script_file=None, parameters=None, run_on_repair=False):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair run')

    REPAIR_DIR_NAME = 'azext_vm_repair'
    SCRIPTS_DIR_NAME = 'scripts'
    LINUX_RUN_SCRIPT_NAME = 'linux-run-driver.sh'
    WINDOWS_RUN_SCRIPT_NAME = 'win-run-driver.ps1'
    RUN_COMMAND_RUN_SHELL_ID = 'RunShellScript'
    RUN_COMMAND_RUN_PS_ID = 'RunPowerShellScript'

    try:
        # Fetch VM data
        source_vm = get_vm(cmd, resource_group_name, vm_name)

        # Build absoulte path of driver script
        loader = pkgutil.get_loader(REPAIR_DIR_NAME)
        mod = loader.load_module(REPAIR_DIR_NAME)
        rootpath = os.path.dirname(mod.__file__)
        is_linux = _is_linux_os(source_vm)
        if is_linux:
            run_script = os.path.join(rootpath, SCRIPTS_DIR_NAME, LINUX_RUN_SCRIPT_NAME)
            command_id = RUN_COMMAND_RUN_SHELL_ID
        else:
            run_script = os.path.join(rootpath, SCRIPTS_DIR_NAME, WINDOWS_RUN_SCRIPT_NAME)
            command_id = RUN_COMMAND_RUN_PS_ID

        # If run_on_repair is False, then repair_vm is the source_vm (scripts run directly on source vm)
        repair_vm_id = parse_resource_id(repair_vm_id)
        repair_vm_name = repair_vm_id['name']
        repair_resource_group = repair_vm_id['resource_group']

        repair_run_command = 'az vm run-command invoke -g {rg} -n {vm} --command-id {command_id} ' \
                             '--scripts "@{run_script}" -o json' \
                             .format(rg=repair_resource_group, vm=repair_vm_name, command_id=command_id, run_script=run_script)

        # Normal scenario with run id
        if not custom_script_file:
            # Fetch run path from GitHub
            repair_script_path = _fetch_run_script_path(run_id)
            repair_run_command += ' --parameters script_path="./{repair_script}"'.format(repair_script=repair_script_path)
        # Custom script scenario for script testers
        else:
            # no-op run id
            repair_run_command += ' "@{custom_file}" --parameters script_path=no-op'.format(custom_file=custom_script_file)

        # Append Parameters
        if parameters:
            if is_linux:
                param_string = _process_bash_parameters(parameters)
            else:
                param_string = _process_ps_parameters(parameters)
            # Work around for run-command bug, unexpected behavior with space characters
            param_string = param_string.replace(' ', '%20')
            repair_run_command += ' params="{}"'.format(param_string)
        if run_on_repair:
            vm_string = 'repair VM'
        else:
            vm_string = 'VM'
        logger.info('Running script on %s: %s', vm_string, repair_vm_name)

        # Run script and measure script run-time
        script_start_time = timeit.default_timer()
        return_str = _call_az_command(repair_run_command)
        command.script.run_time = timeit.default_timer() - script_start_time

        # Extract stdout and stderr, if stderr exists then possible error
        run_command_return = json.loads(return_str)
        if is_linux:
            run_command_message = run_command_return['value'][0]['message'].split('[stdout]')[1].split('[stderr]')
            stdout = run_command_message[0].strip('\n')
            stderr = run_command_message[1].strip('\n')
        else:
            stdout = run_command_return['value'][0]['message']
            stderr = run_command_return['value'][1]['message']
        logger.debug("stderr: %s", stderr)

        # Parse through stdout to populate log properties: 'level', 'message'
        run_script_succeeded = _check_script_succeeded(stdout)
        logs = _parse_run_script_raw_logs(stdout)

        # Process log-start and log-end
        # Log is cutoff at the start if over 4k bytes
        log_cutoff = True
        log_fullpath = ''
        for log in logs:
            if log['level'] == 'Log-Start':
                log_cutoff = False
            if log['level'] == 'Log-End':
                split_log = log['message'].split(']')
                if len(split_log) == 2:
                    log_fullpath = split_log[1]
        if log_cutoff:
            logger.warning('Log file is too large and has been cutoff at the start of file. Please locate the log file within the %s using the logFullpath to check full logs.', vm_string)

        # Output 'output' or 'error' level logs depending on status
        if run_script_succeeded:
            command.script.set_status_success()
            command.message = 'Script completed succesfully.'
            command.script.output = '\n'.join([log['message'] for log in logs if log['level'].lower() == 'output'])
            logger.info('\nScript returned with output:\n%s\n', command.script.output)
        else:
            command.script.set_status_error()
            command.message = 'Script completed with errors.'
            command.script.output = '\n'.join([log['message'] for log in logs if log['level'].lower() == 'error'])
            logger.error('\nScript returned with error:\n%s\n', command.script.output)

        command.set_status_success()
    except KeyboardInterrupt:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command interrupted by user input."
        command.message = "Repair run failed. Command interrupted by user input."
    except AzCommandError as azCommandError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(azCommandError)
        command.message = "Repair run failed."
    except requests.exceptions.RequestException as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = "Failed to fetch run script data from GitHub. Please check this repository is reachable: https://github.com/Azure/repair-script-library"
    except RunScriptNotFoundForIdError as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = "Repair run failed. Run ID not found."
    except Exception as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'
    finally:
        if command.error_stack_trace:
            logger.debug(command.error_stack_trace)

    if not command.is_status_success():
        command.set_status_error()
        command.script.output = 'Repair run failed.'
        return_dict = command.init_return_dict()
    else:
        # Build return Dict
        return_dict = command.init_return_dict()
        return_dict['script_status'] = command.script.status
        return_dict['logs'] = stdout
        return_dict['log_full_path'] = log_fullpath
        return_dict['output'] = command.script.output
        return_dict['vm_name'] = repair_vm_name
        return_dict['resource_group'] = repair_resource_group

    return return_dict


def list_scripts(cmd):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair list-scripts')

    try:
        run_map = _fetch_run_script_map()
        command.set_status_success()
    except requests.exceptions.RequestException as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = "Failed to fetch run script data from GitHub. Please check this repository is reachable: https://github.com/Azure/repair-script-library"
    except Exception as exception:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'
    finally:
        if command.error_stack_trace:
            logger.debug(command.error_stack_trace)

    if not command.is_status_success():
        command.set_status_error()
        return_dict = command.init_return_dict()
    else:
        command.message = 'Available script list succesfully fetched from https://github.com/Azure/repair-script-library'
        return_dict = command.init_return_dict()
        return_dict['map'] = run_map

    return return_dict
