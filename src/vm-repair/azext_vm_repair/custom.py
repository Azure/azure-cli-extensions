# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals, too-many-statements, broad-except, too-many-branches
import json
import timeit
import traceback
import requests

from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from azure.cli.command_modules.storage.storage_url_helpers import StorageResourceIdentifier
from msrestazure.tools import parse_resource_id
from .exceptions import AzCommandError, SkuNotAvailableError, UnmanagedDiskCopyError, WindowsOsNotAvailableError, RunScriptNotFoundForIdError, SkuDoesNotSupportHyperV, ScriptReturnsError, SupportingResourceNotFoundError, CommandCanceledByUserError

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
    _fetch_disk_info,
    _unlock_singlepass_encrypted_disk,
    _invoke_run_command,
    _get_cloud_init_script,
    _select_distro_linux,
    _check_linux_hyperV_gen,
    _select_distro_linux_gen2,
    _set_repair_map_url,
    _is_gen2,
    _unlock_encrypted_vm_run,
    _create_repair_vm,
    _check_n_start_vm,
    _check_existing_rg,
    _fetch_architecture,
    _select_distro_linux_Arm64
)
from .exceptions import AzCommandError, RunScriptNotFoundForIdError, SupportingResourceNotFoundError, CommandCanceledByUserError
logger = get_logger(__name__)


