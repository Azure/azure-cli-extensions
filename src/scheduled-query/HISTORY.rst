.. :changelog:

Release History
===============
1.0.0b1
++++++
* Fix update action group failure with empty actions
* Fix action group parameter help message

0.5.3
++++++
* Upgrade antlr to 4.13.1

0.5.2
++++++
* Fix scheduled query condition operator mapping

0.5.1
++++++
* Supress warning message from antlr 4.9.3

0.5.0
++++++
* Update API version to 2021-08-01

0.4.0
++++++
* Add `--skip-query-validation` parameter
* Add `--check-ws-alerts-storage` parameter
* Add `--auto-mitigate` parameter
* [Breaking Change] `--actions` are split into `--action-groups` and `--custom-properties`
* [Breaking Change] the default value of `--mute-actions-duration` is changed to None

0.3.1
++++++
* Support query placeholder for `--condition` parameter.
* Add `--condition-query` parameter to support query placeholder.

0.2.2
++++++
* Fix parse bug for `--condition` parameter.

0.2.0
++++++
* Adjust pattern for `--condition` parameter.

0.1.0
++++++
* Initial release.
