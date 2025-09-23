.. :changelog:

Release History
===============

1.0.2
+++++
* Set `azext.minCliCoreVersion` to `2.75.0` since it is using DATA_STORAGE_TABLE

1.0.1
+++++
* Remove DATA_COSMOS_TABLE and DATA_STORAGE references

1.0.0
+++++
* Remove msrestazure dependency

0.3.0
+++++
* Add support for setting proxy and debug configuration of the VM Extension for SAP

0.2.2
+++++
* Fix for https://github.com/Azure/azure-cli-extensions/issues/3019
* Switched from VM PUT to VM PATCH REST call when adding a VM identity 
