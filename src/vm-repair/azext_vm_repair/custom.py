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
from azure.mgmt.core.tools import parse_resource_id
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
    _fetch_compatible_windows_os_urn_v2,
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
    _select_distro_linux_Arm64,
    _fetch_vm_security_profile_parameters,
    _fetch_osdisk_security_profile_parameters,
    _fetch_compatible_windows_os_urn_v2,
    _make_public_ip_name
)
from .exceptions import AzCommandError, RunScriptNotFoundForIdError, SupportingResourceNotFoundError, CommandCanceledByUserError
logger = get_logger(__name__)


def create(cmd, vm_name, resource_group_name, repair_password=None, repair_username=None, repair_vm_name=None, copy_disk_name=None, repair_group_name=None, unlock_encrypted_vm=False, enable_nested=False, associate_public_ip=False, distro='ubuntu', yes=False, encrypt_recovery_key="", disable_trusted_launch=False, os_disk_type=None):  
    """  
    This function creates a repair VM.  
      
    Parameters:  
    - cmd: The command to be executed.  
    - vm_name: The name of the virtual machine.  
    - resource_group_name: The name of the resource group.  
    - repair_password: The password for the repair VM. If not provided, a default will be used.  
    - repair_username: The username for the repair VM. If not provided, a default will be used.  
    - repair_vm_name: The name of the repair VM. If not provided, a default will be used.  
    - copy_disk_name: The name of the disk to be copied. If not provided, the OS disk of the source VM will be used.  
    - repair_group_name: The name of the repair group. If not provided, a default will be used.  
    - unlock_encrypted_vm: If True, the encrypted VM will be unlocked. Default is False.  
    - enable_nested: If True, nested virtualization will be enabled. Default is False.  
    - associate_public_ip: If True, a public IP will be associated with the VM. Default is False.  
    - distro: The Linux distribution to use for the repair VM. Default is 'ubuntu'.  
    - yes: If True, confirmation prompts will be skipped. Default is False.  
    - encrypt_recovery_key: The Bitlocker recovery key to use for encrypting the VM. Default is an empty string.  
    - disable_trusted_launch: A flag parameter that, when used, sets the security type of the repair VM to Standard.
    - os_disk_type: Set the OS disk storage account type of the repair VM to the specified type. The default is PremiumSSD_LRS. 
    """  
    
    # Logging all the command parameters, except the sensitive data.
    # Mask sensitive information
    masked_repair_password = '****' if repair_password else None
    masked_repair_username = '****' if repair_username else None
    masked_repair_encrypt_recovery_key = '****' if encrypt_recovery_key else None
    logger.debug('vm repair create command parameters: vm_name: %s, resource_group_name: %s, repair_password: %s, repair_username: %s, repair_vm_name: %s, copy_disk_name: %s, repair_group_name: %s, unlock_encrypted_vm: %s, enable_nested: %s, associate_public_ip: %s, distro: %s, yes: %s, encrypt_recovery_key: %s, disable_trusted_launch: %s, os_disk_type: %s', 
                 vm_name, resource_group_name, masked_repair_password, masked_repair_username, repair_vm_name, copy_disk_name, repair_group_name, unlock_encrypted_vm, enable_nested, associate_public_ip, distro, yes, masked_repair_encrypt_recovery_key, disable_trusted_launch, os_disk_type)  
  
    # Initializing a command helper object.  
    command = command_helper(logger, cmd, 'vm repair create')  
      
    # The main command execution block.  
    try:  
        # Set parameters used in exception handling to avoid Unbound errors:
        existing_rg = None
        copy_disk_id = None  
        
        # Fetching the data of the source VM.  
        source_vm = get_vm(cmd, resource_group_name, vm_name)  
        source_vm_instance_view = get_vm(cmd, resource_group_name, vm_name, 'instanceView')  
  
        # Checking if the OS of the source VM is Linux and what the Hyper-V generation is.  
        is_linux = _is_linux_os(source_vm)  
        vm_hypervgen = _is_gen2(source_vm_instance_view)  
  
        # Fetching the name of the OS disk and checking if it's managed.  
        target_disk_name = source_vm.storage_profile.os_disk.name  
        is_managed = _uses_managed_disk(source_vm)  
        # Fetching the tag for the repair resource and initializing the list of created resources.  
        resource_tag = _get_repair_resource_tag(resource_group_name, vm_name)  
        created_resources = []  
        # Fetching the architecture of the source VM.  
        architecture_type = _fetch_architecture(source_vm)  
  
        # Checking if the source VM's OS is Linux and if it uses a managed disk.  
        if is_linux and _uses_managed_disk(source_vm):  
            # Setting the OS type to 'Linux'.  
            os_type = 'Linux'  
            # Checking the Hyper-V generation of the source VM.
            hyperV_generation_linux = _check_linux_hyperV_gen(source_vm)
            if hyperV_generation_linux == 'V2':
                # If the Hyper-V generation is 'V2', it may be ARM:
                if architecture_type == 'Arm64':
                    # If the architecture type is 'Arm64', log this information and select the Linux distribution for an Arm64 VM.  
                    logger.info('ARM64 VM detected')
                    os_image_urn = _select_distro_linux_Arm64(distro)
                    # Trusted launch is not supported on ARM
                    logger.info('Disabling trusted launch on ARM')
                    disable_trusted_launch = True
                else:
                    # log this information and select the Linux distribution for an x86 Gen2 VM.
                    logger.info('Generation 2 VM detected')
                    os_image_urn = _select_distro_linux_gen2(distro)
            else:
                # If the architecture type is not 'V2', select a Gen1 VM
                os_image_urn = _select_distro_linux(distro)  
        else:  
            # If the source VM's OS is not Linux, check if a recovery key is provided.  
            if encrypt_recovery_key:  
                # If a recovery key is provided, fetch the compatible Windows OS URN for a VM with Bitlocker encryption.  
                os_image_urn = _fetch_compatible_windows_os_urn_v2(source_vm)  
            else:  
                # If no recovery key is provided, fetch the compatible Windows OS URN for a regular VM.  
                os_image_urn = _fetch_compatible_windows_os_urn(source_vm)  
            # Setting the OS type to 'Windows'.  
            os_type = 'Windows'
  
        # Set public IP address for repair VM
        public_ip_name = _make_public_ip_name(repair_vm_name, associate_public_ip)
        
        # Set up base create vm command
        if is_linux:
            create_repair_vm_command = 'az vm create -g {g} -n {n} --tag {tag} --image {image} --admin-username {username} --admin-password {password} --public-ip-address {option} --custom-data {cloud_init_script}' \
                .format(g=repair_group_name, n=repair_vm_name, tag=resource_tag, image=os_image_urn, username=repair_username, password=repair_password, option=public_ip_name, cloud_init_script=_get_cloud_init_script())
        else:
            create_repair_vm_command = 'az vm create -g {g} -n {n} --tag {tag} --image {image} --admin-username {username} --admin-password {password} --public-ip-address {option}' \
                .format(g=repair_group_name, n=repair_vm_name, tag=resource_tag, image=os_image_urn, username=repair_username, password=repair_password, option=public_ip_name)

        # Fetching the size of the repair VM.  
        sku = _fetch_compatible_sku(source_vm, enable_nested)  
        if not sku:  
            # If no compatible size is found, raise an error.  
            raise SkuNotAvailableError('Failed to find compatible VM size for source VM\'s OS disk within given region and subscription.')  
        # Adding the size to the command.  
        create_repair_vm_command += ' --size {sku}'.format(sku=sku)  


        # Setting the availability zone for the repair VM.  
        # If the source VM has availability zones, the first one is chosen for the repair VM.  
        if source_vm.zones:  
            zone = source_vm.zones[0]  
            create_repair_vm_command += ' --zone {zone}'.format(zone=zone)  

        if disable_trusted_launch:  
            logger.debug('Set security-type to Standard...')  
            create_repair_vm_command += ' --security-type Standard'  
        else:
            # If a Bitlocker recovery key is provided, this indicates the source VM is encrypted.  
            # In this case, the VM and OS disk security profiles need to be fetched and added to the repair VM creation command.  
            if encrypt_recovery_key: 
                # TODO: this was assumed to also need for Trusted Launch VMs, but I don't think this is the case. 
                
                # For confidential VM, some SKUs expect specific security types, secure_boot_enabled and vtpm_enabled.  
                # Fetching the VM security profile and adding it to the command if it exists.  
                logger.debug('Fetching VM security profile...')  
                vm_security_params = _fetch_vm_security_profile_parameters(source_vm)  
                if vm_security_params:  
                    create_repair_vm_command += vm_security_params  
        
        if encrypt_recovery_key:  
            # TODO: this was assumed to also need for Trusted Launch VMs, but I don't think this is the case. 
            
            # For confidential VM and Trusted Launch VM security tags on disks, the disk security profile needs to be brought over as well. 
            # Fetching the OS Disk security profile and adding it to the command if it exists.  
            logger.debug('Fetching OS Disk security profile...')  
            osdisk_security_params = _fetch_osdisk_security_profile_parameters(source_vm)  
            if osdisk_security_params:  
                create_repair_vm_command += osdisk_security_params  
  
        # Creating a new resource group for the repair VM and its resources.  
        # First, check if the repair group already exists.  
        # If it doesn't, create a new resource group at the same location as the source VM.  
        existing_rg = _check_existing_rg(repair_group_name)  
        if not existing_rg:  
            create_resource_group_command = 'az group create -l {loc} -n {group_name}' \
                .format(loc=source_vm.location, group_name=repair_group_name)  
            logger.info('Creating resource group for repair VM and its resources...')  
            _call_az_command(create_resource_group_command)  

        # Check if user is changing the Repair VM os disk type
        if os_disk_type:
            create_repair_vm_command += ' --storage-sku {os_disk_type} '.format(os_disk_type=os_disk_type)

        # Check if the source VM uses managed disks.  
        # If it does, the repair VM will also be created with managed disks.  
        if is_managed:  
            logger.info('Source VM uses managed disks. Creating repair VM with managed disks.\n')  
  
            # Fetch the SKU, location, OS type, and Hyper-V generation of the disk from the source VM.  
            disk_sku, location, os_type, hyperV_generation = _fetch_disk_info(resource_group_name, target_disk_name)  
  
            # Prepare the command to create a copy of the source VM's OS disk.  
            # The command includes the resource group name, copy disk name, target disk name, SKU, location, and OS type.  
            copy_disk_command = 'az disk create -g {g} -n {n} --source {s} --sku {sku} --location {loc} --os-type {os_type} --query id -o tsv' \
                .format(g=resource_group_name, n=copy_disk_name, s=target_disk_name, sku=disk_sku, loc=location, os_type=os_type)  
            # If the Hyper-V generation for the disk is available, append it to the copy disk command.  
            if hyperV_generation:  
                copy_disk_command += ' --hyper-v-generation {hyperV}'.format(hyperV=hyperV_generation)  
  
            # If the source VM is a Linux Gen2 VM but the Hyper-V generation is not available in the disk info,  
            # log this situation and manually add 'V2' to the copy disk command.  
            elif is_linux and hyperV_generation_linux == 'V2':  
                logger.info('The disk did not contain the information of gen2, but the machine is created from gen2 image')  
                copy_disk_command += ' --hyper-v-generation {hyperV}'.format(hyperV=hyperV_generation_linux)  
  
            # If the source VM has availability zones, get the first one and add it to the copy disk command.  
            if source_vm.zones:  
                zone = source_vm.zones[0]  
                copy_disk_command += ' --zone {zone}'.format(zone=zone)  
    
            # Execute the command to create a copy of the OS disk of the source VM.  
            logger.info('Copying OS disk of source VM...')  
            copy_disk_id = _call_az_command(copy_disk_command).strip('\n')  

            # Depending on the operating system of the source VM and whether it's encrypted, different steps are taken.  
            # If the source VM is not a Linux machine, create the repair VM.  
            # This is the case for Windows VMs, both encrypted and not encrypted.  
            if not is_linux:  
                # Call the method to create the repair VM, providing the necessary parameters.  
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)  
  
            # If the source VM is a Windows machine and it is encrypted, unlock the encrypted VM after creation.  
            if not is_linux and unlock_encrypted_vm:  
                # Call the method to create the repair VM.  
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)  
                # Call the method to unlock the encrypted VM, providing the necessary parameters.  
                _unlock_encrypted_vm_run(repair_vm_name, repair_group_name, is_linux, encrypt_recovery_key)  
  
            # If the source VM is a Linux machine and it is encrypted, create the repair VM and then unlock it.  
            if is_linux and unlock_encrypted_vm:  
                # Call the method to create the repair VM.  
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username)  
                # Call the method to unlock the encrypted VM.  
                _unlock_encrypted_vm_run(repair_vm_name, repair_group_name, is_linux)  
  
            # If the source VM is a Linux machine and it is not encrypted, create the repair VM and then attach the data disk.  
            # This is done after VM creation to avoid a UUID mismatch causing an incorrect boot.  
            if is_linux and (not unlock_encrypted_vm):  
                # Call the method to create the repair VM, with the fix_uuid parameter set to True.  
                _create_repair_vm(copy_disk_id, create_repair_vm_command, repair_password, repair_username, fix_uuid=True)  
                logger.info('Attaching copied disk to repair VM as data disk...')  
                # Set up the command to attach the copied disk to the repair VM.  
                attach_disk_command = "az vm disk attach -g {g} --name {disk_id} --vm-name {vm_name} ".format(g=repair_group_name, disk_id=copy_disk_id, vm_name=repair_vm_name)  
                # Execute the command to attach the disk.  
                _call_az_command(attach_disk_command)  


        # Check if the source VM uses unmanaged disks.  
        # If it does, the repair VM will also be created with unmanaged disks.  
        else:  
            logger.info('Source VM uses unmanaged disks. Creating repair VM with unmanaged disks.\n')  
  
            # Get the URI of the OS disk from the source VM.  
            os_disk_uri = source_vm.storage_profile.os_disk.vhd.uri  
  
            # Create the name of the copy disk by appending '.vhd' to the existing name.  
            copy_disk_name = copy_disk_name + '.vhd'  
  
            # Create a StorageResourceIdentifier object for the storage account associated with the OS disk.  
            storage_account = StorageResourceIdentifier(cmd.cli_ctx.cloud, os_disk_uri)  
  
            # Validate the VM creation command to ensure all parameters are correct before proceeding.  
            validate_create_vm_command = create_repair_vm_command + ' --validate'  
            logger.info('Validating VM template before continuing...')  
            _call_az_command(validate_create_vm_command, secure_params=[repair_password, repair_username])  
  
            # Fetch the connection string of the storage account.  
            get_connection_string_command = 'az storage account show-connection-string -g {g} -n {n} --query connectionString -o tsv' \
                .format(g=resource_group_name, n=storage_account.account_name)  
            logger.debug('Fetching storage account connection string...')  
            connection_string = _call_az_command(get_connection_string_command).strip('\n')  
  
            # Create a snapshot of the unmanaged OS disk.  
            make_snapshot_command = 'az storage blob snapshot -c {c} -n {n} --connection-string "{con_string}" --query snapshot -o tsv' \
                .format(c=storage_account.container, n=storage_account.blob, con_string=connection_string)  
            logger.info('Creating snapshot of OS disk...')  
            snapshot_timestamp = _call_az_command(make_snapshot_command, secure_params=[connection_string]).strip('\n')  
            snapshot_uri = os_disk_uri + '?snapshot={timestamp}'.format(timestamp=snapshot_timestamp)  
  
            # Create a copy of the snapshot into an unmanaged disk.  
            copy_snapshot_command = 'az storage blob copy start -c {c} -b {name} --source-uri {source} --connection-string "{con_string}"' \
                .format(c=storage_account.container, name=copy_disk_name, source=snapshot_uri, con_string=connection_string)  
            logger.info('Creating a copy disk from the snapshot...')  
            _call_az_command(copy_snapshot_command, secure_params=[connection_string])  
  
            # Generate the URI of the copied disk.  
            copy_disk_id = os_disk_uri.rstrip(storage_account.blob) + copy_disk_name  
  
            # Create the repair VM with the copied unmanaged disk.  
            create_repair_vm_command = create_repair_vm_command + ' --use-unmanaged-disk'  
            logger.info('Creating repair VM while disk copy is in progress...')  
            _call_az_command(create_repair_vm_command, secure_params=[repair_password, repair_username])  
  
            # Check if the disk copy process is done.  
            logger.info('Checking if disk copy is done...')  
            copy_check_command = 'az storage blob show -c {c} -n {name} --connection-string "{con_string}" --query properties.copy.status -o tsv' \
                .format(c=storage_account.container, name=copy_disk_name, con_string=connection_string)  
            copy_result = _call_az_command(copy_check_command, secure_params=[connection_string]).strip('\n')  
  
            # If the disk copy process failed, raise an error.  
            if copy_result != 'success':  
                raise UnmanagedDiskCopyError('Unmanaged disk copy failed.')  
  
            # Attach the copied unmanaged disk to the repair VM.  
            logger.info('Attaching copied disk to repair VM as data disk...')  
            attach_disk_command = "az vm unmanaged-disk attach -g {g} -n {disk_name} --vm-name {vm_name} --vhd-uri {uri}" \
                .format(g=repair_group_name, disk_name=copy_disk_name, vm_name=repair_vm_name, uri=copy_disk_id)  
            _call_az_command(attach_disk_command)  


        # Check if the Nested Hyper-V needs to be enabled.  
        # If it does, run the script to install Hyper-V and create the nested VM.  
        if enable_nested:  
            logger.info("Running Script win-enable-nested-hyperv.ps1 to install HyperV")  
  
            # Set up the command to run the script to enable Nested Hyper-V.  
            run_hyperv_command = "az vm repair run -g {g} -n {name} --run-id win-enable-nested-hyperv --parameters gen={gen}" \
                .format(g=repair_group_name, name=repair_vm_name, gen=vm_hypervgen)  
  
            # Execute the command to enable Nested Hyper-V.  
            ret_enable_nested = _call_az_command(run_hyperv_command)  
            logger.debug("az vm repair run hyperv command returned: %s", ret_enable_nested)  
  
            # If the script indicates that a restart is required, restart the repair VM.  
            if str.find(ret_enable_nested, "SuccessRestartRequired") > -1:  
                restart_cmd = 'az vm restart -g {rg} -n {vm}'.format(rg=repair_group_name, vm=repair_vm_name)  
                logger.info("Restarting Repair VM")  
                restart_ret = _call_az_command(restart_cmd)  
                logger.debug(restart_ret)  
  
                # After the restart, run the script to enable Nested Hyper-V again to create the nested VM.  
                logger.info("Running win-enable-nested-hyperv.ps1 again to create nested VM")  
                run_hyperv_command = "az vm repair run -g {g} -n {name} --run-id win-enable-nested-hyperv --parameters gen={gen}" \
                    .format(g=repair_group_name, name=repair_vm_name, gen=vm_hypervgen)  
                ret_enable_nested_again = _call_az_command(run_hyperv_command)  
                logger.debug("stderr: %s", ret_enable_nested_again)  
  
        # List all the resources in the repair resource group.  
        created_resources = _list_resource_ids_in_rg(repair_group_name)  
  
        # Set the command status to success.  
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
        created_resources.append(copy_disk_id if copy_disk_id is not None else "")
        command.message = 'Your repair VM \'{n}\' has been created in the resource group \'{repair_rg}\' with disk \'{d}\' attached as data disk. ' \
                          'Please use this VM to troubleshoot and repair. Once the repairs are complete use the command ' \
                          '\'az vm repair restore -n {source_vm} -g {rg} --verbose\' to restore disk to the source VM. ' \
                          'Note that the copied disk is created within the original resource group \'{rg}\'.' \
                          .format(n=repair_vm_name, repair_rg=repair_group_name, d=copy_disk_name, rg=resource_group_name, source_vm=vm_name)
        return_dict = command.init_return_dict()
        # Add additional custom return properties
        return_dict['repair_vm_name'] = repair_vm_name
        return_dict['copied_disk_name'] = copy_disk_name
        return_dict['copied_disk_uri'] = copy_disk_id if copy_disk_id is not None else ""
        return_dict['repair_resource_group'] = repair_group_name
        return_dict['resource_tag'] = resource_tag
        return_dict['created_resources'] = created_resources

        logger.info('\n%s\n', command.message)
    return return_dict