def create(cmd, vm_name, resource_group_name, repair_password=None, repair_username=None, repair_vm_name=None, copy_disk_name=None, repair_group_name=None, unlock_encrypted_vm=False, enable_nested=False, associate_public_ip=False, distro='ubuntu', yes=False):

    # log all the parameters
    logger.debug('vm repair create command parameters: vm_name: %s, resource_group_name: %s, repair_password: %s, repair_username: %s, repair_vm_name: %s, copy_disk_name: %s, repair_group_name: %s, unlock_encrypted_vm: %s, enable_nested: %s, associate_public_ip: %s, distro: %s, yes: %s', vm_name, resource_group_name, repair_password, repair_username, repair_vm_name, copy_disk_name, repair_group_name, unlock_encrypted_vm, enable_nested, associate_public_ip, distro, yes)

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair create')
    # Main command calling block
    try:
        # Fetch source VM data
        source_vm = get_vm(cmd, resource_group_name, vm_name)
        source_vm_instance_view = get_vm(cmd, resource_group_name, vm_name, 'instanceView')

        is_linux = _is_linux_os(source_vm)
        vm_hypervgen = _is_gen2(source_vm_instance_view)

        target_disk_name = source_vm.storage_profile.os_disk.name
        is_managed = _uses_managed_disk(source_vm)
        copy_disk_id = None
        resource_tag = _get_repair_resource_tag(resource_group_name, vm_name)
        created_resources = []
        architecture_type = _fetch_architecture(source_vm)

        # Fetch OS image urn and set OS type for disk create
        if is_linux and _uses_managed_disk(source_vm):
            # os_image_urn = "UbuntuLTS"
            os_type = 'Linux'
            hyperV_generation_linux = _check_linux_hyperV_gen(source_vm)
            if hyperV_generation_linux == 'V2':
                logger.info('Generation 2 VM detected')
                os_image_urn = _select_distro_linux_gen2(distro)
            if architecture_type == 'Arm64':
                logger.info('ARM64 VM detected')
                os_image_urn = _select_distro_linux_Arm64(distro)
            else:
                os_image_urn = _select_distro_linux(distro)
        else:
            os_image_urn = _fetch_compatible_windows_os_urn(source_vm)
            os_type = 'Windows'

        # Set up base create vm command
        if is_linux:
            create_repair_vm_command = 'az vm create -g {g} -n {n} --tag {tag} --image {image} --admin-username {username} --admin-password {password} --public-ip-address {option} --custom-data {cloud_init_script}' \
                .format(g=repair_group_name, n=repair_vm_name, tag=resource_tag, image=os_image_urn, username=repair_username, password=repair_password, option=associate_public_ip, cloud_init_script=_get_cloud_init_script())
        else:
            create_repair_vm_command = 'az vm create -g {g} -n {n} --tag {tag} --image {image} --admin-username {username} --admin-password {password} --public-ip-address {option}' \
                .format(g=repair_group_name, n=repair_vm_name, tag=resource_tag, image=os_image_urn, username=repair_username, password=repair_password, option=associate_public_ip)

        # Fetch VM size of repair VM
        sku = _fetch_compatible_sku(source_vm, enable_nested)
        if not sku:
            raise SkuNotAvailableError('Failed to find compatible VM size for source VM\'s OS disk within given region and subscription.')
        create_repair_vm_command += ' --size {sku}'.format(sku=sku)

        # Set availability zone for vm
        if source_vm.zones:
            zone = source_vm.zones[0]
            create_repair_vm_command += ' --zone {zone}'.format(zone=zone)

        # Create new resource group
        existing_rg = _check_existing_rg(repair_group_name)
        if not existing_rg:
            create_resource_group_command = 'az group create -l {loc} -n {group_name}' \
                                            .format(loc=source_vm.location, group_name=repair_group_name)
            logger.info('Creating resource group for repair VM and its resources...')
            _call_az_command(create_resource_group_command)

        # MANAGED DISK
        if is_managed:
            logger.info('Source VM uses managed disks. Creating repair VM with managed disks.\n')

            # Copy OS disk command
            disk_sku, location, os_type, hyperV_generation = _fetch_disk_info(resource_group_name, target_disk_name)
            copy_disk_command = 'az disk create -g {g} -n {n} --source {s} --sku {sku} --location {loc} --os-type {os_type} --query id -o tsv' \
                                .format(g=resource_group_name, n=copy_disk_name, s=target_disk_name, sku=disk_sku, loc=location, os_type=os_type)

            # Only add hyperV variable when available
            if hyperV_generation:
                copy_disk_command += ' --hyper-v-generation {hyperV}'.format(hyperV=hyperV_generation)
            elif is_linux and hyperV_generation_linux == 'V2':
                logger.info('The disk did not contain the information of gen2 , but the machine is created from gen2 image')
                copy_disk_command += ' --hyper-v-generation {hyperV}'.format(hyperV=hyperV_generation_linux)
            # Set availability zone for vm when available
            if source_vm.zones:
                zone = source_vm.zones[0]
                copy_disk_command += ' --zone {zone}'.format(zone=zone)
            # Copy OS Disk
            logger.info('Copying OS disk of source VM...')
            copy_disk_id = _call_az_command(copy_disk_command).strip('\n')

            # Create VM according to the two conditions: is_linux, unlock_encrypted_vm
            # Only in the case of a Linux VM without encryption the data-disk gets attached after VM creation.
            # This is required to prevent an incorrect boot due to an UUID mismatch
            if not is_linux:
                # windows
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)

            if not is_linux and unlock_encrypted_vm:
                # windows with encryption
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)
                _unlock_encrypted_vm_run(repair_vm_name, repair_group_name, is_linux)

            if is_linux and unlock_encrypted_vm:
                # linux with encryption
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)
                _unlock_encrypted_vm_run(repair_vm_name, repair_group_name, is_linux)

            if is_linux and (not unlock_encrypted_vm):
                # linux without encryption
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username, fix_uuid=True)
                logger.info('Attaching copied disk to repair VM as data disk...')
                attach_disk_command = "az vm disk attach -g {g} --name {disk_id} --vm-name {vm_name} ".format(g=repair_group_name, disk_id=copy_disk_id, vm_name=repair_vm_name)
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

        # invoke enable-NestedHyperV.ps1 again to attach Disk to Nested
        if enable_nested:
            logger.info("Running Script win-enable-nested-hyperv.ps1 to install HyperV")

            run_hyperv_command = "az vm repair run -g {g} -n {name} --run-id win-enable-nested-hyperv --parameters gen={gen}" \
                .format(g=repair_group_name, name=repair_vm_name, gen=vm_hypervgen)
            ret_enable_nested = _call_az_command(run_hyperv_command)

            logger.debug("az vm repair run hyperv command returned: %s", ret_enable_nested)

            if str.find(ret_enable_nested, "SuccessRestartRequired") > -1:
                restart_cmd = 'az vm restart -g {rg} -n {vm}'.format(rg=repair_group_name, vm=repair_vm_name)
                logger.info("Restarting Repair VM")
                restart_ret = _call_az_command(restart_cmd)
                logger.debug(restart_ret)

                # invoking hyperv script again
                logger.info("Running win-enable-nested-hyperv.ps1 again to create nested VM")
                run_hyperv_command = "az vm repair run -g {g} -n {name} --run-id win-enable-nested-hyperv --parameters gen={gen}" \
                    .format(g=repair_group_name, name=repair_vm_name, gen=vm_hypervgen)
                ret_enable_nested_again = _call_az_command(run_hyperv_command)

                logger.debug("stderr: %s", ret_enable_nested_again)

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
    except SkuDoesNotSupportHyperV as skuDoesNotSupportHyperV:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(skuDoesNotSupportHyperV)
        command.message = "v2 sku does not support nested VM in hyperv. Please run command without --enabled-nested."
    except ScriptReturnsError as scriptReturnsError:
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(scriptReturnsError)
        command.message = "Error returned from script when enabling hyperv."
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
        if existing_rg:
            _clean_up_resources(repair_group_name, confirm=True)
        else:
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
        if repair_vm_id:
            logger.info('Repair VM ID: %s', repair_vm_id)
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


