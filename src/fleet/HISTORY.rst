.. :changelog:

Release History
===============

0.1.0
++++++
* Initial release.

0.1.1
++++++
* Upgrade SDK version to 2022-07-02-preview
* Bug fixes

0.2.0
++++++
* Use new SDK

0.2.1
++++++
* Update fleet member commands

0.2.2
++++++
* Add fleet multi-cluster update commands

0.2.3
++++++
* Upgrade SDK version to 2023-06-15-preview

0.2.4
++++++
* Added support for private fleet & MSI.

0.2.5
++++++
* Upgrade SDK version to 2023-08-15-preview

0.2.6
++++++
* By default, fleets are now created without a hub
* Added support for Fleet Upgrade Strategy
* Added argument for Node Image Selection.

0.2.7
++++++
* Fix for `az fleet updaterun --node-image-selection` argument.

0.2.8
++++++
* Updates to Fleet identity options.

0.3.0
++++++
* Resolved issues related to system & user assigned MSI.
* UpdateRun now takes a Strategy name in lieu of resource Id, e.g., `az fleet updaterun create --update_strategy_name UpdateStrategyName`
* Deletes now require confirmation.

1.0.0
++++++
* Promoted extension to GA.
* Added `az fleet create` preview parameter `vm-size` for Hubful fleets.

1.0.1
++++++
* Updated help examples.
* Fixed serialization bug.

1.0.2
++++++
* Minor style & linting updates to codebase.