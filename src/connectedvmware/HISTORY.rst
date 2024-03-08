.. :changelog:

Release History
===============
1.0.0
++++++
* Add command `az connectedvmware create-from-machines`.
* Delete HCRP Machine resource by default during `delete vm`. To retain, use `--retain-machine` flag.
* Use GA API Version for VCENTER_KIND_GET_API_VERSION.
* Set extension to non-preview version

0.2.4
++++++
* Link existing HCRP machine to vCenter using the CLI.
* Add examples in help.

0.2.3
++++++
* Fix docs and help for vm creation from template with disk override.
* Convert any HCRP machine with empty kind to VMWare / AVS kind, while enabling vm from inventory.
* Reprompt fix for password for vcenter connect.

0.2.2
++++++
* GA release: Using stable API version for all operations.
* `az connectedvmware inventory item show` shows inventory-type specific properties.

0.2.1
++++++
* Bug fix for `get-resource-id` internal function, which was not honoring resource-group override.

0.2.0
++++++
* Using New Resource Model for all VM operations:
    * `vm` command : Create, Update, Delete, Show, Start, Stop, Restart VirtualMachineInstance
    * `vm guest-agent` command : Enable, Show VMInstanceGuestAgent
    * `vm extension` command : Create, Update, Delete, Show, List MachineExtensions
* If underlying machine is not present, it gets created during vm create
* Added delete-from-host flag for `vm delete`
* Deprecated VM List option as VM Instance is a child resource of Machines.
* Updated tests and helps accordingly.
* raising better exception types instead of CLIError

0.1.12
++++++
* Fixed VM extension issue.

0.1.11
++++++
Including pwinput in code to workaround the issue with azure cli version >= 2.42.0 in windows installed using MSI.
Issue link: https://github.com/Azure/azure-cli/issues/24781

0.1.10
++++++
* Bug Fix: Wait for SystemAssigned Identity PATCH to complete before enabling Guest management on VM.

0.1.9
++++++
* Update API Version from 2020-10-01-preview to 2022-01-10-preview.
* Support for VM delete in retain mode.

0.1.8
++++++
* Displaying asterisks (*****) for password input.

0.1.7
++++++
* Proxy support in vm guest agent.
* Deprecate support to create resource from moref id.
* [BREAKING CHANGE] Fixed guest-agent enable issue. 

0.1.6
++++++
* Fix vm update issue.
* Fix inventory item show.
* Add support for tagging.

0.1.5
++++++
* Fixed inventory item id issue.

0.1.4
++++++
* Add vm extension support.

0.1.3
++++++
* Fixed inventory item issue.

0.1.2
++++++
* Added support for cluster, datastore and host.
* Added support for placement profile.

0.1.1
++++++
* vcenter connection details can be skipped in CLI args, the user will be prompted for the skipped values in that case.

0.1.0
++++++
* Initial release.