def run(cmd, vm_name, resource_group_name, run_id=None, repair_vm_id=None, custom_script_file=None, parameters=None, run_on_repair=False, preview=None):

    # log method parameters
    logger.debug('vm repair run parameters: vm_name: %s, resource_group_name: %s, run_id: %s, repair_vm_id: %s, custom_script_file: %s, parameters: %s, run_on_repair: %s, preview: %s',
                 vm_name, resource_group_name, run_id, repair_vm_id, custom_script_file, parameters, run_on_repair, preview)

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair run')
    LINUX_RUN_SCRIPT_NAME = 'linux-run-driver.sh'
    WINDOWS_RUN_SCRIPT_NAME = 'win-run-driver.ps1'
    if preview:
        _set_repair_map_url(preview)

    try:
        # Fetch VM data
        source_vm = get_vm(cmd, resource_group_name, vm_name)
        is_linux = _is_linux_os(source_vm)

        if is_linux:
            script_name = LINUX_RUN_SCRIPT_NAME
        else:
            script_name = WINDOWS_RUN_SCRIPT_NAME

        # If run_on_repair is False, then repair_vm is the source_vm (scripts run directly on source vm)
        if run_on_repair:
            repair_vm_id = parse_resource_id(repair_vm_id)
            repair_vm_name = repair_vm_id['name']
            repair_resource_group = repair_vm_id['resource_group']
        else:
            repair_vm_name = vm_name
            repair_resource_group = resource_group_name

        run_command_params = []
        additional_scripts = []

        # Normal scenario with run id
        if not custom_script_file:
            # Fetch run path from GitHub
            repair_script_path = _fetch_run_script_path(run_id)
            run_command_params.append('script_path="./{}"'.format(repair_script_path))
        # Custom script scenario for script testers
        else:
            run_command_params.append('script_path=no-op')
            additional_scripts.append(custom_script_file)

        if preview:
            parts = preview.split('/')
            if len(parts) < 7 or parts.index('map.json') == -1:
                raise Exception('Invalid preview url. Write full URL of map.json file. example https://github.com/Azure/repair-script-library/blob/main/map.json')
            last_index = parts.index('map.json')
            fork_name = parts[last_index - 4]
            branch_name = parts[last_index - 1]
            run_command_params.append('repo_fork="{}"'.format(fork_name))
            run_command_params.append('repo_branch="{}"'.format(branch_name))

        # Append Parameters
        if parameters:
            if is_linux:
                param_string = _process_bash_parameters(parameters)
            else:
                param_string = _process_ps_parameters(parameters)
            run_command_params.append('params="{}"'.format(param_string))
        if run_on_repair:
            vm_string = 'repair VM'
        else:
            vm_string = 'VM'
        logger.info('Running script on %s: %s', vm_string, repair_vm_name)

        # Run script and measure script run-time
        script_start_time = timeit.default_timer()
        stdout, stderr = _invoke_run_command(script_name, repair_vm_name, repair_resource_group, is_linux, run_command_params, additional_scripts)
        command.script.run_time = timeit.default_timer() - script_start_time
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
        return_dict['err'] = stderr
        return_dict['log_full_path'] = log_fullpath
        return_dict['output'] = command.script.output
        return_dict['vm_name'] = repair_vm_name
        return_dict['resource_group'] = repair_resource_group

    return return_dict


