.. :changelog:

Release History
===============
0.3.0
++++++
* Removing preview flag.
* Fix for AAD login.

0.2.7
++++++
* add support for auth type password in RDP connection
* line formatting issue with IP connect

0.2.6
++++++
* Adding auth type aad for RDP to mimic the enable-mfa flag.
* Fixing issue where if powershell is opened in system32 directory, file generation throws error. Files are now dumped in temp folder.

0.2.5
++++++
* Fixing the command `az network bastion rdp` to avoid the `java.lang.NullPointerException` while calling `get_auth_token` function

0.2.4
++++++
* Fixing blocking of IP connect with AZ CLI tunnel to allow only standard ports.
* documentation update
* security fixes

0.2.3
++++++
* Fixes for IP address connect

0.2.2
++++++
* Bug fixes
* Fixes for IP address connect

0.2.1
++++++
* Bug fixes.

0.2.0
++++++
* Adding support for IP connect through AZ CLI.
* Initial support for connectivity through developerSku.
* Bug fixes.

0.1.0
++++++
* Initial release.
