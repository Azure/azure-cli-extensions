.. :changelog:

Release History
===============

1.0.0b5
+++++
* Add: Support yaml file for `az apic api register` command
* Update: Update some command names, parameter names as well as related descriptions for better understanding. Please leverage `-h` option or refer Azure CLI reference doc to see full list of commands and parameters.
* Update: Some parameters now have constraints to ensure valid values are provided.
* Update: 
* Update: Minimum Azure CLI version requirement is updated to 2.57.
* Fix: Various bug fixes for last preview version.
* Remove: All portal commands as it should not be exposed to customers.
* Remove: `--workspace-name` and `--terms-of-service` parameters are removed as they are not expected to be exposed.
* Remove: `head` commands in each command group are removed.

1.0.0b4
+++++
* Add: Support for Default Portal configuration and default hostname provisoning deprovisioning commands

1.0.0b3
+++++
* Add: Support for Import from apim command along with add examples for create service

1.0.0b2
++++++
* Remove: All workspace cli commands as it should not be exposed to customers just yet.

1.0.0b1
++++++
* Initial release.