def list_scripts(cmd, preview=None):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair list-scripts')
    if preview:
        _set_repair_map_url(preview)

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


def reset_nic(cmd, vm_name, resource_group_name, yes=False):

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair reset-nic')
    DYNAMIC_CONFIG = 'Dynamic'

    try:
        # 0) Check if VM is deallocated or off. If it is, ask to run start the VM.
        VM_OFF_MESSAGE = 'VM is not running. The VM must be in running to reset its NIC.\n'

        vm_instance_view = get_vm(cmd, resource_group_name, vm_name, 'instanceView')
        VM_started = _check_n_start_vm(vm_name, resource_group_name, not yes, VM_OFF_MESSAGE, vm_instance_view)
        if not VM_started:
            raise CommandCanceledByUserError("Could not get consent to run VM before resetting the NIC.")

        # 1) Fetch vm network info
        logger.info('Fetching necessary VM network information to reset the NIC...\n')
        # Fetch primary nic id. The primary field is null or true for primary nics.
        get_primary_nic_id_command = 'az vm nic list -g {g} --vm-name {n} --query "[[?primary].id || [?primary==null].id][0][0]" -o tsv' \
                                     .format(g=resource_group_name, n=vm_name)
        primary_nic_id = _call_az_command(get_primary_nic_id_command)
        if not primary_nic_id:
            # Raise no primary nic excpetion
            raise SupportingResourceNotFoundError('The primary NIC for the VM was not found on Azure.')
        primary_nic_name = primary_nic_id.split('/')[-1]

        # Get ip config info to get: vnet name, current private ip, ipconfig name, subnet id
        get_primary_ip_config = 'az network nic ip-config list -g {g} --nic-name {nic_name} --query [[?primary]][0][0]' \
                                .format(g=resource_group_name, nic_name=primary_nic_name)
        ip_config_string = _call_az_command(get_primary_ip_config)
        if not ip_config_string:
            # Raise primary ip_config not found
            raise SupportingResourceNotFoundError('The primary IP configuration for the VM NIC was not found on Azure.')
        ip_config_object = json.loads(ip_config_string)

        subnet_id = ip_config_object['subnet']['id']
        subnet_id_tokens = subnet_id.split('/')
        subnet_name = subnet_id_tokens[-1]
        vnet_name = subnet_id_tokens[-3]
        vnet_resource_group = subnet_id_tokens[-7]
        ipconfig_name = ip_config_object['name']
        orig_ip_address = ip_config_object['privateIPAddress']
        # Dynamic | Static
        orig_ip_allocation_method = ip_config_object['privateIPAllocationMethod']

        # Get aviailable ip address within subnet
        get_available_ip_command = 'az network vnet subnet list-available-ips -g {g} --vnet-name {vnet} --name {subnet} --query [0] -o tsv' \
                                   .format(g=vnet_resource_group, vnet=vnet_name, subnet=subnet_name)
        swap_ip_address = _call_az_command(get_available_ip_command)
        if not swap_ip_address:
            # Raise available IP not found
            raise SupportingResourceNotFoundError('Available IP address was not found within the VM subnet.')

        # 3) Update private IP address to another in subnet. This will invoke and wait for a VM restart.
        logger.info('Updating VM IP configuration. This might take a few minutes...\n')
        # Update IP address
        update_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip} ' \
                            .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=swap_ip_address)
        _call_az_command(update_ip_command)

        # 4) Change things back. This will also invoke and wait for a VM restart.
        logger.info('NIC reset is complete. Now reverting back to your original configuration...\n')
        # If user had dynamic config, change back to dynamic
        revert_ip_command = None
        if orig_ip_allocation_method == DYNAMIC_CONFIG:
            # Revert Static to Dynamic
            revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --set privateIpAllocationMethod={method}' \
                                .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, method=DYNAMIC_CONFIG)
        else:
            # Revert to original static ip
            revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip} ' \
                                .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=orig_ip_address)

        _call_az_command(revert_ip_command)
        logger.info('VM guest NIC reset is complete and all configurations are reverted.')
    # Some error happened. Stop command and revert back as needed.
    except KeyboardInterrupt:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command interrupted by user input."
        command.message = "Command interrupted by user input."
    except AzCommandError as azCommandError:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(azCommandError)
        command.message = "Reset NIC failed."
    except SupportingResourceNotFoundError as resourceError:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(resourceError)
        command.message = "Reset NIC could not be initiated."
    except CommandCanceledByUserError as canceledError:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(canceledError)
        command.message = VM_OFF_MESSAGE
    except Exception as exception:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = str(exception)
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'
    else:
        command.set_status_success()
        command.message = 'VM guest NIC reset complete. The VM is in running state.'
    finally:
        if command.error_stack_trace:
            logger.debug(command.error_stack_trace)
        # Generate return object and log errors if needed
        return_dict = command.init_return_dict()

    return return_dict


