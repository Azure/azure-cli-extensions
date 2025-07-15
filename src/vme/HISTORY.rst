.. :changelog:

Release History
===============

1.0.0b1
++++++
* Initial release.

1.0.0b2
++++++
* Add new 'az vme list' command to list all version managed extensions.

1.0.0b3
++++++
* Update 'az vme list --output table' to show correct versions.
* Wait for the bundle feature flag to fully propagate after enabling it.

1.0.0b4
++++++
* Add '--force' to 'az vme uninstall' to force delete extension.

1.0.0b5
++++++
* Skip running animation if stdout is not a TTY.
