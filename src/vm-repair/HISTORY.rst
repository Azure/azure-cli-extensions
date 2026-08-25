
Release History
===============

2.2.6
++++++
Fixing ``az extension add --name vm-repair`` failing with ``Pip failed with status code 2`` on 32-bit Windows installations of the Azure CLI. The extension declared ``opencensus`` as a dependency but never imported it. Because extensions are installed with ``pip --target``, that unused dependency pulled roughly twenty extra packages into the extension folder, including ``cryptography``, which stopped publishing 32-bit Windows wheels in version 49.0.0. On a 32-bit CLI, pip had no compatible wheel, fell back to building ``cryptography`` from source, and failed. Removing the unused ``opencensus`` dependency removes that entire dependency tree.
Also declaring ``applicationinsights``, which the telemetry module imports on every command but which was never listed as a dependency. It previously resolved only because the Azure CLI happened to ship it, even though no Azure CLI package requires it, so any future CLI that dropped it would have broken every ``vm repair`` command at import time.

2.2.5
++++++
Fixing a regression introduced in 2.2.1 that could break every ``vm repair`` command on Windows when ``az`` resolves to the ``az.cmd`` launcher (the default for MSI installations). The command-injection hardening quoted every token of the nested ``az`` call, including the ``az`` program name itself. cmd.exe then treated it as a literal path instead of a PATH search, so ``%~dp0`` inside ``az.cmd`` no longer pointed at the launcher directory, the bundled Python interpreter was not found, and the call failed with ``Failed to load python executable.`` and exit code 1. The ``az`` token is no longer quoted; all arguments are still individually quoted, so the injection protection added in 2.2.1 (MSRC 115198) is unchanged.
Also fixing failed ``az`` calls that surfaced an empty error message. Because the launcher reports on standard output and leaves standard error empty, the failure previously produced a blank error and empty telemetry. The error now falls back to the command's standard output, reports the exit code when there is no output at all, and masks credentials passed as secure parameters.

2.2.4
++++++
Replacing deprecated ``datetime.utcnow()`` with timezone-aware ``datetime.now(timezone.utc)`` for Python 3.12+ forward compatibility. ``datetime.utcnow()`` is deprecated as of Python 3.12 and scheduled for removal in a future release. The generated timestamps (used for repair VM, copied disk, and repair resource group names) are unchanged. Also replacing ``pkgutil.get_loader()``/``loader.load_module()`` (deprecated in Python 3.12, removed in Python 3.14) with ``importlib.util.find_spec()`` when locating the bundled driver scripts, and extending the static Python 3.12+ compatibility guard to cover these APIs.

2.2.3
++++++
Fixing a crash ("version: null") when running any ``vm repair`` command on Azure CLI 2.87. Newer ``setuptools`` no longer generates the ``metadata.json`` that CLI 2.87 relied on to read the installed extension version, so the version resolved to ``None`` and the extension's version check raised a ``TypeError`` before the command could run. The version check now handles a missing version gracefully instead of failing. Azure CLI 2.88 also fixes the underlying metadata issue, so upgrading the CLI remains the recommended long-term resolution.

2.2.1
++++++
Fixing a command injection vulnerability (MSRC 115198 / VULN-185362). Source VM tag values copied via ``--copy-tags`` could contain shell metacharacters that, on Windows, were interpreted by ``cmd.exe`` and executed as arbitrary commands on the operator's workstation. Tag keys and values are now validated and quoted before being interpolated into the ``az`` command, and ``_call_az_command`` quotes every argument so ``cmd.exe`` treats shell metacharacters as literal text. Minimum fixed version: 2.2.1.

2.2.0
++++++
Adding `--tags` parameter to `vm repair create` and `vm repair repair-and-restore` commands to allow users to tag the repair VM for organizational requirements
Adding `--copy-tags` parameter to `vm repair create` and `vm repair repair-and-restore` commands to allow users to copy tags from the source VM to the repair VM
Adding `--size` parameter to `vm repair create` and `vm repair repair-and-restore` commands to allow users to specify the size of the repair VM
Changing the default to only create a public IP when `--associate-public-ip` flag is set
Updating Linux image list for new versions and removing EoL versions
TODO: update public docs after release to match new behaviors
TODO: remove `--yes` parameter in future release after users have adapted to new behavior

2.1.3
++++++
Fixing an issue with repair-and-restore related to the change to python3.13
Fixing an unreported issue with restore only sending the disk name instead of full ID, which works up until az-cli 2.81
linting/flake8 fixes
Removing logging of user/pass of repair VM

2.1.2
++++++
Added images available for --distro flag to include current distributions, will remove EoL versions in future releases
Fixing a logic bug to allow V2 linux detection to work properly, and with Arm64
Disabled trusted launch for Arm64

2.1.1
++++++
Updated README file for `vm repair` extension.

2.1.0
++++++
Added new parameter `--os-disk-type` to `vm repair create` to let users specify the repair vm's os disk storage account type.

2.0.3
++++++
Added new long parameter functionality in `vm repair run` cmd `parameters` parameter. When using the prefix `++`, the entire key=value string will be sent to the running script, not just the value.


2.0.2
++++++
Updated parameter descriptions and examples for `az vm repair create`.

2.0.1
++++++
Fixed 2 Unbound variable bugs in `vm repair create` and improved the code documentation.

2.0.0
++++++
Changed default VM image to 2022-datacenter-smalldisk for better default security.

1.1.1
++++++
Migrated VM Repair off of the `msrestazure` API to `azure.core` and `azure.mgmt` APIs.
Fixed a bug with `--associate-public-ip` where it was always creating a public IP. Now a private IP will be used if `--associate-public-ip` is not specified.

1.1.0
++++++
Added script for GT fixit button.
Added support for `--disable-trusted-launch` flag parameter to set security type to `Standard` on the repair VM no matter what the source VM has.

1.0.10
++++++
Added breaking change warning for the default image for Windows source VMs if the source VM image is not found in `az vm repair create`. It will change from a 2016 image to 2022 in November 2024.

1.0.9
++++++
Fixed and updated several vm-repair tests for better coverage.
Removed and updated broken image aliases pointing at images that no longer existed.
Add `--encrypt-recovery-key` string parameter to `vm repair create` to use recovery key provided by the user to unlock the disk for a confidential VM.

1.0.8
++++++
SELFHELP telemetry added as initiator. Extra parameters is introduced at the backend to capture the telemetry data.

1.0.7
++++++
az command adjustment

1.0.6
++++++
Add CLI update wait for ASG to wait for the operation done as the async 2rd operation will cancel the 1st call.

1.0.5
++++++
Bug fix ASG is not added properly when reset the nic
Add ASG if exist when nic is reset

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
