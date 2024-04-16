
Release History
===============
1.0.4
++++++
Logging improvements and script fixing

1.0.3
++++++
Bug fix the win-nest specific SKU issue

1.0.2
++++++
Bug fix for repo null string check so its set to main correctly
Add more logging to capture issues

1.0.1
++++++
Fix bug in win-run-driver.ps1 for 1.0.0b1.

1.0.0b1
++++++
Fix bug in win-run-driver.ps1 default values for invoking run command through az vm repair run.

0.5.9
++++++
Adding default values in win-run-driver.ps1 script for repo_fork and branch_name.

0.5.8
++++++
Fix az vm repair run --preview parameter to take in fork and branch name of User's repository.

0.5.7
++++++
Remove VM-repair SUSE image check

0.5.6
++++++
Renaming the Public IP resource.
Fix the name of the resource, previously the name was always "yes". Now it follows the format repair-<VM>_PublicIP

0.5.5
++++++
Adding ARM64 support.
Fix for telemetry for repair-and-restore command.
Repair VM fix for gen1 VM attaching disk on SCSI controller, preventing nested VM from booting (by Ryan McCallum)

0.5.4
++++++
Adding repair-and-restore command to create a one command flow for vm-repair with fstab scripts.

0.5.3
++++++
Removing check for EncryptionSettingsCollection.enabled is string 'false'.

0.5.2
++++++
Fix bug in _fetch_encryption_settings, add check for EncryptionSettingsCollection.enabled is false.

0.5.1
++++++
Updated exsiting privateIpAddress field to privateIPAddress and privateIpAllocationMethod to privateIPAllocationMethod.

0.5.0
++++++
Support for hosting repair vm in existing resource group and fixing existing resource group logic 

0.5.0
++++++
Support for hosting repair vm in existing resource group and fixing existing resource group logic 

0.4.10
++++++
Support for hosting repair vm in existing resource group and fixing existing resource group logic 

0.4.9
++++++
Fix for encrypted vm's auto unlock feature 

0.4.8
++++++
Fix for encrypted vm's and fixing test cases

0.4.7
++++++
Setting subscription account for reset-nic

0.4.6
++++++
Updating the fetch_repair_vm to use the small letters in the query instead of capital letters

0.4.5
++++++
Improve az vm repair reset-nic command to use subnet list available ips command

0.4.4
++++++
Add az vm repair reset-nic command

0.4.3
++++++
Adding a new distro option for creating the recovery VM, adding the detect for gen2 Linux machine and create a gen2 recovery VM

0.4.2
++++++
Linux only: Fixing duplicated UUID issue. Data disk gets attached only after VM got created.

0.4.1
++++++
Fixing bug in preview parameter

0.4.0
++++++
Fixing issue in disk copy, removing floating point in disk name.

0.3.9
++++++
Add support for preview flag and fix Gen2 bug

0.3.8
++++++
Add support for optional public IP 

0.3.6
++++++
Add support for ALAR2 which requires cloud-init script to prepare the recovery VM with a
build environment for Rust.

0.3.5
++++++

Add support for nested VMs
