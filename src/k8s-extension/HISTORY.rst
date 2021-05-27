.. :changelog:

Release History
===============

0.4.2
++++++++++++++++++

* Change resource tag from 'amlk8s' to 'Azure Arc-enabled ML' in microsoft.azureml.kubernetes

0.4.1
++++++++++++++++++

* Add compatible logic for the track 2 migration of resource dependence

0.4.0
++++++++++++++++++

* Release customization for microsoft.openservicemesh

0.3.1
++++++++++++++++++

* Add provider registration to check to validations
* Only validate scoring fe settings when inference is enabled in microsoft.azureml.kubernetes

0.3.0
++++++++++++++++++

* Release customization for microsoft.azureml.kubernetes

0.2.1
++++++++++++++++++

* Remove `k8s-extension update` until PATCH is supported
* Improved logging for overwriting extension name with default 

0.2.0
++++++++++++++++++

* Refactor for clear separation of extension-type specific customizations
* OpenServiceMesh customization.
* Fix clusterType of Microsoft.ResourceConnector resource
* Update clusterType validation to allow 'appliances'
* Update identity creation to use the appropriate parent resource's type and api-version
* Throw error if cluster type is not one of the 3 supported types
* Rename azuremonitor-containers extension type to microsoft.azuremonitor.containers
* Move CLI errors to non-deprecated error types
* Remove support for update

0.1.3
++++++++++++++++++

* Customization for microsoft.openservicemesh

0.1.2
++++++++++++++++++

* Add support for Arc Appliance cluster type

0.1.1
++++++++++++++++++
* Add support for microsoft-azure-defender extension type

0.1.0
++++++++++++++++++
* Initial release.
