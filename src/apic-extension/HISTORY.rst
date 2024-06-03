.. :changelog:

Release History
===============

1.0.0
++++++++++++++++++
* Update: Redesigned `az apic service import-from-apim` command to provide easier way to specify APIM instance
* Update: Renamed `az apic service *` commands to `az apic *` commands
* Update: Renamed `--name/--service/--service-name/-s` parameters in `az apic *` commands to `--name/-n`
* Update: Renamed `--service/--service-name/-s` parameters in each sub commands to `--service-name/-n`
* Update: Renamed `--metadata-schema/--metadata-schema-name/--name` parameters in `az apic metadata *` commands to `--metadata-name`
* Update: Renamed `--environment-name` parameter in `az apic api register` command to `--environment-id`
* Fix: API title created by register command is not same with provided spec
* Fix: Error not thrown when import spec with >3MB file
* Fix: Error when register API with long description in spec
* Fix: `--definition-id`, `--environment-id`, `--server`, `--title` parameters should be required in `az apic api deployment create` command
* Fix: `--format`, `--specification`, `--value` parameters should be required in `az apic api definition import-specification` command
* Remove: `--state`` parameter for `az apic api deployment` commands.
* Remove: `--file-name`` parameter for `az apic api definition import-specification`, `az apic metadata create` and `az apic metadata update` command. Use the `@filename` syntax provided by Azure CLI to read parameter value from a file directly.

1.0.0b5
++++++++++++++++++
* Add: Support yaml file for `az apic api register` command.
* Update: Command names, parameter names, and command descriptions for better understanding. Please leverage `-h` option or refer Azure CLI reference doc to see full list of commands and parameters.
* Update: Introduction to parameter constraints to ensure that valid values are provided.
* Update: Minimum Azure CLI version requirement is updated to 2.57.
* Fix: Various bug fixes for lastest preview version.
* Remove: Portal commands as we don't support this capability any longer.
* Remove: `--workspace-name` and `--terms-of-service` parameters are removed as they are not expected to be exposed.
* Remove: `head` commands in each command group are removed.

1.0.0b4
++++++++++++++++++
* Add: Support for Default Portal configuration and default hostname provisoning deprovisioning commands

1.0.0b3
++++++++++++++++++
* Add: Support for Import from apim command along with add examples for create service

1.0.0b2
++++++++++++++++++
* Remove: All workspace cli commands as it should not be exposed to customers just yet.

1.0.0b1
++++++++++++++++++
* Initial release.