# This method is responsible for restoring the VM after repair  
def restore(cmd, vm_name, resource_group_name, disk_name=None, repair_vm_id=None, yes=False):  
  
    # Create an instance of the command helper object to facilitate logging and status tracking.  
    command = command_helper(logger, cmd, 'vm repair restore')  
  
    try:  
        # Fetch source and repair VM data  
        source_vm = get_vm(cmd, resource_group_name, vm_name)  # Fetch the source VM data  
        is_managed = _uses_managed_disk(source_vm)  # Check if the source VM uses managed disks  
        if repair_vm_id:  
            logger.info('Repair VM ID: %s', repair_vm_id)  
            repair_vm_id = parse_resource_id(repair_vm_id)  # Parse the repair VM ID  
            repair_vm_name = repair_vm_id['name']  
            repair_resource_group = repair_vm_id['resource_group']  
        source_disk = None  
  
        # For MANAGED DISK  
        if is_managed:  
            source_disk = source_vm.storage_profile.os_disk.name  
            # Commands to detach the repaired data disk from the repair VM and attach it to the source VM as an OS disk  
            detach_disk_command = 'az vm disk detach -g {g} --vm-name {repair} --name {disk}' \
                .format(g=repair_resource_group, repair=repair_vm_name, disk=disk_name)  
            attach_fixed_command = 'az vm update -g {g} -n {n} --os-disk {disk}' \
                .format(g=resource_group_name, n=vm_name, disk=disk_name)  
  
            # Detach the repaired data disk from the repair VM and attach it to the source VM as an OS disk  
            logger.info('Detaching repaired data disk from repair VM...')  
            _call_az_command(detach_disk_command)  
            logger.info('Attaching repaired data disk to source VM as an OS disk...')  
            _call_az_command(attach_fixed_command)  
          
        # For UNMANAGED DISK  
        else:  
            source_disk = source_vm.storage_profile.os_disk.vhd.uri  
            # Fetch disk uri from disk name  
            repair_vm = get_vm(cmd, repair_vm_id['resource_group'], repair_vm_id['name'])  
            data_disks = repair_vm.storage_profile.data_disks  
  
            # The params went through validator so no need for existence checks  
            disk_uri = [disk.vhd.uri for disk in data_disks if disk.name == disk_name][0]  
  
            # Commands to detach the repaired data disk from the repair VM and attach it to the source VM as an OS disk  
            detach_unamanged_command = 'az vm unmanaged-disk detach -g {g} --vm-name {repair} --name {disk}' \
                .format(g=repair_resource_group, repair=repair_vm_name, disk=disk_name)  
            attach_unmanaged_command = 'az vm update -g {g} -n {n} --set storageProfile.osDisk.vhd.uri="{uri}"' \
                .format(g=resource_group_name, n=vm_name, uri=disk_uri)  
  
            # Detach the repaired data disk from the repair VM and attach it to the source VM as an OS disk  
            logger.info('Detaching repaired data disk from repair VM...')  
            _call_az_command(detach_unamanged_command)  
            logger.info('Attaching repaired data disk to source VM as an OS disk...')  
            _call_az_command(attach_unmanaged_command)  
  
        # Clean up the resources in the repair resource group  
        _clean_up_resources(repair_resource_group, confirm=not yes)  
        command.set_status_success()  # Set the command status to success  
    # Handle possible exceptions  
    except KeyboardInterrupt:  
        # Capture the stack trace and set the error message if the command is interrupted by the user  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = "Command interrupted by user input."  
        command.message = "Command interrupted by user input. If the restore command fails at retry, please rerun the repair process from \'az vm repair create\'."  
    except AzCommandError as azCommandError:  
        # Capture the stack trace and set the error message if an Azure command error occurs  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = str(azCommandError)  
        command.message = "Repair restore failed. If the restore command fails at retry, please rerun the repair process from \'az vm repair create\'."  
    except Exception as exception:  
        # Capture the stack trace and set the error message if an unexpected error occurs  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = str(exception)  
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'  
    finally:  
        # Log the stack trace if an error has occurred  
        if command.error_stack_trace:  
            logger.debug(command.error_stack_trace)  
  
    # Set the command status to error if it's not success  
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


