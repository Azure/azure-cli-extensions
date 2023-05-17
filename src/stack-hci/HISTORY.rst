.. :changelog:

Release History
===============

0.1.7
++++++
* Upgrade api-version to 2023-03-01
* Migrate azure-stack-hci commands to aaz

0.1.6
++++++
* Upgrade api-version to 2022-05-01
* Add new command `az stack-hci arc-setting update` to support updating arc settings for HCI cluster
* Add new command `az stack-hci arc-setting create-identity` to support creating aad identity for arc settings
* Add new command `az stack-hci arc-setting generate-password` to support generating password for arc settings
* Add new command `az stack-hci cluster create-identity` to support creating cluster identity

0.1.5
++++++
* Support arc setting management
* Support extension management

0.1.4
++++++
* Add missing help message for `az stack-hci`

0.1.3
++++++
* Fix the issue that listing clusters under subscription doesn't work
* Migrate to track 2 SDK

0.1.2
++++++
* GA stack-hci extension

0.1.1
++++++
* Upgrade api-version to 2020-10-01

0.1.0
++++++
* Initial release.
