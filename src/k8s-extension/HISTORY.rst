.. :changelog:

Release History
===============

0.1.0
++++++++++++++++++
* Initial release.

0.1.1
++++++++++++++++++
* Add support for microsoft-azure-defender extension type

0.1.2
++++++++++++++++++

* Add support for Arc Appliance cluster type

0.1.3
++++++++++++++++++

* Customization for microsoft.openservicemesh

0.1PP.4
++++++++++++++++++

* Refactor for clear separation of extension-type specific customizations
* Introduce new versioning scheme to allow Preview releases by Partners

0.1PP.5
++++++++++++++++++

* OpenServiceMesh customization.
* If Version is passed in, accept None for AutoUpgradeMinorVersion, and not require it to be False.

0.1PP.6
++++++++++++++++++

* OpenServiceMesh customization.
* Scope is always cluster.  Version is mandatory for staging and pilot release-trains.

0.1PP.7
++++++++++++++++++

* Fix clusterType of Microsoft.ResourceConnector resource

0.1PP.8
++++++++++++++++++

* Update clusterType validation to allow 'appliances'
* Update identity creation to use the appropriate parent resource's type and api-version
* Throw error if cluster type is not one of the 3 supported types

0.1PP.9
++++++++++++++++++

* Rename azuremonitor-containers extension type to microsoft.azuremonitor.containers

0.1PP.10
++++++++++++++++++

* Add azuremonitor-containers back with alternative microsoft.azuremonitor.containers

0.1PP.11
++++++++++++++++++

* Add shorter aliases for long parameter names

0.1PP.12
++++++++++++++++++

* Remove support for azuremonitor-containers extension type naming

0.1PP.13
++++++++++++++++++

* Move CLI errors to non-deprecated error types
* Remove support for update

0.1PP.14
++++++++++++++++++

* Update help text, group CLI arguments
