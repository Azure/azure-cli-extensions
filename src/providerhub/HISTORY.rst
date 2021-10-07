.. :changelog:

Release History
===============

0.2.0
++++++
* Support commands for
    `az providerhub notification-registration`
    `az providerhub operation`
    `az providerhub sku`
* Enable creation of nested resource types and adding extension categories.
* Refine and update initial release commands.

* [BREAKING CHANGE] `az providerhub default-rollout create`:
    `--row2-wait-duration` moved to `--row2 wait-duration`
    `--skip-regions` moved to `--canary skip-regions`
* [BREAKING CHANGE]: `--provider-type` type changed from enum to string.
* [BREAKING CHANGE]: `--routing-type` type changed from enum to string.

0.1.0
++++++
* Initial release.