# This method is responsible for running a script on a VM  
def run(cmd, vm_name, resource_group_name, run_id=None, repair_vm_id=None, custom_script_file=None, parameters=None, run_on_repair=False, preview=None):  
  
    # Log the input parameters for the method  
    logger.debug('vm repair run parameters: vm_name: %s, resource_group_name: %s, run_id: %s, repair_vm_id: %s, custom_script_file: %s, parameters: %s, run_on_repair: %s, preview: %s',  
                 vm_name, resource_group_name, run_id, repair_vm_id, custom_script_file, parameters, run_on_repair, preview)  
  
    # Initiate a command helper object for logging and status tracking  
    command = command_helper(logger, cmd, 'vm repair run')  
  
    # Define the script names for Linux and Windows  
    LINUX_RUN_SCRIPT_NAME = 'linux-run-driver.sh'  
    WINDOWS_RUN_SCRIPT_NAME = 'win-run-driver.ps1'  
  
    # Set the repair map URL if a preview is available  
    if preview:  
        _set_repair_map_url(preview)  
  
    try:  
        # Fetch data of the VM on which the script is to be run  
        source_vm = get_vm(cmd, resource_group_name, vm_name)  
  
        # Determine the OS of the source VM  
        is_linux = _is_linux_os(source_vm)  
  
        # Choose the appropriate script based on the OS of the source VM  
        if is_linux:  
            script_name = LINUX_RUN_SCRIPT_NAME  
        else:  
            script_name = WINDOWS_RUN_SCRIPT_NAME  
  
        # If run_on_repair is False, then the repair VM is the same as the source VM (i.e., scripts run directly on the source VM)  
        if run_on_repair:  
            repair_vm_id = parse_resource_id(repair_vm_id)  
            repair_vm_name = repair_vm_id['name']  
            repair_resource_group = repair_vm_id['resource_group']  
        else:  
            repair_vm_name = vm_name  
            repair_resource_group = resource_group_name  
  
        run_command_params = []  
        additional_scripts = []  
  
        # For the default scenario where a run ID is provided  
        if not custom_script_file:  
            # Fetch the path to the script from GitHub using the run ID  
            repair_script_path = _fetch_run_script_path(run_id)  
            run_command_params.append('script_path="./{}"'.format(repair_script_path))  
        # For the custom script scenario for script testers  
        else:  
            run_command_params.append('script_path=no-op')  
            additional_scripts.append(custom_script_file)  
  
        # If a preview URL is provided, validate it and extract the fork and branch names  
        if preview:  
            parts = preview.split('/')  
            if len(parts) < 7 or parts.index('map.json') == -1:  
                raise Exception('Invalid preview url. Write full URL of map.json file. example https://github.com/Azure/repair-script-library/blob/main/map.json')  
            last_index = parts.index('map.json')  
            fork_name = parts[last_index - 4]  
            branch_name = parts[last_index - 1]  
            run_command_params.append('repo_fork="{}"'.format(fork_name))  
            run_command_params.append('repo_branch="{}"'.format(branch_name))  
  
        # Append parameters for the script  
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
  
        logger.info('Running script on %s: %s', vm_string, repair_vm_name)  # Log the VM on which the script is being run  


                # Start the timer to measure the run-time of the script  
        script_start_time = timeit.default_timer()  
  
        # Invoke the run command on the VM and capture the standard output and error  
        stdout, stderr = _invoke_run_command(script_name, repair_vm_name, repair_resource_group, is_linux, run_command_params, additional_scripts)  
  
        # Calculate the run-time of the script and log it  
        command.script.run_time = timeit.default_timer() - script_start_time  
        logger.debug("stderr: %s", stderr)  
  
        # Parse the standard output to check if the script execution was successful  
        run_script_succeeded = _check_script_succeeded(stdout)  
  
        # Parse the raw logs from the standard output  
        logs = _parse_run_script_raw_logs(stdout)  
  
        # Process the start and end of the log  
        # If the log is over 4k bytes, it gets cutoff at the start  
        log_cutoff = True  
        log_fullpath = ''  
        for log in logs:  
            if log['level'] == 'Log-Start':  
                log_cutoff = False  
            if log['level'] == 'Log-End':  
                split_log = log['message'].split(']')  
                if len(split_log) == 2:  
                    log_fullpath = split_log[1]  
  
        # If the log is cutoff, give a warning to the user  
        if log_cutoff:  
            logger.warning('Log file is too large and has been cutoff at the start of file. Please locate the log file within the %s using the logFullpath to check full logs.', vm_string)  
  
        # If the script execution was successful, set the status to success and log the output  
        # If the script execution was unsuccessful, set the status to error and log the error  
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
  
        # Set the overall command status to success  
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


