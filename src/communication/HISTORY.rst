.. :changelog:

Release History
===============
1.9.1
++++++
* Add Email communication Domain resource Initiate and Cancel verification operations

1.9.0
++++++
* Adding managed identity support for stable api version 2023-04-01

1.8.0b2
++++++
* Add Email communication resource CRUD operations
* Add Domain resource CRUD operations
* Add Sender username CRUD operations

1.8.0b1
++++++
* Update ACS Rooms to use 1.1.0b1 version

1.7.2b1
++++++
* Update Email to the latest 1.0.0 version


1.7.2
++++++
* Add additional test cases for ACS Rooms


1.7.1b1
++++++
* Adding managed identity support


1.7.0b1
++++++
* Migrate control plane operations to aaz
* Upgrade control plane api version to 2023-04-01-preview


1.6.1
++++++
 * Update Rooms sdk version to 1.0.0 and remove from preview mode


1.6.0
++++++
 * Update Rooms sdk version to 1.0.0b3


1.5.2
++++++
 * Email service sdk version set to 1.0.0b1 to satisfy the current contract


1.5.1
++++++
 * Add AzureCli to the user-agent header for Rooms and Email service clients
 

1.5.0
++++++
 * Add communication email command group in preview mode


1.4.1
++++++
 * Update version missed in previous release
 * Remove redundant version definition in setup.py
 

1.4.0
++++++
 * Add communication rooms command group in preview mode
 * Add confirmation for delete/remote/revoke commands under identity, chat, rooms
 * Update minCliCoreVersion to 2.40.0


1.3.0
++++++
 * Add AzureCli to the user-agent header


1.2.2
++++++
 * Fix a bug in chat 'message delete command'


1.2.1
++++++
 * Update command helps
 * Fix bugs in preview and deprecated flags


1.2.0
++++++
* Add communication chat command group in preview mode.
* Add communication identity command group in preview mode.
* Deprecate 'identity issue-access-token' for 'identity token issue'
* Deprecate 'sms sens-sms' for 'sms send'
* Deprecate 'phonenumbers show-phonenumber' for 'phonenumber show'
* Deprecate 'phonenumbers list-phonenumbers' for 'phonenumber list'


1.1.2
++++++
* Add support for multiple SMS recipients.


1.1.1
++++++
* Fix codestyle issues in communiction command group.


1.1.0
++++++
* Add communication identity command group.
* Add communication sms command group.
* Add communication phonenumbers command group.


1.0.0
++++++
* GA release.

'az communication show-status' has been removed


0.1.0
++++++
* Initial release.
