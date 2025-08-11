.. :changelog:

Release History
===============
1.2.0b3
++++++++++++++++++

**New Features:**

* Added new command ``az apic api-analysis`` to manage API analysis in Azure API Center.
  * Added ``az apic api-analysis create`` to create an API analysis.
  * Added ``az apic api-analysis delete`` to delete an API analysis.
  * Added ``az apic api-analysis list`` to list all API analyses.
  * Added ``az apic api-analysis show`` to show details of an API analysis.
  * Added ``az apic api-analysis update`` to update an API analysis.
  * Added ``az apic api-analysis import-ruleset`` to import an API analysis ruleset.
  * Added ``az apic api-analysis export-ruleset`` to export an API analysis ruleset.
* Added new command ``az apic import apim`` to import an API from an Azure API Management instance.

**Deprecations:**
  * Deprecated the ``az apic import-from-apim`` command.

1.2.0b2
++++++++++++++++++
* Remove msrestazure dependency

1.2.0b1
++++++++++++++++++

**New Features:**

* Added new command ``az apic integration create`` to manage integrations in Azure API Center.
  * Added ``az apic integration create apim`` to manage Azure API Management integrations as an API source.
  * Added ``az apic integration create aws`` to manage Amazon API Gateway as an API source.
* Added new command ``az apic import aws`` to import an API from an Amazon API Gateway instance.
* Added url option for ``--api-location`` parameter in ``az apic api register`` command.

**Updates:**

* Added examples for using ``@filename`` syntax in several commands' help documentations.
* Improved error messages for the ``az apic api register`` command.

**Fixes:**

* Corrected the example for ``az apic update`` command.
* Fixed an expired link in ``az apic api definition import-specification`` command's help documentation.

1.1.0
++++++++++++++++++

**New Features:**

* Added ``--custom-metadata-only`` parameter to ``az apic metadata export`` command.
* Added single custom metadata update for ``az apic api update`` command.

**Updates:**

* Added example for ``az apic api update`` command.
* Added examples with system assigned identity for ``az apic create`` and ``az apic update`` commands.

**Fixes:**

* Set external document correctly in ``az apic api register`` command.
* Do not use API description as summary in ``az apic api register`` command. 

**Removals:**

* Eliminated duplicate example for ``az apic create`` command.

1.0.0
++++++++++++++++++
Potential Impact: The changes in this release, including the renaming of commands and parameters, may require changes to existing scripts and integrations. Please review the changes carefully and update your code accordingly.

**Updates:**

* Redesigned ``az apic service import-from-apim`` command for an easier specification of APIM instances.
* [BREAKING CHANGE] Renamed ``az apic service *`` commands to ``az apic *`` commands.
* [BREAKING CHANGE] Renamed ``--name/--service/--service-name/-s`` parameters in ``az apic *`` commands to ``--name/-n``.
* [BREAKING CHANGE] Renamed ``--service/--service-name/-s`` parameters in subcommands to ``--service-name/-n``.
* [BREAKING CHANGE] Renamed ``--metadata-schema/--metadata-schema-name/--name`` parameters in ``az apic metadata *`` commands to ``--metadata-name``.
* [BREAKING CHANGE] Renamed ``--environment-name`` parameter in ``az apic api register`` command to ``--environment-id``.

**Fixes:**

* Ensured API title created by ``register`` command matches the provided specification.
* Addressed the non-throwing of errors when importing specifications with files larger than 3MB.
* Resolved errors occurring when registering APIs with long descriptions in the specification.
* [BREAKING CHANGE] Made ``--definition-id``, ``--environment-id``, ``--server``, ``--title`` parameters mandatory in ``az apic api deployment create`` command.
* [BREAKING CHANGE] Made ``--format``, ``--specification``, ``--value`` parameters mandatory in ``az apic api definition import-specification`` command.

**Removals:**

* Removed ``--state`` parameter from ``az apic api deployment`` commands.
* [BREAKING CHANGE] Eliminated ``--file-name`` parameter for ``az apic api definition import-specification``, ``az apic metadata create``, and ``az apic metadata update`` commands. Introduced usage of the ``@filename`` syntax for reading parameter values from a file directly in Azure CLI.

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
