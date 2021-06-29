.. :changelog:

Release History
===============

0.2.0
+++++
* [BREAKING CHANGE] `az confluent organization create`: Remove `--user-detail`, the parameter is now auto-filled by the email address, first name and last name decoded from access token. 
* [BREAKING CHANGE] `az confluent organization create`: Flatten `--offer-detail` to `--offer-id`, `--plan-id`, `--plan-name`, `--publisher-id` and `--term-unit`.
* Add new command `az confluent offer-detail show`.
* `az confluent organization create`: Add Owner or Contributor access check of the subscription before creating the organization.
* `az confluent organization delete`: Customize confirmation message based on plan type. 

0.1.0
++++++
* Initial release.