# This method lists all available repair scripts  
def list_scripts(cmd, preview=None):  
    # Initiate a command helper object for logging and status tracking  
    command = command_helper(logger, cmd, 'vm repair list-scripts')  
  
    # Set the repair map URL if a preview is available  
    if preview:  
        _set_repair_map_url(preview)  
  
    try:  
        # Fetch the map of all available scripts  
        run_map = _fetch_run_script_map()  
  
        # Set the command status to success  
        command.set_status_success()  
  
    # Handle possible exceptions  
    except requests.exceptions.RequestException as exception:  
        # Capture the stack trace and set the error message if a request exception occurs  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = str(exception)  
        command.message = "Failed to fetch run script data from GitHub. Please check this repository is reachable: https://github.com/Azure/repair-script-library"  
    except Exception as exception:  
        # Capture the stack trace and set the error message if an unexpected error occurs  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = str(exception)  
        command.message = 'An unexpected error occurred. Try running again with the --debug flag to debug.'  
    finally:  
        # Log the stack trace if an error has occurred  
        if command.error_stack_trace:  
            logger.debug(command.error_stack_trace)  
  
    # Set the command status to error if it's not success  
    if not command.is_status_success():  
        command.set_status_error()  
        return_dict = command.init_return_dict()  
    else:  
        # Construct return dict  
        command.message = 'Available script list succesfully fetched from https://github.com/Azure/repair-script-library'  
        return_dict = command.init_return_dict()  
        return_dict['map'] = run_map  
  
    return return_dict  


