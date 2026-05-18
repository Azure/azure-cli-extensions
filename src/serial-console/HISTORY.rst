Release History
===============
1.0.0b4
+++++++
* Fixed garbled console output where binary websocket frames were printed as a Python bytes repr (``b'...\r\n\x1b[...]'``) instead of decoded text. Decode bytes to str in ``on_message`` so ANSI escapes and CR/LF are interpreted by the user's terminal.
* Bumped ``websocket-client`` dependency from ``==1.3.1`` to ``~=1.8.0`` to align with the version required by ``azure-cli`` and avoid a ``pkg_resources.ContextualVersionConflict`` at install time.

1.0.0b3
++++++
* Fixed an issue where admin commands were not being sent when the VM was using a custom boot diagnostics storage account.

1.0.0b2
++++++
* Changed to 2024 API version, fixes Disable API to track "properties". Essentially return to 2018 format

1.0.0b1
++++++
* Migrated to a new authentication flow to enhance overall security

0.1.8
++++++
* Changed first message flow, fixed typo

0.1.7
++++++
* Preparation for the new websocket authentication mechanism

0.1.6
++++++
* Fix pair region mapping for eastus to westus

0.1.5
++++++
* Fix resource group for custom storage account

0.1.4
++++++
* Fix repeating loading message
* Bump websocket-client version

0.1.3
++++++
* Change to use different region for url calls when custom storage account firewalls are enabled

0.1.2
++++++
* Change to make custom boot diagnostics optional

0.1.1
++++++
* Change to require custom boot diagnostics

0.1.0
++++++
* Initial release.