def repair_and_restore(cmd, vm_name, resource_group_name, repair_password=None, repair_username=None, repair_vm_name=None, copy_disk_name=None, repair_group_name=None):
    from datetime import datetime
    import secrets
    import string

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair repair-and-restore')

    password_length = 30
    password_characters = string.ascii_lowercase + string.digits + string.ascii_uppercase
    repair_password = ''.join(secrets.choice(password_characters) for i in range(password_length))

    username_length = 20
    username_characters = string.ascii_lowercase + string.digits
    repair_username = ''.join(secrets.choice(username_characters) for i in range(username_length))

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    repair_vm_name = ('repair-' + vm_name)[:14] + '_'
    copy_disk_name = vm_name + '-DiskCopy-' + timestamp
    repair_group_name = 'repair-' + vm_name + '-' + timestamp
    existing_rg = _check_existing_rg(repair_group_name)

    create_out = create(cmd, vm_name, resource_group_name, repair_password, repair_username, repair_vm_name=repair_vm_name, copy_disk_name=copy_disk_name, repair_group_name=repair_group_name, associate_public_ip=False, yes=True)

    # log create_out
    logger.info('create_out: %s', create_out)

    repair_vm_name = create_out['repair_vm_name']
    copy_disk_name = create_out['copied_disk_name']
    repair_group_name = create_out['repair_resource_group']

    logger.info('Running fstab run command')

    try:
        run_out = run(cmd, repair_vm_name, repair_group_name, run_id='linux-alar2', parameters=["fstab"])

    except Exception:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command failed when running fstab script."
        command.message = "Command failed when running fstab script."
        if existing_rg:
            _clean_up_resources(repair_group_name, confirm=True)
        else:
            _clean_up_resources(repair_group_name, confirm=False)
        return

    # log run_out
    logger.info('run_out: %s', run_out)

    if run_out['script_status'] == 'ERROR':
        logger.error('fstab script returned an error.')
        if existing_rg:
            _clean_up_resources(repair_group_name, confirm=True)
        else:
            _clean_up_resources(repair_group_name, confirm=False)
        return

    logger.info('Running restore command')
    show_vm_id = 'az vm show -g {g} -n {n} --query id -o tsv' \
        .format(g=repair_group_name, n=repair_vm_name)

    repair_vm_id = _call_az_command(show_vm_id)

    restore(cmd, vm_name, resource_group_name, copy_disk_name, repair_vm_id, yes=True)

    command.message = 'fstab script has been applied to the source VM. A new repair VM \'{n}\' was created in the resource group \'{repair_rg}\' with disk \'{d}\' attached as data disk. ' \
        'The repairs were complete using the fstab script and the repair VM was then deleted. ' \
        'The repair disk was restored to the source VM. ' \
        .format(n=repair_vm_name, repair_rg=repair_group_name, d=copy_disk_name)

    command.set_status_success()
    if command.error_stack_trace:
        logger.debug(command.error_stack_trace)
    # Generate return object and log errors if needed
    return_dict = command.init_return_dict()

    logger.info('\n%s\n', command.message)

    return return_dict