# This method resets the network interface card (NIC) of a virtual machine (VM)  
def reset_nic(cmd, vm_name, resource_group_name, yes=False):  
    # Initiate a command helper object for logging and status tracking  
    command = command_helper(logger, cmd, 'vm repair reset-nic')  
    DYNAMIC_CONFIG = 'Dynamic'  
  
    try:  
        # 0) Check if VM is off. If it is, ask to start the VM.  
        # VM must be running to reset its NIC.  
        VM_OFF_MESSAGE = 'VM is not running. The VM must be in running to reset its NIC.\n'  
  
        vm_instance_view = get_vm(cmd, resource_group_name, vm_name, 'instanceView')  
        VM_started = _check_n_start_vm(vm_name, resource_group_name, not yes, VM_OFF_MESSAGE, vm_instance_view)  
  
        # If VM is not started, raise an error  
        if not VM_started:  
            raise CommandCanceledByUserError("Could not get consent to run VM before resetting the NIC.")  
  
        # 1) Fetch VM network info  
        logger.info('Fetching necessary VM network information to reset the NIC...\n')  
          
        # Fetch primary NIC ID. The primary field is null or true for primary NICs.  
        get_primary_nic_id_command = 'az vm nic list -g {g} --vm-name {n} --query "[[?primary].id || [?primary==null].id][0][0]" -o tsv' \
            .format(g=resource_group_name, n=vm_name)  
        primary_nic_id = _call_az_command(get_primary_nic_id_command)  
  
        # If no primary NIC is found, raise an error  
        if not primary_nic_id:  
            raise SupportingResourceNotFoundError('The primary NIC for the VM was not found on Azure.')  
        primary_nic_name = primary_nic_id.split('/')[-1]  
  
        # Get IP config info to get: vnet name, current private IP, IP config name, subnet ID  
        get_primary_ip_config = 'az network nic ip-config list -g {g} --nic-name {nic_name} --query [[?primary]][0][0]' \
            .format(g=resource_group_name, nic_name=primary_nic_name)  
        ip_config_string = _call_az_command(get_primary_ip_config)  
  
        # If no primary IP configuration is found, raise an error  
        if not ip_config_string:  
            raise SupportingResourceNotFoundError('The primary IP configuration for the VM NIC was not found on Azure.')  
        ip_config_object = json.loads(ip_config_string)  

                # Extract subnet ID from the IP configuration  
        subnet_id = ip_config_object['subnet']['id']  
  
        # Tokenize the subnet ID to extract various components  
        subnet_id_tokens = subnet_id.split('/')  
        subnet_name = subnet_id_tokens[-1]  # Last token is subnet name  
        vnet_name = subnet_id_tokens[-3]  # The third token from last is VNet name  
        vnet_resource_group = subnet_id_tokens[-7]  # The seventh token from last is VNet resource group  
        ipconfig_name = ip_config_object['name']  # Extract IP configuration name  
        orig_ip_address = ip_config_object['privateIPAddress']  # Extract original IP address  
  
        # Extract application security groups, if any  
        application_names = ""  
        applicationSecurityGroups = 'applicationSecurityGroups'  
        if applicationSecurityGroups in ip_config_object:  
            for item in ip_config_object[applicationSecurityGroups]:  
                application_id_tokens = item['id'].split('/')  
                if application_id_tokens[-1] is not None:  
                    application_names += application_id_tokens[-1] + " "  
  
        logger.info('applicationSecurityGroups {application_names}...\n')  
  
        # Extract original IP allocation method (Dynamic or Static)  
        orig_ip_allocation_method = ip_config_object['privateIPAllocationMethod']  
  
        # Get available IP address within subnet  
        get_available_ip_command = 'az network vnet subnet list-available-ips -g {g} --vnet-name {vnet} --name {subnet} --query [0] -o tsv' \
            .format(g=vnet_resource_group, vnet=vnet_name, subnet=subnet_name)  
        swap_ip_address = _call_az_command(get_available_ip_command)  
        if not swap_ip_address:  
            # Raise available IP not found error  
            raise SupportingResourceNotFoundError('Available IP address was not found within the VM subnet.')  
  
        # 3) Update private IP address to another in subnet. This will invoke and wait for a VM restart.  
        logger.info('Updating VM IP configuration. This might take a few minutes...\n')  
  
        # Update IP address  
        if application_names:  
            update_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip} --asgs {asgs}' \
                .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=swap_ip_address, asgs=application_names)  
        else:  
            logger.info('applicationSecurityGroups do not exist...\n')  
            update_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip}' \
                .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=swap_ip_address)  
        _call_az_command(update_ip_command)  

                # Wait for IP to be updated  
        # This command waits for the network interface card (NIC) IP configuration to be updated  
        wait_ip_update_command = 'az network nic ip-config wait --updated -g {g} --nic-name {nic}' \
            .format(g=resource_group_name, nic=primary_nic_name)  
        _call_az_command(wait_ip_update_command)  
  
        # 4) Revert the configurations. This will also invoke and wait for a VM restart.  
        logger.info('NIC reset is complete. Now reverting back to your original configuration...\n')  
  
        # Initialize the revert IP command variable  
        revert_ip_command = None  
  
        # If the original IP allocation method was dynamic, revert back to dynamic  
        if orig_ip_allocation_method == DYNAMIC_CONFIG:  
            # If there are application security groups, include them in the command  
            if application_names:  
                revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --set privateIpAllocationMethod={method} --asgs {asgs}' \
                    .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, method=DYNAMIC_CONFIG, asgs=application_names)  
            else:  
                revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --set privateIpAllocationMethod={method}' \
                    .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, method=DYNAMIC_CONFIG)  
        else:  
            # If the original IP allocation method was not dynamic, revert to the original static IP  
            # If there are application security groups, include them in the command  
            if application_names:  
                revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip} --asgs {asgs}' \
                    .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=orig_ip_address, asgs=application_names)  
            else:  
                revert_ip_command = 'az network nic ip-config update -g {g} --nic-name {nic} -n {config} --private-ip-address {ip} ' \
                    .format(g=resource_group_name, nic=primary_nic_name, config=ipconfig_name, ip=orig_ip_address)  
  
        # Execute the revert IP command  
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
    """    
    This function manages the process of repairing and restoring a specified virtual machine (VM). The process involves  
    the creation of a repair VM, the generation of a copy of the problem VM's disk, and the formation of a new resource   
    group specifically for the repair operation.   
  
    :param cmd: Command object that is used to execute Azure CLI commands.  
    :param vm_name: The name of the VM that is targeted for repair.  
    :param resource_group_name: The name of the resource group in which the targeted VM is located.  
    :param repair_password: (Optional) Password to be used for the repair operation. If not provided, a random password is generated.  
    :param repair_username: (Optional) Username to be used for the repair operation. If not provided, a random username is generated.  
    :param repair_vm_name: (Optional) The name to assign to the repair VM. If not provided, a unique name is generated.  
    :param copy_disk_name: (Optional) The name to assign to the copy of the disk. If not provided, a unique name is generated.  
    :param repair_group_name: (Optional) The name of the repair resource group. If not provided, a unique name is generated.  
    """  
    from datetime import datetime  
    import secrets  
    import string  
  
    # Initialize command helper object  
    command = command_helper(logger, cmd, 'vm repair repair-and-restore')  
  
    # Generate a random password for the repair operation  
    password_length = 30  
    password_characters = string.ascii_lowercase + string.digits + string.ascii_uppercase  
    repair_password = ''.join(secrets.choice(password_characters) for i in range(password_length))  
  
    # Generate a random username for the repair operation  
    username_length = 20  
    username_characters = string.ascii_lowercase + string.digits  
    repair_username = ''.join(secrets.choice(username_characters) for i in range(username_length))  
  
    # Generate unique names for the repair VM, copied disk, and repair resource group  
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')  
    repair_vm_name = ('repair-' + vm_name)[:14] + '_'  
    copy_disk_name = vm_name + '-DiskCopy-' + timestamp  
    repair_group_name = 'repair-' + vm_name + '-' + timestamp  
  
    # Check if a resource group with the same name already exists  
    existing_rg = _check_existing_rg(repair_group_name)  
  
    # Create a repair VM, copy of the disk, and a new resource group  
    create_out = create(cmd, vm_name, resource_group_name, repair_password, repair_username, repair_vm_name=repair_vm_name, copy_disk_name=copy_disk_name, repair_group_name=repair_group_name, associate_public_ip=False, yes=True)  
  
    # Log the output of the create operation  
    logger.info('create_out: %s', create_out)  
  
    # Extract the repair VM name, copied disk name, and repair resource group from the output  
    repair_vm_name = create_out['repair_vm_name']  
    copy_disk_name = create_out['copied_disk_name']  
    repair_group_name = create_out['repair_resource_group']  
  
    # Log that the fstab run command is about to be executed  
    logger.info('Running fstab run command')  

    try:  
        # Run the fstab script on the repair VM  
        run_out = run(cmd, repair_vm_name, repair_group_name, run_id='linux-alar2', parameters=["fstab", "initiator=SELFHELP"])  
  
    except Exception:  
        # If running the fstab script fails, log the error and clean up resources  
        command.set_status_error()  
        command.error_stack_trace = traceback.format_exc()  
        command.error_message = "Command failed when running fstab script."  
        command.message = "Command failed when running fstab script."  
    
        # If the resource group existed before, confirm before cleaning up resources  
        # Otherwise, clean up resources without confirmation  
        if existing_rg:  
            _clean_up_resources(repair_group_name, confirm=True)  
        else:  
            _clean_up_resources(repair_group_name, confirm=False)  
        return  
    
    # Log the output of the run command  
    logger.info('run_out: %s', run_out)  
    
    # If the fstab script returned an error, log the error and clean up resources  
    if run_out['script_status'] == 'ERROR':  
        logger.error('fstab script returned an error.')  
        if existing_rg:  
            _clean_up_resources(repair_group_name, confirm=True)  
        else:  
            _clean_up_resources(repair_group_name, confirm=False)  
        return  
    
    # Run the restore command  
    logger.info('Running restore command')  
    show_vm_id = 'az vm show -g {g} -n {n} --query id -o tsv' \
        .format(g=repair_group_name, n=repair_vm_name)  
    
    repair_vm_id = _call_az_command(show_vm_id)  
    
    restore(cmd, vm_name, resource_group_name, copy_disk_name, repair_vm_id, yes=True)  
    
    # Set the success message  
    command.message = 'fstab script has been applied to the source VM. A new repair VM \'{n}\' was created in the resource group \'{repair_rg}\' with disk \'{d}\' attached as data disk. ' \
        'The repairs were complete using the fstab script and the repair VM was then deleted. ' \
        'The repair disk was restored to the source VM. ' \
            .format(n=repair_vm_name, repair_rg=repair_group_name, d=copy_disk_name)  
    
    # Mark the operation as successful  
    command.set_status_success()  
    
    # If there were any errors, log the stack trace  
    if command.error_stack_trace:  
        logger.debug(command.error_stack_trace)  
    
    # Initialize the return dictionary and log the success message  
    return_dict = command.init_return_dict()  
    
    logger.info('\n%s\n', command.message)  
    
    # Return the result of the operation  
    return return_dict

