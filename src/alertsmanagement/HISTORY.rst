.. :changelog:

Release History
===============

0.2.3
++++++
* az alerts-management prometheus-rule-group: support prometheus rule group

0.2.2
++++++
Added support for contains and doesNotContain operators for filter-resource-type in create method

0.2.1
++++++
Fixed help file text and an error loading the help files of all methods

0.2.0
++++++
This version supports the new alert processing rule API (changed from action rule) and is breaking  old versions.
It is recommended to replace all old versions to use this version of the CLI.
new API for alert processing rule can be found here: https://docs.microsoft.com/en-us/rest/api/monitor/alertsmanagement/alert-processing-rules
new documentation for alert processing rules can be found here: https://docs.microsoft.com/en-us/rest/api/monitor/alertsmanagement/alert-processing-rules

0.1.1
++++++
* Add an example were the recurrence type is set to once.
* Fix error: when the recurrence type is set to once, 'Action Rule property 'properties.suppressionConfig.schedule' cannot be null.'

0.1.0
++++++
* Initial release.
