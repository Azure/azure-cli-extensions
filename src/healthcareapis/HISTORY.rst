.. :changelog:

Release History
===============

0.4.0
++++++

* `az healthcareapis service` Add new argument `--login-servers` to support adding login servers to the service instance.
* `az healthcareapis service` Add new argument `--oci-artifacts` to support specifying open container initiative artifacts.
* `az healthcareapis private-endpoint-connection` Will deprecate argument `--private-link-service-connection-state-actions-required`
* `az healthcareapis private-endpoint-connection` Will deprecate argument `--private-link-service-connection-state-description`
* `az healthcareapis private-endpoint-connection` Will deprecate argument `--private-link-service-connection-state-status`
* `az healthcareapis private-endpoint-connection` Add new argument `--private-link-service-connection-state` to support specifying information about the state of the connection between service consumer and provider.
* Add new subgroups `az healthcareapis workspace` to Manage workspace with healthcareapis.
* Add new subgroups `az healthcareapis workspace dicom-service` to Manage dicom service with healthcareapis.
* Add new subgroups `az healthcareapis workspace fhir-service` to Manage fhir service with healthcareapis.
* Add new subgroups `az healthcareapis workspace iot-connector` to Manage iot connector with healthcareapis.
* Add new subgroups `az healthcareapis workspace iot-connector fhir-destination` to Manage iot connector fhir destination with healthcareapis.
* Add new subgroups `az healthcareapis workspace private-endpoint-connection` to Manage workspace private endpoint connection with healthcareapis.
* Add new subgroups `az healthcareapis workspace private-link-resource` to Manage workspace private link resource with healthcareapis.

0.3.3
++++++

* Fixed bugs

0.3.2
++++++

* Fixed bugs

0.3.1
++++++

* Added support for AcrConfiguration
* Upgraded API version to latest stable
* Fixed bugs

0.3.0
++++++

* Added support for private link
* Added support for customer managed key

0.2.0
+++++

* Added support for managed identity and setting the export storage account

0.1.3
+++++

* Removed the limitation of max compatible cli core version

0.1.2
+++++

* Upgraded API version to latest stable
* Removed preview tag

0.1.1
+++++

* Updated examples
* Fixed bugs

0.1.0
++++++

* Initial release.