def repair_button(cmd, vm_name, resource_group_name, button_command, repair_password=None, repair_username=None, repair_vm_name=None, copy_disk_name=None, repair_group_name=None):
    from datetime import datetime
    import secrets
    import string

    # Init command helper object
    command = command_helper(logger, cmd, 'vm repair repair-button')

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

    logger.info('Running command')

    try:
        run_out = run(cmd, repair_vm_name, repair_group_name, run_id='linux-alar2', parameters=[button_command, "initiator=SELFHELP"])

    except Exception:
        command.set_status_error()
        command.error_stack_trace = traceback.format_exc()
        command.error_message = "Command failed when running  script."
        command.message = "Command failed when running script."
        if existing_rg:
            _clean_up_resources(repair_group_name, confirm=True)
        else:
            _clean_up_resources(repair_group_name, confirm=False)
        return

    # log run_out
    logger.info('run_out: %s', run_out)

    if run_out['script_status'] == 'ERROR':
        logger.error(' script returned an error.')
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

    command.message = 'script has been applied to the source VM. A new repair VM \'{n}\' was created in the resource group \'{repair_rg}\' with disk \'{d}\' attached as data disk. ' \
        'The repairs were complete using the script and the repair VM was then deleted. ' \
        'The repair disk was restored to the source VM. ' \
        .format(n=repair_vm_name, repair_rg=repair_group_name, d=copy_disk_name)

    command.set_status_success()
    if command.error_stack_trace:
        logger.debug(command.error_stack_trace)
    # Generate return object and log errors if needed
    return_dict = command.init_return_dict()

    logger.info('\n%s\n', command.message)

    return return_dict
